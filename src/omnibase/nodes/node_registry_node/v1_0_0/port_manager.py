from datetime import datetime, timedelta
from typing import Dict, Optional
from uuid import UUID, uuid4

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.model.model_onex_event import (
    OnexEvent,
    OnexEventMetadataModel,
    OnexEventTypeEnum,
)
from omnibase.nodes.node_registry_node.v1_0_0.models.port_usage import (
    PortUsageEntry,
    PortUsageMap,
)
from omnibase.nodes.node_registry_node.v1_0_0.models.state import (
    PortLeaseModel,
    PortRequestModel,
    RegistryEventBusState,
    RegistryPortState,
)
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
import portpicker
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum


class PortManager:
    """
    Handles dynamic event bus port allocation, lease tracking, and introspection for the registry node.
    Tracks explicit port-to-node usage via PortUsageMap for fast lookup and collision avoidance.
    All port allocation and release actions emit protocol-pure log/telemetry events.
    """

    def __init__(self, event_bus: ProtocolEventBus = None):
        self.port_state = RegistryPortState()
        self.event_bus_state = RegistryEventBusState()
        self.port_usage_map = PortUsageMap()
        self.event_bus = event_bus  # Injected for event emission
        # TODO: Initialize any additional state as needed

    def request_port(self, request: PortRequestModel) -> PortLeaseModel:
        """
        Allocate a port for the requester, ensuring no collision and updating registry state.
        Emits a structured log/telemetry event for allocation.
        """
        now = datetime.utcnow()
        # Clean up expired leases
        expired_ports = []
        for port, entry in self.port_usage_map.ports.items():
            if entry.expires_at:
                expires_at_dt = datetime.fromisoformat(entry.expires_at)
                if expires_at_dt < now:
                    expired_ports.append(port)
        for port in expired_ports:
            del self.port_usage_map.ports[port]
        # Find available port
        used_ports = set(self.port_usage_map.ports.keys())
        port = None
        if request.preferred_port:
            if request.preferred_port in used_ports:
                raise OnexError(
                    f"Port {request.preferred_port} is already in use",
                    CoreErrorCode.RESOURCE_EXHAUSTED,
                )
            # portpicker can check if port is available
            if not portpicker.is_port_free(request.preferred_port):
                raise OnexError(
                    f"Preferred port {request.preferred_port} is not available (in use by system)",
                    CoreErrorCode.RESOURCE_EXHAUSTED,
                )
            port = request.preferred_port
        else:
            # Use portpicker to pick an unused port
            port = portpicker.pick_unused_port()
            if port is None:
                raise OnexError("No available ports (portpicker returned None)", CoreErrorCode.RESOURCE_EXHAUSTED)
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[PORTMANAGER] Allocated port {port} for node {request.requester_id} (protocol={request.protocol}) via portpicker.",
            event_bus=self.event_bus,
        )
        # Allocate lease
        lease_id = str(uuid4())
        expires_at = (now + timedelta(seconds=request.ttl or 60)).isoformat()
        lease = PortLeaseModel(
            port=port,
            protocol=request.protocol,
            lease_id=lease_id,
            expires_at=expires_at,
            status="active",
            assigned_to=str(request.requester_id),
            requested_at=now.isoformat(),
        )
        self.port_state.ports[lease_id] = lease
        usage_entry = PortUsageEntry(
            port=port,
            node_id=request.requester_id,
            lease_id=lease_id,
            protocol=request.protocol,
            status="active",
            expires_at=expires_at,
        )
        self.port_usage_map.ports[port] = usage_entry
        self.emit_port_allocation_event(lease)
        return lease

    def release_port(self, lease_id: str) -> bool:
        """
        Release a port lease by lease_id. Emits a structured log/telemetry event for release.
        """
        lease = self.port_state.ports.get(lease_id)
        if not lease:
            return False
        port = lease.port
        if port in self.port_usage_map.ports:
            del self.port_usage_map.ports[port]
        del self.port_state.ports[lease_id]
        self.emit_port_release_event(lease_id)
        return True

    def get_active_leases(self) -> Dict[str, PortLeaseModel]:
        """
        Return all active port leases keyed by lease_id.
        """
        return self.port_state.ports

    def introspect_ports(self) -> RegistryPortState:
        """
        Return the current port registry state for introspection.
        """
        return self.port_state

    def introspect_event_buses(self) -> RegistryEventBusState:
        """
        Return the current event bus registry state for introspection.
        """
        return self.event_bus_state

    def introspect_port_usage(self) -> PortUsageMap:
        """
        Return the current port usage map for introspection.
        """
        return self.port_usage_map

    # --- Logging/Telemetry (stubs) ---
    def emit_port_allocation_event(self, lease: PortLeaseModel):
        """
        Emit a protocol-pure log/telemetry event for port allocation.
        """
        if self.event_bus is None:
            return
        event = OnexEvent(
            node_id=lease.assigned_to,
            event_type=OnexEventTypeEnum.STRUCTURED_LOG,  # Or define PORT_ALLOCATED in future
            metadata=OnexEventMetadataModel(
                input_state={"lease": lease.model_dump()},
                status="allocated",
                result_summary=f"Port {lease.port} allocated to {lease.assigned_to}",
            ),
        )
        self.event_bus.publish(event)

    def emit_port_release_event(self, lease_id: str):
        """
        Emit a protocol-pure log/telemetry event for port release.
        """
        if self.event_bus is None:
            return
        event = OnexEvent(
            node_id=lease_id,
            event_type=OnexEventTypeEnum.STRUCTURED_LOG,  # Or define PORT_RELEASED in future
            metadata=OnexEventMetadataModel(
                status="released",
                result_summary=f"Port lease {lease_id} released",
            ),
        )
        self.event_bus.publish(event)
