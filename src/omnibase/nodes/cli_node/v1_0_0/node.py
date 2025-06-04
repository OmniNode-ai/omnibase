"""
CLI Node Implementation.

Main node implementation for the CLI node that handles command routing,
node discovery, and execution via event-driven architecture.
"""

import asyncio
import importlib
import json
import sys
import time
from pathlib import Path
from typing import Callable, Dict, Optional

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus

from .introspection import CLINodeIntrospection
from .introspection_collector import IntrospectionCollector
from .models.state import (
    CLIInputState,
    CLIOutputState,
    NodeRegistrationState,
    create_cli_output_state,
)

_COMPONENT_NAME = Path(__file__).stem


class CLINode:
    def __init__(self, event_bus: ProtocolEventBus = None):
        self.event_bus = event_bus or get_event_bus()
        self.event_bus.subscribe(self.handle_event)

    def handle_event(self, event: OnexEvent):
        # Only handle TOOL_PROXY_INVOKE (run node) events
        if event.event_type != OnexEventTypeEnum.TOOL_PROXY_INVOKE:
            return
        # Extract target node and args
        metadata = event.metadata or {}
        target_node = metadata.get("target_node")
        args = metadata.get("args", [])
        log_format = metadata.get("log_format", "json")
        correlation_id = event.correlation_id
        # Publish a new event to the bus addressed to the target node
        node_event = OnexEvent(
            event_id=event.event_id,
            timestamp=event.timestamp,
            node_id=target_node,
            event_type=OnexEventTypeEnum.TOOL_PROXY_INVOKE,
            correlation_id=correlation_id,
            metadata={
                "args": args,
                "log_format": log_format,
            },
        )
        self.event_bus.publish(node_event)


def run_cli_node(
    input_state: CLIInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., CLIOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> CLIOutputState:
    """
    Main node entrypoint for CLI node.

    Args:
        input_state: CLIInputState (must include version)
        event_bus: ProtocolEventBus (optional, defaults to InMemoryEventBus)
        output_state_cls: Optional callable to construct output state (for testing/mocking)
        handler_registry: Optional FileTypeHandlerRegistry (not used by CLI node)

    Returns:
        CLIOutputState (version matches input_state.version)
    """
    if event_bus is None:
        event_bus = get_event_bus(mode="bind")
    cli_node = CLINode(event_bus=event_bus)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, cli_node.execute(input_state))
                return future.result()
        else:
            return loop.run_until_complete(cli_node.execute(input_state))
    except RuntimeError:
        return asyncio.run(cli_node.execute(input_state))


def main() -> None:
    """
    CLI entrypoint for standalone execution.
    """
    event_bus = InMemoryEventBus()
    cli_node = CLINode(event_bus=event_bus)
    # Keep the process alive to handle events
    while True:
        time.sleep(1)


def get_introspection() -> dict:
    """Get introspection data for the CLI node."""
    return CLINodeIntrospection.get_introspection_response().model_dump()


if __name__ == "__main__":
    main()
