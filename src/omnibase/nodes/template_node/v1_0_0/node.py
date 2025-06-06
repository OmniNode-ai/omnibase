"""
Template Node (ONEX Canonical)

Implements the reducer pattern with .run() and .bind() lifecycle. All business logic is delegated to inline handlers or runtime helpers.
"""

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
import datetime
from datetime import timezone

import yaml
from pydantic import ValidationError

from omnibase.enums.enum_registry_output_status import RegistryOutputStatusEnum
from omnibase.enums.log_level import LogLevelEnum
from omnibase.enums.onex_status import OnexStatus
from omnibase.model.model_node_metadata import LogFormat, NodeMetadataBlock
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.model.model_output_field import OnexFieldModel
from omnibase.model.model_reducer import ActionModel, StateModel
from omnibase.model.model_semver import SemVerModel
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
from omnibase.protocol.protocol_reducer import ProtocolReducer
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import (
    MetadataYAMLHandler,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import (
    emit_log_event_sync,
    get_log_format,
    log_level_emoji,
    make_log_context,
    set_log_format,
)

from .introspection import TemplateNodeIntrospection
from .models.state import TemplateNodeInputState, TemplateNodeOutputState
from omnibase.nodes.template_node.protocols.input_validation_tool_protocol import InputValidationToolProtocol
from omnibase.nodes.template_node.protocols.output_field_tool_protocol import OutputFieldTool as OutputFieldToolProtocol
from omnibase.runtimes.onex_runtime.v1_0_0.protocol.tool_scenario_runner_protocol import ToolScenarioRunnerProtocol
from omnibase.runtimes.onex_runtime.v1_0_0.tools.tool_scenario_runner import ToolScenarioRunner
from omnibase.nodes.template_node.v1_0_0.tools.input.input_validation_tool import InputValidationTool
from omnibase.model.model_output_field_utils import compute_output_field
from omnibase.tools.tool_input_validation import ToolInputValidation
from omnibase.tools.tool_compute_output_field import tool_compute_output_field
from omnibase.mixin.mixin_node_id_from_contract import MixinNodeIdFromContract
from omnibase.mixin.mixin_introspect_from_contract import MixinIntrospectFromContract

NODE_ONEX_YAML_PATH = Path(__file__).parent / "node.onex.yaml"

TRACE_MODE = os.environ.get("ONEX_TRACE") == "1"
_trace_mode_flag = None


def is_trace_mode():
    global _trace_mode_flag
    if _trace_mode_flag is not None:
        return _trace_mode_flag
    import sys

    _trace_mode_flag = TRACE_MODE or ("--debug-trace" in sys.argv)
    return _trace_mode_flag


class TemplateNode(MixinNodeIdFromContract, MixinIntrospectFromContract, TemplateNodeIntrospection, ProtocolReducer):
    """
    Canonical ONEX reducer node implementing ProtocolReducer.
    
    **ALL business logic must be delegated to protocol-typed helpers/tools.**
    This class is strictly an orchestrator: it wires together protocol-compliant tools, event bus, and scenario runner.
    No business logic, validation, or output computation should be implemented inline here.
    
    Dependency injection for tools follows the ONEX canonical pattern:
    - All tools are injected via the constructor, typed as their Protocol interfaces.
    - Defaults are set to canonical implementations.
    - This enables easy swapping/mocking and future migration to a registry/DI framework (e.g., Eye).
    - When a registry is available, update the constructor to resolve tools from the registry.
    
    Maintainers: If you find business logic in this class, refactor it into a protocol-typed helper/tool.
    """

    def __init__(
        self,
        event_bus: ProtocolEventBus = None,
        input_validation_tool: InputValidationToolProtocol = ToolInputValidation(
            TemplateNodeInputState, TemplateNodeOutputState, OnexFieldModel, node_id="template_node"
        ),
        output_field_tool: OutputFieldToolProtocol = tool_compute_output_field,
        scenario_runner: ToolScenarioRunnerProtocol = ToolScenarioRunner(),
    ):
        node_id = self._load_node_id()
        super().__init__(node_id=node_id, event_bus=event_bus or get_event_bus())
        self.input_validation_tool: InputValidationToolProtocol = input_validation_tool
        self.output_field_tool: OutputFieldToolProtocol = output_field_tool
        self.scenario_runner: ToolScenarioRunnerProtocol = scenario_runner
        self.event_bus.subscribe(self.handle_event)
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"TemplateNode instantiated",
                context=make_log_context(node_id=self.node_id),
            )

    def handle_event(self, event: OnexEvent):
        """
        Orchestrates event-driven scenario execution. All business logic is delegated to protocol-typed helpers/tools.
        This method should never implement scenario logic directly.
        """
        if event.event_type != OnexEventTypeEnum.TOOL_PROXY_INVOKE:
            return
        if event.node_id != self.node_id:
            return
        metadata = event.metadata or {}
        scenario_id = metadata.get("scenario_id")
        log_format = metadata.get("log_format", "json")
        correlation_id = event.correlation_id
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[handle_event] Received TOOL_PROXY_INVOKE with scenario_id: {scenario_id}",
            context=make_log_context(
                node_id=self.node_id, correlation_id=correlation_id
            ),
        )
        try:
            if scenario_id:
                # Delegate to scenario runner
                scenarios_index_path = Path(__file__).parent / "scenarios" / "index.yaml"
                with open(scenarios_index_path, "r") as f:
                    scenario_registry = yaml.safe_load(f)
                node_scenarios_dir = Path(__file__).parent / "scenarios"
                result, error = self.scenario_runner.run_scenario(
                    self,
                    scenario_id,
                    scenario_registry,
                    node_scenarios_dir=node_scenarios_dir,
                    correlation_id=correlation_id,
                )
                result_event = OnexEvent(
                    event_id=uuid.uuid4(),
                    timestamp=None,
                    node_id=self.node_id,
                    event_type=OnexEventTypeEnum.TOOL_PROXY_RESULT,
                    correlation_id=correlation_id,
                    metadata={
                        "result": result,
                        "error": error,
                        "log_format": log_format,
                    },
                )
                self.event_bus.publish(result_event)
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[handle_event] Scenario complete for correlation_id: {correlation_id}",
                    context=make_log_context(
                        node_id=self.node_id, correlation_id=correlation_id
                    ),
                )
            else:
                emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"[handle_event] No scenario_id provided in TOOL_PROXY_INVOKE metadata.",
                    context=make_log_context(
                        node_id=self.node_id, correlation_id=correlation_id
                    ),
                )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[handle_event] Exception during scenario: {e}",
                context=make_log_context(
                    node_id=self.node_id, correlation_id=correlation_id
                ),
            )
            raise

    def run(self, input_state: TemplateNodeInputState) -> TemplateNodeOutputState:
        """
        Orchestrates scenario execution for direct invocation. Accepts a validated TemplateNodeInputState model.
        All output computation and business logic must be delegated to protocol-typed helpers/tools.
        """
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"Entered run() with input_state: {input_state}",
                context=make_log_context(node_id=self.node_id),
            )
        semver = SemVerModel.parse(str(self.node_version))
        # Use protocol-compliant output field tool
        output_field = self.output_field_tool(input_state, input_state.model_dump())
        # Ensure event_id and timestamp are always set
        event_id = getattr(input_state, 'event_id', None) or str(uuid.uuid4())
        timestamp = getattr(input_state, 'timestamp', None)
        if not timestamp:
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"Exiting run() with output_field: {output_field}, event_id: {event_id}, timestamp: {timestamp}",
                context=make_log_context(node_id=self.node_id),
            )
        return TemplateNodeOutputState(
            version=semver,
            status=OnexStatus.SUCCESS,
            message="TemplateNode ran successfully.",
            output_field=output_field,
            event_id=event_id,
            timestamp=timestamp,
            correlation_id=getattr(input_state, 'correlation_id', None),
            node_name=getattr(input_state, 'node_name', None),
            node_version=str(self.node_version),
        )

    def bind(self, *args, **kwargs):
        """
        Bind pattern stub. In ONEX, this is used for chaining nodes.
        """
        return self

    def initial_state(self) -> StateModel:
        """
        Return the initial state for the reducer. Override as needed.
        """
        return TemplateNodeInputState(
            version=SemVerModel(
                str(NodeMetadataBlock.from_file(NODE_ONEX_YAML_PATH).version)
            ),
            input_field="",
            optional_field=None,
        )

    def dispatch(self, state: StateModel, action: ActionModel) -> StateModel:
        """
        Intentionally minimal for the template node: returns the state unchanged.
        In production nodes, all business logic for state transitions should be delegated to protocol-typed helpers/tools.
        """
        return state

    def introspect(self):
        """
        Return a list of available scenarios for this node from scenarios/index.yaml.
        """
        scenarios_index_path = Path(__file__).parent / "scenarios" / "index.yaml"
        if not scenarios_index_path.exists():
            return {"scenarios": []}
        with open(scenarios_index_path, "r") as f:
            data = yaml.safe_load(f)
        return data


