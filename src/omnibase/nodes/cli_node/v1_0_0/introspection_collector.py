# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: introspection_collector.py
# version: 1.0.0
# uuid: 8f9e1a2b-3c4d-5e6f-7890-1a2b3c4d5e6f
# author: OmniNode Team
# created_at: 2025-05-27T19:30:00
# last_modified_at: 2025-05-27T19:38:03.414407
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 6306f91df0d7a7b26ac8b3798dd81f69bb4fba978ccfca6ba447c003ea0dab4a
# entrypoint: python@introspection_collector.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.introspection_collector
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Event-Driven Introspection Collector.

This module provides asynchronous introspection collection using the event bus.
Instead of sequentially calling each node, it broadcasts an introspection request
and collects responses asynchronously for better performance and scalability.
"""

import asyncio
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class IntrospectionCollector:
    """
    Event-driven introspection collector.

    Broadcasts introspection requests and collects responses asynchronously
    for improved performance and scalability.
    """

    def __init__(
        self,
        event_bus: ProtocolEventBus,
        timeout_ms: int = 5000,
        node_id: str = "cli_node",
    ):
        """
        Initialize the introspection collector.

        Args:
            event_bus: Event bus for communication
            timeout_ms: Timeout for collecting responses in milliseconds
            node_id: ID of the requesting node
        """
        self.event_bus = event_bus
        self.timeout_ms = timeout_ms
        self.node_id = node_id
        self.responses: Dict[str, Dict[str, Any]] = {}
        self.correlation_id: Optional[str] = None
        self.start_time: Optional[float] = None

    def _handle_introspection_response(self, event: OnexEvent) -> None:
        """Handle introspection response events."""
        if (
            event.event_type == OnexEventTypeEnum.INTROSPECTION_RESPONSE
            and event.correlation_id == self.correlation_id
        ):

            node_id = str(event.node_id)
            introspection_data = (
                event.metadata.get("introspection", {}) if event.metadata else {}
            )

            self.responses[node_id] = {
                "introspection": introspection_data,
                "response_time_ms": (
                    (time.time() - self.start_time) * 1000 if self.start_time else 0
                ),
                "timestamp": event.timestamp,
                "event_id": str(event.event_id),
            }

            emit_log_event(
                LogLevelEnum.DEBUG,
                f"Received introspection response from {node_id}",
                node_id=self.node_id,
                context={
                    "responding_node": node_id,
                    "correlation_id": self.correlation_id,
                },
            )

    def _handle_node_discovery_response(self, event: OnexEvent) -> None:
        """Handle node discovery response events."""
        if (
            event.event_type == OnexEventTypeEnum.NODE_DISCOVERY_RESPONSE
            and event.correlation_id == self.correlation_id
        ):

            node_id = str(event.node_id)
            node_info = event.metadata.get("node_info", {}) if event.metadata else {}

            # Store basic node info for discovery
            if node_id not in self.responses:
                self.responses[node_id] = {}

            self.responses[node_id]["node_info"] = node_info
            self.responses[node_id]["discovered_at"] = time.time()

            emit_log_event(
                LogLevelEnum.DEBUG,
                f"Discovered node {node_id}",
                node_id=self.node_id,
                context={
                    "discovered_node": node_id,
                    "correlation_id": self.correlation_id,
                },
            )

    async def collect_introspections(
        self,
        introspection_types: Optional[List[str]] = None,
        node_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Collect introspection data from all nodes asynchronously.

        Args:
            introspection_types: Specific types of introspection to request
            node_filter: Filter pattern for node names

        Returns:
            Dictionary containing introspection data from all responding nodes
        """
        self.correlation_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.responses = {}

        # Subscribe to response events
        self.event_bus.subscribe(self._handle_introspection_response)

        # Prepare request metadata
        request_metadata = {
            "timeout_ms": self.timeout_ms,
            "requested_by": self.node_id,
            "request_timestamp": self.start_time,
        }

        if introspection_types:
            request_metadata["introspection_types"] = introspection_types

        if node_filter:
            request_metadata["node_filter"] = node_filter

        # Broadcast introspection request
        request_event = OnexEvent(
            event_type=OnexEventTypeEnum.INTROSPECTION_REQUEST,
            node_id=self.node_id,
            correlation_id=self.correlation_id,
            metadata=request_metadata,
        )

        emit_log_event(
            LogLevelEnum.INFO,
            f"Broadcasting introspection request with correlation_id {self.correlation_id}",
            node_id=self.node_id,
            context={
                "correlation_id": self.correlation_id,
                "timeout_ms": self.timeout_ms,
            },
        )

        self.event_bus.publish(request_event)

        # Wait for responses with timeout
        await asyncio.sleep(self.timeout_ms / 1000)

        # Unsubscribe from events
        self.event_bus.unsubscribe(self._handle_introspection_response)

        total_time = (time.time() - self.start_time) * 1000

        emit_log_event(
            LogLevelEnum.INFO,
            f"Introspection collection completed: {len(self.responses)} responses in {total_time:.2f}ms",
            node_id=self.node_id,
            context={
                "correlation_id": self.correlation_id,
                "response_count": len(self.responses),
                "total_time_ms": total_time,
            },
        )

        return {
            "correlation_id": self.correlation_id,
            "total_time_ms": total_time,
            "response_count": len(self.responses),
            "timeout_ms": self.timeout_ms,
            "responses": self.responses,
            "request_metadata": request_metadata,
        }

    async def discover_nodes(self) -> Dict[str, Any]:
        """
        Discover all available nodes using event-driven pattern.

        Returns:
            Dictionary containing discovered node information
        """
        self.correlation_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.responses = {}

        # Subscribe to discovery response events
        self.event_bus.subscribe(self._handle_node_discovery_response)

        # Broadcast node discovery request
        discovery_event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_DISCOVERY_REQUEST,
            node_id=self.node_id,
            correlation_id=self.correlation_id,
            metadata={
                "timeout_ms": self.timeout_ms,
                "requested_by": self.node_id,
                "request_timestamp": self.start_time,
            },
        )

        emit_log_event(
            LogLevelEnum.INFO,
            f"Broadcasting node discovery request with correlation_id {self.correlation_id}",
            node_id=self.node_id,
            context={"correlation_id": self.correlation_id},
        )

        self.event_bus.publish(discovery_event)

        # Wait for responses
        await asyncio.sleep(self.timeout_ms / 1000)

        # Unsubscribe from events
        self.event_bus.unsubscribe(self._handle_node_discovery_response)

        total_time = (time.time() - self.start_time) * 1000

        emit_log_event(
            LogLevelEnum.INFO,
            f"Node discovery completed: {len(self.responses)} nodes found in {total_time:.2f}ms",
            node_id=self.node_id,
            context={
                "correlation_id": self.correlation_id,
                "node_count": len(self.responses),
                "total_time_ms": total_time,
            },
        )

        return {
            "correlation_id": self.correlation_id,
            "total_time_ms": total_time,
            "node_count": len(self.responses),
            "timeout_ms": self.timeout_ms,
            "nodes": self.responses,
        }

    def get_response_summary(self) -> Dict[str, Any]:
        """Get summary of collected responses."""
        if not self.responses:
            return {"total_responses": 0}

        response_times = [
            resp.get("response_time_ms", 0)
            for resp in self.responses.values()
            if "response_time_ms" in resp
        ]

        return {
            "total_responses": len(self.responses),
            "responding_nodes": list(self.responses.keys()),
            "avg_response_time_ms": (
                sum(response_times) / len(response_times) if response_times else 0
            ),
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "correlation_id": self.correlation_id,
        }


