# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: node.py
# version: 1.0.0
# uuid: 2df37627-d790-48bb-aabb-099b07e367f2
# author: OmniNode Team
# created_at: 2025-05-22T12:17:04.399436
# last_modified_at: 2025-05-22T20:50:39.717456
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 1789dd9797b246cf0958c85db3e9e7aa3309855477aa6bf8e64603a52fd411f4
# entrypoint: python@node.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.node
# meta_type: tool
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Callable, Optional

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum
from omnibase.fixtures.mocks.dummy_schema_loader import DummySchemaLoader
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.protocol.protocol_file_io import ProtocolFileIO
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import (
    get_correlation_id_from_state,
    telemetry,
)
from omnibase.utils.real_file_io import RealFileIO

from .helpers.stamper_engine import StamperEngine
from .introspection import StamperNodeIntrospection
from .models.state import (
    StamperInputState,
    StamperOutputState,
    create_stamper_input_state,
    create_stamper_output_state,
)

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


@telemetry(node_name="stamper_node", operation="stamp_file")
def run_stamper_node(
    input_state: StamperInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., StamperOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
    correlation_id: Optional[str] = None,
    file_io: Optional[ProtocolFileIO] = None,
) -> StamperOutputState:
    """
    Canonical ONEX node entrypoint for stamping metadata blocks into files.
    Emits NODE_START, NODE_SUCCESS, NODE_FAILURE events.

    Args:
        input_state: StamperInputState (must include version)
        event_bus: ProtocolEventBus (optional, defaults to InMemoryEventBus)
        output_state_cls: Optional callable to construct output state (for testing/mocking)
        handler_registry: Optional FileTypeHandlerRegistry for custom handlers
        correlation_id: Optional correlation ID for telemetry
        file_io: Optional ProtocolFileIO for custom file I/O

    Returns:
        StamperOutputState (version matches input_state.version)

    Example of node-local handler registration:
        registry = FileTypeHandlerRegistry()
        registry.register_handler(".custom", MyCustomHandler(), source="node-local")
        output = run_stamper_node(input_state, handler_registry=registry)
    """
    if event_bus is None:
        event_bus = InMemoryEventBus()
    if output_state_cls is None:
        output_state_cls = StamperOutputState

    # Extract or generate correlation ID
    final_correlation_id = correlation_id or get_correlation_id_from_state(input_state)

    # Add correlation ID to input state if not present
    if final_correlation_id and not input_state.correlation_id:
        input_state.correlation_id = final_correlation_id

    node_id = "stamper_node"
    event_bus.publish(
        OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id=node_id,
            correlation_id=final_correlation_id,
            metadata={"input_state": input_state.model_dump()},
        )
    )
    try:
        # Instantiate the canonical engine with optional custom handler registry
        engine = StamperEngine(
            schema_loader=DummySchemaLoader(),
            handler_registry=handler_registry,  # Pass custom registry if provided
            file_io=file_io,  # Pass custom file I/O if provided
        )  # TODO: Inject real schema_loader if needed

        # Example: Register node-local handlers if registry is provided
        # This demonstrates the plugin/override API for node-local handler extensions
        if handler_registry:
            emit_log_event(
                LogLevelEnum.DEBUG,
                "Using custom handler registry with node-local extensions",
                node_id=_COMPONENT_NAME,
            )
            # Node could register custom handlers here:
            # handler_registry.register_handler(".custom", MyCustomHandler(), source="node-local")

        # Call the real stamping logic
        result = engine.stamp_file(
            Path(input_state.file_path),
            author=input_state.author,
            discover_functions=input_state.discover_functions,
        )

        # Use factory function to create output state with proper version propagation
        status = (
            result.status.value
            if hasattr(result.status, "value")
            else str(result.status)
        )
        message = str(
            result.messages[0].summary
            if result.messages
            else (result.metadata.get("note") if result.metadata else "No message")
        )

        # Use output_state_cls if provided (for testing), otherwise use factory function
        if output_state_cls != StamperOutputState:
            # Custom output state class provided (likely for testing)
            output = output_state_cls(
                version=input_state.version,
                status=status,
                message=message,
                correlation_id=final_correlation_id,
            )
        else:
            # Use factory function for default case
            output = create_stamper_output_state(
                status=status,
                message=message,
                input_state=input_state,
                correlation_id=final_correlation_id,
            )

        event_bus.publish(
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_SUCCESS,
                node_id=node_id,
                correlation_id=final_correlation_id,
                metadata={
                    "input_state": input_state.model_dump(),
                    "output_state": output.model_dump(),
                },
            )
        )
        return output
    except Exception as exc:
        # Create error output state using factory function for error events
        error_output = create_stamper_output_state(
            status="failure",
            message=f"Stamping failed: {str(exc)}",
            input_state=input_state,
            correlation_id=final_correlation_id,
        )

        event_bus.publish(
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_FAILURE,
                node_id=node_id,
                correlation_id=final_correlation_id,
                metadata={
                    "input_state": input_state.model_dump(),
                    "output_state": error_output.model_dump(),
                    "error": str(exc),
                },
            )
        )
        raise


def main() -> None:
    """CLI entrypoint for standalone execution."""
    import argparse
    import uuid

    parser = argparse.ArgumentParser(description="ONEX Stamper Node CLI")
    parser.add_argument("file_path", type=str, nargs="?", help="Path to file to stamp")
    parser.add_argument(
        "--author", type=str, default="OmniNode Team", help="Author name"
    )
    parser.add_argument(
        "--correlation-id", type=str, help="Correlation ID for request tracking"
    )
    parser.add_argument(
        "--introspect", action="store_true", help="Enable introspection"
    )
    parser.add_argument(
        "--discover-functions",
        action="store_true",
        help="Discover and include function tools in metadata (unified tools approach)",
    )
    args = parser.parse_args()

    # Handle introspection command
    if args.introspect:
        StamperNodeIntrospection.handle_introspect_command()
        return

    # Validate required arguments for normal operation
    if not args.file_path:
        parser.error("file_path is required when not using --introspect")

    # Generate correlation ID if not provided
    correlation_id = args.correlation_id or str(uuid.uuid4())

    # Use factory function to create input state with proper version handling
    input_state = create_stamper_input_state(
        file_path=args.file_path,
        author=args.author,
        correlation_id=correlation_id,
        discover_functions=args.discover_functions,
    )

    # Create a handler registry with real file IO for CLI usage
    handler_registry = FileTypeHandlerRegistry()
    handler_registry.register_all_handlers()

    # Use default event bus for CLI with real file IO
    output = run_stamper_node(
        input_state,
        correlation_id=correlation_id,
        handler_registry=handler_registry,
        file_io=RealFileIO(),
    )
    emit_log_event(
        LogLevelEnum.INFO,
        output.model_dump_json(indent=2),
        node_id=_COMPONENT_NAME,
    )


if __name__ == "__main__":
    main()
