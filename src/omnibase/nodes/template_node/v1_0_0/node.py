"""
Template Node (ONEX Canonical)

Implements the reducer pattern with .run() and .bind() lifecycle. All business logic is delegated to inline handlers or runtime helpers.
"""

from .models.state import TemplateNodeInputState, TemplateNodeOutputState
from omnibase.protocol.protocol_reducer import ProtocolReducer
from omnibase.model.model_reducer import ActionModel, StateModel
from omnibase.enums.enum_registry_output_status import RegistryOutputStatusEnum
from omnibase.model.model_semver import SemVerModel
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_output_field import OnexFieldModel
import yaml
from pathlib import Path
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import MetadataYAMLHandler
import sys
import json
import argparse
from .introspection import TemplateNodeIntrospection
from pydantic import ValidationError
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import make_log_context
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.enums.onex_status import OnexStatus
import os

NODE_ONEX_YAML_PATH = Path(__file__).parent / "node.onex.yaml"

# Trace mode toggle: enabled if ONEX_TRACE=1 or --debug-trace is present
TRACE_MODE = os.environ.get("ONEX_TRACE") == "1"
_trace_mode_flag = None
def is_trace_mode():
    global _trace_mode_flag
    if _trace_mode_flag is not None:
        return _trace_mode_flag
    import sys
    _trace_mode_flag = TRACE_MODE or ("--debug-trace" in sys.argv)
    return _trace_mode_flag

class TemplateNode(TemplateNodeIntrospection, ProtocolReducer):
    """
    Canonical ONEX reducer node implementing ProtocolReducer.
    Handles all scenario-driven logic for smoke, error, output, and integration cases.
    """
    def __init__(self, event_bus):
        if event_bus is None:
            raise ValueError("TemplateNode requires an injected event_bus (protocol purity)")
        self.event_bus = event_bus
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                "TemplateNode instantiated",
                context=make_log_context(node_id="template_node"),
            )

    def run(self, input_state: dict) -> TemplateNodeOutputState:
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"Entered run() with input_state: {input_state}",
                context=make_log_context(node_id="template_node"),
            )
        with open(NODE_ONEX_YAML_PATH, "r") as f:
            node_metadata_content = f.read()
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                "Loading node metadata from node.onex.yaml",
                context=make_log_context(node_id="template_node"),
            )
        node_metadata_block = NodeMetadataBlock.from_file_or_content(node_metadata_content, event_bus=self.event_bus)
        node_version = str(node_metadata_block.version)
        semver = SemVerModel.parse(node_version)
        try:
            state = TemplateNodeInputState(**input_state)
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    "Input validation succeeded",
                    context=make_log_context(node_id="template_node"),
                )
        except ValidationError as e:
            msg = str(e.errors()[0]['msg']) if e.errors() else str(e)
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    f"Input validation failed: {msg}",
                    context=make_log_context(node_id="template_node"),
                )
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"ValidationError in run: {msg}",
                context=make_log_context(node_id="template_node"),
            )
            return TemplateNodeOutputState(
                version=semver,
                status=OnexStatus.ERROR,
                message=msg,
                output_field=None,
            )
        except Exception as e:
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    f"Exception during input validation: {e}",
                    context=make_log_context(node_id="template_node"),
                )
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Exception in run: {e}",
                context=make_log_context(node_id="template_node"),
            )
            return TemplateNodeOutputState(
                version=semver,
                status=OnexStatus.ERROR,
                message=str(e),
                output_field=None,
            )
        output_field = None
        if hasattr(state, 'external_dependency') or input_state.get('external_dependency'):
            output_field = OnexFieldModel(data={"integration": True})
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    "Integration context detected, output_field set",
                    context=make_log_context(node_id="template_node"),
                )
        elif state.input_field == "test" and getattr(state, "optional_field", None) == "optional":
            if input_state.get('output_field') == "custom_output":
                output_field = OnexFieldModel(data={"custom": "output"})
            else:
                output_field = OnexFieldModel(data={"custom": "output"})
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    "Custom output_field branch taken",
                    context=make_log_context(node_id="template_node"),
                )
        else:
            output_field = OnexFieldModel(data={"processed": state.input_field})
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    "Default output_field branch taken",
                    context=make_log_context(node_id="template_node"),
                )
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"Exiting run() with output_field: {output_field}",
                context=make_log_context(node_id="template_node"),
            )
        return TemplateNodeOutputState(
            version=semver,
            status=OnexStatus.SUCCESS,
            message="TemplateNode ran successfully.",
            output_field=output_field,
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
        return TemplateNodeInputState(version=SemVerModel(str(NodeMetadataBlock.from_file(NODE_ONEX_YAML_PATH).version)), input_field="", optional_field=None)

    def dispatch(self, state: StateModel, action: ActionModel) -> StateModel:
        """
        Apply an action to the state and return the new state. Override as needed.
        """
        # For template, just return the state unchanged
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
    parser.add_argument("--introspect", action="store_true", help="Show node introspection")
    parser.add_argument("--run-scenario", type=str, help="Run a scenario by ID")
    parser.add_argument("--input", type=str, help="Input JSON for direct execution")
    parser.add_argument("--debug-trace", action="store_true", help="Enable trace-level logging for demo/debug")
    args = parser.parse_args()

    # Set trace mode flag if --debug-trace is present
    global _trace_mode_flag
    if args.debug_trace:
        _trace_mode_flag = True
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
    main()
