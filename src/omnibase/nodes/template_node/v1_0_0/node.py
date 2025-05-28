# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: node.py
# version: 1.0.0
# uuid: 63cc9b05-2058-4fe9-a82f-88d543e5554a
# author: OmniNode Team
# created_at: 2025-05-28T12:36:26.928181
# last_modified_at: 2025-05-28T17:20:05.224569
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 8ae84cdc132ab24156893249625abf4ff007a53e1eb2dd84a3bb3001859501dc
# entrypoint: python@node.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.node
# meta_type: tool
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
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import (
    OnexVersionLoader,
)
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import telemetry

from .introspection import TemplateNodeIntrospection

# TEMPLATE: Update these imports to match your state models
from .models.state import TemplateInputState, TemplateOutputState

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class TemplateNode(EventDrivenNodeMixin):
    def __init__(self, node_id: str = "template_node", event_bus: Optional[ProtocolEventBus] = None, **kwargs):
        super().__init__(node_id=node_id, event_bus=event_bus, **kwargs)

    @telemetry(node_name="template_node", operation="run")
    def run(self, input_state: TemplateInputState, output_state_cls: Optional[Callable[..., TemplateOutputState]] = None, handler_registry: Optional[FileTypeHandlerRegistry] = None, event_bus: Optional[ProtocolEventBus] = None, **kwargs) -> TemplateOutputState:
        if output_state_cls is None:
            output_state_cls = TemplateOutputState
        self.emit_node_start({"input_state": input_state.model_dump()})
        try:
            if handler_registry:
                emit_log_event(
                    LogLevelEnum.DEBUG,
                    "Using custom handler registry for file processing",
                    node_id=self.node_id,
                )
            result_message = f"TEMPLATE: Processed {input_state.template_required_field}"
            output = output_state_cls(
                version=input_state.version,
                status="success",
                message=result_message,
                template_output_field=f"TEMPLATE_RESULT_{input_state.template_required_field}",
            )
            self.emit_node_success({
                "input_state": input_state.model_dump(),
                "output_state": output.model_dump(),
            })
            return output
        except Exception as exc:
            self.emit_node_failure({
                "input_state": input_state.model_dump(),
                "error": str(exc),
            })
            raise


def run_template_node(
    input_state: TemplateInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., TemplateOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> TemplateOutputState:
    node = TemplateNode(event_bus=event_bus)
    return node.run(input_state, output_state_cls=output_state_cls, handler_registry=handler_registry)


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

    args = parser.parse_args()

    # Handle introspection command
    if args.introspect:
        TemplateNodeIntrospection.handle_introspect_command()
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
    output = run_template_node(input_state)

    # Print the output
    emit_log_event(
        LogLevelEnum.INFO,
        output.model_dump_json(indent=2),
        node_id=_COMPONENT_NAME,
    )

    # Use canonical exit code mapping
    exit_code = get_exit_code_for_status(OnexStatus(output.status))
    sys.exit(exit_code)


def get_introspection() -> dict:
    """Get introspection data for the template node."""
    return TemplateNodeIntrospection.get_introspection_response().model_dump()


if __name__ == "__main__":
    main()
