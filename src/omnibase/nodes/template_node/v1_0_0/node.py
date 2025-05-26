# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: node.py
# version: 1.0.0
# uuid: 4f13e6e3-84de-4e5d-8579-f90f3dd41a16
# author: OmniNode Team
# created_at: 2025-05-24T09:29:37.987105
# last_modified_at: 2025-05-25T20:45:00
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 5aa9aa96ef80b9158d340ef33ab4819ec2ceeb1f608b2696a9363af138181e5c
# entrypoint: python@node.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.node
# meta_type: tool
# === /OmniNode:Metadata ===


"""
TEMPLATE: Main node implementation for template_node.

Replace this docstring with a description of your node's functionality.
Update the function names, logic, and imports as needed.
"""

import logging
import sys
from typing import Callable, Optional

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.error_codes import get_exit_code_for_status
from omnibase.model.enum_onex_status import OnexStatus
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import (
    OnexVersionLoader,
)

from .introspection import TemplateNodeIntrospection

# TEMPLATE: Update these imports to match your state models
from .models.state import TemplateInputState, TemplateOutputState

logger = logging.getLogger(__name__)


def run_template_node(
    input_state: TemplateInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., TemplateOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> TemplateOutputState:
    """
    TEMPLATE: Main node entrypoint for template_node.

    Replace this function with your node's main logic.
    Update the function name, parameters, and implementation as needed.

    Args:
        input_state: TemplateInputState (must include version)
        event_bus: ProtocolEventBus (optional, defaults to InMemoryEventBus)
        output_state_cls: Optional callable to construct output state (for testing/mocking)
        handler_registry: Optional FileTypeHandlerRegistry for custom file processing

    Returns:
        TemplateOutputState (version matches input_state.version)

    Example of node-local handler registration:
        registry = FileTypeHandlerRegistry()
        registry.register_handler(".custom", MyCustomHandler(), source="node-local")
        output = run_template_node(input_state, handler_registry=registry)
    """
    if event_bus is None:
        event_bus = InMemoryEventBus()
    if output_state_cls is None:
        output_state_cls = TemplateOutputState

    # TEMPLATE: Update this to match your node's identifier
    node_id = "template_node"

    # Emit NODE_START event
    event_bus.publish(
        OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id=node_id,
            metadata={"input_state": input_state.model_dump()},
        )
    )

    try:
        # TEMPLATE: Register node-local handlers if registry is provided
        # This demonstrates the plugin/override API for node-local handler extensions
        if handler_registry:
            logger.debug("Using custom handler registry for file processing")
            # TEMPLATE: Register custom handlers here as needed:
            # handler_registry.register_handler(".custom", MyCustomHandler(), source="node-local")
            # handler_registry.register_special("myconfig.yaml", MyConfigHandler(), source="node-local")

        # TEMPLATE: Replace this with your node's main logic
        # This is where you would implement your node's core functionality
        # If your node processes files, pass handler_registry to your engine/helper classes

        # Example template logic - replace with your implementation
        result_message = f"TEMPLATE: Processed {input_state.template_required_field}"

        # TEMPLATE: Update this to match your output state structure
        output = output_state_cls(
            version=input_state.version,
            status="success",
            message=result_message,
            template_output_field=f"TEMPLATE_RESULT_{input_state.template_required_field}",
        )

        # Emit NODE_SUCCESS event
        event_bus.publish(
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_SUCCESS,
                node_id=node_id,
                metadata={
                    "input_state": input_state.model_dump(),
                    "output_state": output.model_dump(),
                },
            )
        )

        return output

    except Exception as exc:
        # Emit NODE_FAILURE event
        event_bus.publish(
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_FAILURE,
                node_id=node_id,
                metadata={
                    "input_state": input_state.model_dump(),
                    "error": str(exc),
                },
            )
        )
        raise


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
    print(output.model_dump_json(indent=2))

    # Use canonical exit code mapping
    exit_code = get_exit_code_for_status(OnexStatus(output.status))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