def main(event_bus=None):
    if event_bus is None:
        event_bus = get_event_bus()
    parser = argparse.ArgumentParser(description="ONEX Template Node")
    parser.add_argument(
        "--introspect", action="store_true", help="Show node introspection"
    )
    parser.add_argument("--run-scenario", type=str, help="Run a scenario by ID")
    parser.add_argument("--input", type=str, help="Input JSON for direct execution")
    parser.add_argument(
        "--debug-trace",
        action="store_true",
        help="Enable trace-level logging for demo/debug",
    )
    parser.add_argument(
        "--log-format",
        type=str,
        choices=[f.value for f in LogFormat],
        default=LogFormat.JSON.value,
        help="Log output format (json, text, key-value, markdown, yaml, csv)",
    )
    args = parser.parse_args()

    # Set trace mode flag if --debug-trace is present
    global _trace_mode_flag
    if args.debug_trace:
        _trace_mode_flag = True
    try:
        log_format_enum = LogFormat(args.log_format.lower())
    except ValueError:
        log_format_enum = LogFormat.JSON
    set_log_format(log_format_enum)
    emit_log_event_sync(
        LogLevelEnum.DEBUG,
        f"[main] set_log_format to {get_log_format()}",
        make_log_context(node_id="template_node"),
    )

    node = TemplateNode(event_bus=event_bus)
    if args.introspect:
        TemplateNodeIntrospection.handle_introspect_command()
    elif args.run_scenario:
        scenario_id = args.run_scenario
        scenarios = TemplateNodeIntrospection.get_scenarios()
        scenario = next((s for s in scenarios if s["id"] == scenario_id), None)
        if not scenario:
            sys.exit(1)
        entrypoint = scenario.get("entrypoint")
        if not entrypoint:
            sys.exit(1)
        try:
            scenario_path = Path(__file__).parent / entrypoint
            with open(scenario_path, "r") as f:
                scenario_yaml = yaml.safe_load(f)
            input_data = scenario_yaml["chain"][0]["input"]
        except Exception as e:
            sys.exit(1)
        try:
            result = node.run(input_data)
        except Exception as e:
            sys.exit(1)
    elif args.input:
        try:
            input_data = json.loads(args.input)
            result = node.run(input_data)
        except Exception as e:
            sys.exit(1)
    else:
        sys.exit(1)


def get_introspection() -> dict:
    """Get introspection data for the template node."""
    return TemplateNodeIntrospection.get_introspection_response()


if __name__ == "__main__":
    node = TemplateNode()
    import time

    while True:
        time.sleep(1)
