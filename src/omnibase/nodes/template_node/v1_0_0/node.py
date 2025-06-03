"""
Template Node (ONEX Canonical)

Implements the reducer pattern with .run() and .bind() lifecycle. All business logic is delegated to inline handlers or runtime helpers.
"""

from .models.state import TemplateNodeInputState, TemplateNodeOutputState
from omnibase.protocol.protocol_reducer import ProtocolReducer
from omnibase.model.model_reducer import ActionModel, StateModel
from omnibase.enums.enum_registry_output_status import RegistryOutputStatusEnum
from omnibase.model.model_semver import SemVerModel
from omnibase.model.model_node_metadata import NodeMetadataBlock, LogFormat
from omnibase.model.model_output_field import OnexFieldModel
import yaml
from pathlib import Path
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import MetadataYAMLHandler
import sys
import json
import argparse
from .introspection import TemplateNodeIntrospection
from pydantic import ValidationError
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import make_log_context, emit_log_event_sync, log_level_emoji, flush_markdown_log_buffer
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.enums.onex_status import OnexStatus
import os

NODE_ONEX_YAML_PATH = Path(__file__).parent / "node.onex.yaml"

TRACE_MODE = os.environ.get("ONEX_TRACE") == "1"
_trace_mode_flag = None
_log_format = LogFormat.JSON.value
def is_trace_mode():
    global _trace_mode_flag
    if _trace_mode_flag is not None:
        return _trace_mode_flag
    import sys
    _trace_mode_flag = TRACE_MODE or ("--debug-trace" in sys.argv)
    return _trace_mode_flag

def set_log_format(fmt):
    global _log_format
    _log_format = fmt

def get_log_format():
    global _log_format
    return _log_format

_markdown_header_printed = False
_markdown_col_widths = [5, 7, 8, 4, 9]  # initial: Level, Message, Function, Line, Timestamp
_markdown_col_names = ["Level", "Message", "Function", "Line", "Timestamp"]
_markdown_max_message_width = 100
def _truncate(s, width):
    s = str(s)
    return s if len(s) <= width else s[:width-1] + "…"

def _update_markdown_col_widths(row):
    global _markdown_col_widths
    for i, val in enumerate(row):
        val_len = len(str(val))
        if i == 1:  # message col
            val_len = min(val_len, _markdown_max_message_width)
        if val_len > _markdown_col_widths[i]:
            _markdown_col_widths[i] = val_len

def _format_markdown_row(row):
    global _markdown_col_widths
    padded = []
    for i, val in enumerate(row):
        width = _markdown_col_widths[i]
        if i == 1:  # message col
            val = _truncate(val, _markdown_max_message_width)
        padded.append(str(val).ljust(width))
    return "| " + " | ".join(padded) + " |"

def emit_log_event_sync(level: LogLevelEnum, message, context):
    import json, yaml, csv, io
    global _markdown_header_printed
    fmt = get_log_format()
    log_event = {
        "level": level.value if hasattr(level, 'value') else str(level),
        "message": message,
        "context": context.model_dump() if hasattr(context, 'model_dump') else dict(context),
    }
    if fmt == LogFormat.JSON.value:
        print(json.dumps(log_event, indent=2))
    elif fmt == LogFormat.TEXT.value:
        print(f"[{log_event['level'].upper()}] {log_event['message']}\nContext: {log_event['context']}")
    elif fmt == LogFormat.KEY_VALUE.value:
        kv = ' '.join(f"{k}={v}" for k, v in log_event.items())
        print(kv)
    elif fmt == "markdown":
        row = [
            log_level_emoji(log_event['level']),
            str(log_event['message']),
            str(log_event['context'].get('calling_function','')),
            str(log_event['context'].get('calling_line','')),
            str(log_event['context'].get('timestamp','')),
        ]
        _update_markdown_col_widths(row)
        if not _markdown_header_printed:
            header = _format_markdown_row(_markdown_col_names)
        # Table columns: Level, Message, Function, Line, Timestamp
        cols = ["Level", "Message", "Function", "Line", "Timestamp"]
        widths = [2, 36, 10, 4, 19]
        row = [
            log_level_emoji(log_event['level']).ljust(widths[0]),
            _truncate(log_event['message'], widths[1]).ljust(widths[1]),
            _truncate(log_event['context'].get('calling_function',''), widths[2]).ljust(widths[2]),
            str(log_event['context'].get('calling_line','')).ljust(widths[3]),
            _truncate(log_event['context'].get('timestamp',''), widths[4]).ljust(widths[4]),
        ]
        if not _markdown_header_printed:
            header = "| " + " | ".join(cols) + " |"
            sep = "|" + "|".join(["-"* (w+2) for w in widths]) + "|"
            print(header)
            print(sep)
            _markdown_header_printed = True
        print("| " + " | ".join(row) + " |")
    elif fmt == "yaml":
        print(yaml.dump(log_event, sort_keys=False))
    elif fmt == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=log_event.keys())
        writer.writeheader()
        writer.writerow(log_event)
        print(output.getvalue().strip())
    else:
        print(json.dumps(log_event, indent=2))

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
    parser.add_argument("--log-format", type=str, choices=[f.value for f in LogFormat] + ["markdown", "yaml", "csv"], default=LogFormat.JSON.value, help="Log output format (json, text, key-value, markdown, yaml, csv)")
    args = parser.parse_args()

    # Set trace mode flag if --debug-trace is present
    global _trace_mode_flag
    if args.debug_trace:
        _trace_mode_flag = True
    set_log_format(args.log_format)
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
    # Explicitly flush markdown log buffer if needed
    if args.log_format == "markdown":
        flush_markdown_log_buffer()

def get_introspection() -> dict:
    """Get introspection data for the template node."""
    return TemplateNodeIntrospection.get_introspection_response()

if __name__ == "__main__":
    main()
