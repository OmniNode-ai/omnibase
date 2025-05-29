# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.696685'
# description: Stamped by PythonHandler
# entrypoint: python://node.py
# hash: 2c2725423252385bfa4ee6a3e01eb4a3372a9f3ef0f857bbb1b22aa464727de1
# last_modified_at: '2025-05-29T11:50:11.868138+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: node.py
# namespace: omnibase.node
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: ae931396-4b10-45ff-bf58-7421b5e2756e
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Callable, Optional

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event
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
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin

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


class StamperNode(EventDrivenNodeMixin):
    def __init__(self, node_id: str = "stamper_node", event_bus: Optional[ProtocolEventBus] = None, **kwargs):
        super().__init__(node_id=node_id, event_bus=event_bus, **kwargs)

    @telemetry(node_name="stamper_node", operation="run")
    def run(
        self,
        input_state: StamperInputState,
        handler_registry: Optional[FileTypeHandlerRegistry] = None,
        file_io: Optional[ProtocolFileIO] = None,
        event_bus: Optional[ProtocolEventBus] = None,
        **kwargs
    ) -> "OnexResultModel":
        """
        Run the stamper node and return the canonical OnexResultModel.
        """
        correlation_id = getattr(input_state, "correlation_id", None)
        self.emit_node_start({"input_state": input_state.model_dump()}, correlation_id=correlation_id)
        try:
            engine = StamperEngine(
                schema_loader=DummySchemaLoader(),
                file_io=file_io,
                handler_registry=handler_registry,
            )
            result = engine.stamp_file(
                Path(input_state.file_path),
                author=input_state.author,
                discover_functions=getattr(input_state, "discover_functions", False),
            )
            self.emit_node_success({
                "input_state": input_state.model_dump(),
                "output_state": result.model_dump() if hasattr(result, "model_dump") else {},
            }, correlation_id=correlation_id)
            return result
        except Exception as e:
            self.emit_node_failure({
                "input_state": input_state.model_dump(),
                "error": str(e),
            }, correlation_id=correlation_id)
            raise


def run_stamper_node(
    input_state: StamperInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
    file_io: Optional[ProtocolFileIO] = None,
    **kwargs
) -> "OnexResultModel":
    """
    Run the stamper node and return the canonical OnexResultModel.
    """
    node = StamperNode(event_bus=event_bus)
    return node.run(
        input_state,
        handler_registry=handler_registry,
        file_io=file_io,
        event_bus=event_bus,
        **kwargs
    )


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


def get_introspection() -> dict:
    """Get introspection data for the stamper node."""
    return StamperNodeIntrospection.get_introspection_response().model_dump()


if __name__ == "__main__":
    main()
