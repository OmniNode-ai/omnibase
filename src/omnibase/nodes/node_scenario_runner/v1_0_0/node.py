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
# namespace: python://omnibase.nodes.node_scenario_runner_node.v1_0_0.node
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
NODE_SCENARIO_RUNNER: Main node implementation for node_scenario_runner_node.

Replace this docstring with a description of your node's functionality.
Update the function names, logic, and imports as needed.
"""

import sys
from pathlib import Path
from typing import Callable, Optional

from omnibase.core.core_error_codes import get_exit_code_for_status
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import telemetry

from .introspection import NodeScenarioRunnerNodeIntrospection

# NODE_SCENARIO_RUNNER: Update these imports to match your state models
from .models.state import NodeScenarioRunnerInputState, NodeScenarioRunnerOutputState

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class NodeScenarioRunnerNode(EventDrivenNodeMixin):
    def __init__(self, event_bus: Optional[ProtocolEventBus] = None, **kwargs):
        super().__init__(node_id="node_scenario_runner_node", event_bus=event_bus, **kwargs)
        self.event_bus = event_bus or get_event_bus(mode="bind")  # Publisher

    @telemetry(node_name="node_scenario_runner_node", operation="run")
    def run(
        self,
        input_state: NodeScenarioRunnerInputState,
        output_state_cls: Optional[Callable[..., NodeScenarioRunnerOutputState]] = None,
        handler_registry: Optional[FileTypeHandlerRegistry] = None,
        event_bus: Optional[ProtocolEventBus] = None,
        **kwargs,
    ) -> NodeScenarioRunnerOutputState:
        if output_state_cls is None:
            output_state_cls = NodeScenarioRunnerOutputState
        self.emit_node_start({"input_state": input_state.model_dump()})
        try:
            if handler_registry:
                emit_log_event_sync(
                    LogLevelEnum.DEBUG,
                    "Using custom handler registry for file processing",
                    node_id=self.node_id,
                    event_bus=self.event_bus,
                )
            result_message = (
                f"NODE_SCENARIO_RUNNER: Processed {input_state.node_scenario_runner_required_field}"
            )
            output = output_state_cls(
                version=input_state.version,
                status="success",
                message=result_message,
                node_scenario_runner_output_field=f"NODE_SCENARIO_RUNNER_RESULT_{input_state.node_scenario_runner_required_field}",
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


def run_node_scenario_runner_node(
    input_state: NodeScenarioRunnerInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., NodeScenarioRunnerOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> NodeScenarioRunnerOutputState:
    if event_bus is None:
        event_bus = get_event_bus(mode="bind")  # Publisher
    node = NodeScenarioRunnerNode(event_bus=event_bus)
    return node.run(
        input_state,
        output_state_cls=output_state_cls,
        handler_registry=handler_registry,
        event_bus=event_bus,
    )


def main() -> None:
    """
    NODE_SCENARIO_RUNNER: CLI entrypoint for standalone execution.

    Replace this with your node's CLI interface.
    Update the argument parser and logic as needed.
    """
    import argparse

    # NODE_SCENARIO_RUNNER: Update this parser to match your node's CLI interface
    parser = argparse.ArgumentParser(description="NODE_SCENARIO_RUNNER Node CLI")
    parser.add_argument(
        "node_scenario_runner_required_field",
        type=str,
        nargs="?",
        help="NODE_SCENARIO_RUNNER: Replace with your required argument",
    )
    parser.add_argument(
        "--node_scenario_runner-optional-field",
        type=str,
        default="NODE_SCENARIO_RUNNER_DEFAULT_VALUE",
        help="NODE_SCENARIO_RUNNER: Replace with your optional argument",
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
        NodeScenarioRunnerNodeIntrospection.handle_introspect_command(event_bus=event_bus)
        return

    # Validate required arguments for normal operation
    if not args.node_scenario_runner_required_field:
        parser.error("node_scenario_runner_required_field is required when not using --introspect")

    # Get schema version
    schema_version = OnexVersionLoader().get_onex_versions().schema_version

    # NODE_SCENARIO_RUNNER: Update this to match your input state structure
    input_state = NodeScenarioRunnerInputState(
        version=schema_version,
        node_scenario_runner_required_field=args.node_scenario_runner_required_field,
        node_scenario_runner_optional_field=args.node_scenario_runner_optional_field,
    )

    # Run the node with default event bus for CLI
    event_bus = get_event_bus(mode="bind")  # Publisher
    output = run_node_scenario_runner_node(input_state, event_bus=event_bus)

    # Print the output
    emit_log_event_sync(
        LogLevelEnum.INFO,
        output.model_dump_json(indent=2),
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )

    # Use canonical exit code mapping
    exit_code = get_exit_code_for_status(OnexStatus(output.status))
    sys.exit(exit_code)


def get_introspection() -> dict:
    """Get introspection data for the node_scenario_runner node."""
    return NodeScenarioRunnerNodeIntrospection.get_introspection_response().model_dump()


if __name__ == "__main__":
    main()