class StreamingIntrospectionCollector(IntrospectionCollector):
    """
    Streaming version of introspection collector.

    Provides real-time callbacks as responses arrive instead of waiting
    for all responses to complete.
    """

    def __init__(
        self,
        event_bus: ProtocolEventBus,
        timeout_ms: int = 5000,
        node_id: str = "cli_node",
        response_callback: Optional[Callable] = None,
    ):
        """
        Initialize streaming collector.

        Args:
            event_bus: Event bus for communication
            timeout_ms: Timeout for collecting responses
            node_id: ID of the requesting node
            response_callback: Callback function called for each response
        """
        super().__init__(event_bus, timeout_ms, node_id)
        self.response_callback = response_callback

    def _handle_introspection_response(self, event: OnexEvent) -> None:
        """Handle introspection response with streaming callback."""
        super()._handle_introspection_response(event)

        # Call streaming callback if provided
        if self.response_callback and event.correlation_id == self.correlation_id:
            node_id = str(event.node_id)
            if node_id in self.responses:
                self.response_callback(node_id, self.responses[node_id])

    async def stream_introspections(
        self,
        introspection_types: Optional[List[str]] = None,
        node_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Stream introspection data with real-time callbacks.

        Same as collect_introspections but calls response_callback for each response.
        """
        return await self.collect_introspections(introspection_types, node_filter)
