# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.928181'
# description: Stamped by PythonHandler
# entrypoint: python://node
# hash: 053ef15192250f70a90bc14fb68215660a61964081693d02ab24ab65acb73df5
# last_modified_at: '2025-05-29T14:14:00.065973+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: node.py
# namespace: python://omnibase.nodes.template_node.v1_0_0.node
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 63cc9b05-2058-4fe9-a82f-88d543e5554a
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
TEMPLATE: Main node implementation for template_node.

Replace this docstring with a description of your node's functionality.
Update the function names, logic, and imports as needed.
"""

import sys
from pathlib import Path
from typing import Callable, Optional

from omnibase.core.core_error_codes import get_exit_code_for_status
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import telemetry

from .introspection import TemplateNodeIntrospection

# TEMPLATE: Update these imports to match your state models
from .models.state import TemplateInputState, TemplateOutputState

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class TemplateNode(EventDrivenNodeMixin):
    def __init__(self, event_bus: Optional[ProtocolEventBus] = None, **kwargs):
        super().__init__(node_id="template_node", event_bus=event_bus, **kwargs)
        self.event_bus = event_bus or get_event_bus(mode="bind")  # Publisher

    @telemetry(node_name="template_node", operation="run")
    def run(
        self,
        input_state: TemplateInputState,
        output_state_cls: Optional[Callable[..., TemplateOutputState]] = None,
        handler_registry: Optional[FileTypeHandlerRegistry] = None,
        event_bus: Optional[ProtocolEventBus] = None,
        **kwargs,
    ) -> TemplateOutputState:
        if output_state_cls is None:
            output_state_cls = TemplateOutputState
        self.emit_node_start({"input_state": input_state.model_dump()})
        try:
            if handler_registry:
                emit_log_event(
                    LogLevelEnum.DEBUG,
                    "Using custom handler registry for file processing",
                    node_id=self.node_id,
                    event_bus=self.event_bus,
                )
            result_message = (
                f"TEMPLATE: Processed {input_state.template_required_field}"
            )
            output = output_state_cls(
                version=input_state.version,
                status="success",
                message=result_message,
                template_output_field=f"TEMPLATE_RESULT_{input_state.template_required_field}",
            )
            self.emit_node_success(
                {
                    "input_state": input_state.model_dump(),
                    "output_state": output.model_dump(),
                }
            )
            return output
        except Exception as exc:
            self.emit_node_failure(
                {
                    "input_state": input_state.model_dump(),
                    "error": str(exc),
                }
            )
            raise


def run_template_node(
    input_state: TemplateInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., TemplateOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> TemplateOutputState:
    if event_bus is None:
        event_bus = get_event_bus(mode="bind")  # Publisher
    node = TemplateNode(event_bus=event_bus)
    return node.run(
        input_state,
        output_state_cls=output_state_cls,
        handler_registry=handler_registry,
        event_bus=event_bus,
    )


def main() -> None:
    """
    TEMPLATE: CLI entrypoint for standalone execution.

    Replace this with your node's CLI interface.
    Update the argument parser and logic as needed.
    """
    import argparse

    # TEMPLATE: Update this parser to match your node's CLI interface
    parser = argparse.ArgumentParser(description="TEMPLATE Node CLI")
    parser.add_argument(
        "template_required_field",
        type=str,
        nargs="?",
        help="TEMPLATE: Replace with your required argument",
    )
    parser.add_argument(
        "--template-optional-field",
        type=str,
        default="TEMPLATE_DEFAULT_VALUE",
        help="TEMPLATE: Replace with your optional argument",
    )
    parser.add_argument(
        "--introspect",
        action="store_true",
        help="Display node contract and capabilities",
    )
    parser.add_argument(
        "--correlation-id", type=str, help="Correlation ID for request tracking"
    )

    args = parser.parse_args()

    # Handle introspection command
    event_bus = get_event_bus(mode="bind")  # Publisher
    if args.introspect:
        TemplateNodeIntrospection.handle_introspect_command(event_bus=event_bus)
        return

    # Validate required arguments for normal operation
    if not args.template_required_field:
        parser.error("template_required_field is required when not using --introspect")

    # Get schema version
    schema_version = OnexVersionLoader().get_onex_versions().schema_version

    # TEMPLATE: Update this to match your input state structure
    input_state = TemplateInputState(
        version=schema_version,
        template_required_field=args.template_required_field,
        template_optional_field=args.template_optional_field,
    )

    # Run the node with default event bus for CLI
    event_bus = get_event_bus(mode="bind")  # Publisher
    output = run_template_node(input_state, event_bus=event_bus)

    # Print the output
    emit_log_event(
        LogLevelEnum.INFO,
        output.model_dump_json(indent=2),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )

    # Use canonical exit code mapping
    exit_code = get_exit_code_for_status(OnexStatus(output.status))
    sys.exit(exit_code)


def get_introspection() -> dict:
    """Get introspection data for the template node."""
    return TemplateNodeIntrospection.get_introspection_response().model_dump()


if __name__ == "__main__":
    main()
