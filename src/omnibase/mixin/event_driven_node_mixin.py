# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.577927'
# description: Stamped by PythonHandler
# entrypoint: python://event_driven_node_mixin
# hash: 0c36231651847d2562500ddc88c5bcaaa3c08fc66039c78546680966b5ecf95c
# last_modified_at: '2025-05-29T14:13:58.669179+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: event_driven_node_mixin.py
# namespace: python://omnibase.mixin.event_driven_node_mixin
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: f3b74f65-7847-4d38-a749-280ebb050142
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Event-Driven Node Mixin.

This mixin provides event-driven capabilities for ONEX nodes, including:
- Automatic node registration on the event bus
- Introspection request/response handling
- Node discovery participation
- Event-driven lifecycle management
"""

import fnmatch
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class EventDrivenNodeMixin:
    """
    Canonical mixin for event-driven ONEX nodes.
    Provides:
    - Automatic event bus setup (defaults to InMemoryEventBus)
    - Standard node registration and event handler setup
    - Helper methods for emitting NODE_START, NODE_SUCCESS, NODE_FAILURE events
    - All communication via event bus; no direct side effects
    """

    def __init__(
        self, node_id: str, event_bus: Optional[ProtocolEventBus] = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.node_id = node_id
        self.event_bus = event_bus or InMemoryEventBus()
        self._setup_event_handlers()
        self._register_node()

    def _setup_event_handlers(self) -> None:
        """Set up event handlers for this node."""
        if not self.event_bus:
            return

        # Subscribe to introspection requests
        self.event_bus.subscribe(self._handle_introspection_request)

        # Subscribe to node discovery requests
        self.event_bus.subscribe(self._handle_node_discovery_request)

        emit_log_event(
            LogLevelEnum.DEBUG,
            f"Event handlers set up for node {self.node_id}",
            node_id=self.node_id,
        )

    def _register_node(self) -> None:
        """Register this node on the event bus."""
        if not self.event_bus:
            return

        registration_event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_REGISTER,
            node_id=self.node_id,
            metadata={
                "node_name": getattr(self, "get_node_name", lambda: self.node_id)(),
                "node_version": getattr(self, "get_node_version", lambda: "unknown")(),
                "capabilities": getattr(self, "get_capabilities", lambda: [])(),
                "introspection_available": getattr(
                    self, "supports_introspection", lambda: False
                )(),
                "registration_timestamp": time.time(),
            },
        )

        self.event_bus.publish(registration_event)

        emit_log_event(
            LogLevelEnum.INFO,
            f"Node {self.node_id} registered on event bus",
            node_id=self.node_id,
        )

    def _handle_introspection_request(self, event: OnexEvent) -> None:
        """Handle introspection request events."""
        if event.event_type != OnexEventTypeEnum.INTROSPECTION_REQUEST:
            return

        # Check if this request applies to us
        if not self._should_respond_to_request(event):
            return

        try:
            # Get introspection data
            introspection_data = self.get_introspection_data()

            # Filter introspection types if requested
            if event.metadata and "introspection_types" in event.metadata:
                requested_types = event.metadata["introspection_types"]
                introspection_data = self._filter_introspection_data(
                    introspection_data, requested_types
                )

            # Send response
            response_event = OnexEvent(
                event_type=OnexEventTypeEnum.INTROSPECTION_RESPONSE,
                node_id=self.node_id,
                correlation_id=event.correlation_id,
                metadata={
                    "introspection": introspection_data,
                    "response_timestamp": time.time(),
                    "request_event_id": str(event.event_id),
                },
            )

            if self.event_bus:
                self.event_bus.publish(response_event)

            emit_log_event(
                LogLevelEnum.DEBUG,
                f"Sent introspection response for correlation_id {event.correlation_id}",
                node_id=self.node_id,
                context={"correlation_id": event.correlation_id},
            )

        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Failed to handle introspection request: {e}",
                node_id=self.node_id,
                context={"correlation_id": event.correlation_id, "error": str(e)},
            )

    def _handle_node_discovery_request(self, event: OnexEvent) -> None:
        """Handle node discovery request events."""
        if event.event_type != OnexEventTypeEnum.NODE_DISCOVERY_REQUEST:
            return

        # Check if this request applies to us
        if not self._should_respond_to_request(event):
            return

        try:
            # Get basic node info
            node_info = {
                "node_name": self.get_node_name(),
                "node_version": self.get_node_version(),
                "capabilities": self.get_capabilities(),
                "introspection_available": self.supports_introspection(),
                "status": "active",
                "discovery_timestamp": time.time(),
            }

            # Send discovery response
            response_event = OnexEvent(
                event_type=OnexEventTypeEnum.NODE_DISCOVERY_RESPONSE,
                node_id=self.node_id,
                correlation_id=event.correlation_id,
                metadata={
                    "node_info": node_info,
                    "response_timestamp": time.time(),
                    "request_event_id": str(event.event_id),
                },
            )

            if self.event_bus:
                self.event_bus.publish(response_event)

            emit_log_event(
                LogLevelEnum.DEBUG,
                f"Sent discovery response for correlation_id {event.correlation_id}",
                node_id=self.node_id,
                context={"correlation_id": event.correlation_id},
            )

        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Failed to handle discovery request: {e}",
                node_id=self.node_id,
                context={"correlation_id": event.correlation_id, "error": str(e)},
            )

    def _should_respond_to_request(self, event: OnexEvent) -> bool:
        """Check if this node should respond to a request event."""
        if not event.metadata:
            return True

        # Check node filter if present
        node_filter = event.metadata.get("node_filter")
        if node_filter:
            node_name = self.get_node_name()
            if not fnmatch.fnmatch(node_name, node_filter):
                return False

        # Check if request is from ourselves (avoid self-response)
        if event.node_id == self.node_id:
            return False

        return True

    def _filter_introspection_data(
        self, introspection_data: Dict[str, Any], requested_types: List[str]
    ) -> Dict[str, Any]:
        """Filter introspection data to only include requested types."""
        if not requested_types:
            return introspection_data

        filtered_data = {}

        for requested_type in requested_types:
            if requested_type in introspection_data:
                filtered_data[requested_type] = introspection_data[requested_type]

        return filtered_data

    # Abstract methods that implementing classes should provide
    def get_node_id(self) -> str:
        """Get the unique identifier for this node."""
        return self.node_id

    def get_node_name(self) -> str:
        """Get the name of this node."""
        return getattr(self, "node_name", self.__class__.__name__)

    def get_node_version(self) -> str:
        """Get the version of this node."""
        return getattr(self, "node_version", "1.0.0")

    def get_capabilities(self) -> List[str]:
        """Get the capabilities of this node."""
        return getattr(self, "capabilities", ["event_driven"])

    def supports_introspection(self) -> bool:
        """Check if this node supports introspection."""
        return hasattr(self, "get_introspection_data") or hasattr(
            self, "get_introspection"
        )

    def get_introspection_data(self) -> Dict[str, Any]:
        """Get introspection data for this node."""
        # Try to use existing introspection methods
        if hasattr(self, "get_introspection"):
            result = self.get_introspection()
            return result if isinstance(result, dict) else {}

        # Fallback to basic introspection
        return {
            "node_metadata": {
                "name": self.get_node_name(),
                "version": self.get_node_version(),
                "capabilities": self.get_capabilities(),
                "supports_introspection": self.supports_introspection(),
            },
            "event_driven": True,
            "introspection_timestamp": time.time(),
        }

    def cleanup_event_handlers(self) -> None:
        """Clean up event handlers when node is shutting down."""
        if not self.event_bus:
            return

        try:
            self.event_bus.unsubscribe(self._handle_introspection_request)
            self.event_bus.unsubscribe(self._handle_node_discovery_request)

            emit_log_event(
                LogLevelEnum.DEBUG,
                f"Event handlers cleaned up for node {self.node_id}",
                node_id=self.node_id,
            )
        except Exception as e:
            emit_log_event(
                LogLevelEnum.WARNING,
                f"Failed to clean up event handlers: {e}",
                node_id=self.node_id,
                context={"error": str(e)},
            )

    def emit_node_start(
        self, metadata: Optional[dict] = None, correlation_id: Optional[str] = None
    ) -> None:
        self.event_bus.publish(
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_START,
                node_id=self.node_id,
                correlation_id=correlation_id,
                metadata=metadata or {},
            )
        )

    def emit_node_success(
        self, metadata: Optional[dict] = None, correlation_id: Optional[str] = None
    ) -> None:
        self.event_bus.publish(
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_SUCCESS,
                node_id=self.node_id,
                correlation_id=correlation_id,
                metadata=metadata or {},
            )
        )

    def emit_node_failure(
        self, metadata: Optional[dict] = None, correlation_id: Optional[str] = None
    ) -> None:
        self.event_bus.publish(
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_FAILURE,
                node_id=self.node_id,
                correlation_id=correlation_id,
                metadata=metadata or {},
            )
        )


class EventDrivenNodeProtocol:
    """
    Protocol defining the interface for event-driven nodes.

    This protocol can be used for type checking and documentation
    of the expected interface for event-driven nodes.
    """

    def get_node_id(self) -> str:
        """Get the unique identifier for this node."""
        raise NotImplementedError

    def get_node_name(self) -> str:
        """Get the name of this node."""
        raise NotImplementedError

    def get_node_version(self) -> str:
        """Get the version of this node."""
        raise NotImplementedError

    def get_capabilities(self) -> List[str]:
        """Get the capabilities of this node."""
        raise NotImplementedError

    def supports_introspection(self) -> bool:
        """Check if this node supports introspection."""
        raise NotImplementedError

    def get_introspection_data(self) -> Dict[str, Any]:
        """Get introspection data for this node."""
        raise NotImplementedError
