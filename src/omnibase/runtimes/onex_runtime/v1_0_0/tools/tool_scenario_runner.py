from pathlib import Path
import yaml
from typing import Any
from omnibase.runtimes.onex_runtime.v1_0_0.protocol.tool_scenario_runner_protocol import ToolScenarioRunnerProtocol
from pydantic import ValidationError
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync, make_log_context
from omnibase.enums.log_level import LogLevelEnum

def normalize_version_dict(d):
    if not isinstance(d, dict):
        return d
    keys = ["major", "minor", "patch", "prerelease", "build"]
    return {k: d.get(k) for k in keys if k in d and d.get(k) is not None}

def deep_partial_compare(model_dict, expect_dict):
    """Recursively check that all fields in expect_dict are present and equal in model_dict."""
    for k, v in expect_dict.items():
        if k not in model_dict:
            return False, f"Missing key: {k}"
        model_v = model_dict[k]
        if k == "version" and isinstance(model_v, dict) and isinstance(v, dict):
            model_v = normalize_version_dict(model_v)
            v = normalize_version_dict(v)
        if isinstance(v, dict) and isinstance(model_v, dict):
            ok, msg = deep_partial_compare(model_v, v)
            if not ok:
                return False, msg
        elif model_v != v:
            return False, f"Mismatch for key '{k}': expected {v}, got {model_v}"
    return True, ""

def strip_none(d):
    if isinstance(d, dict):
        return {k: strip_none(v) for k, v in d.items() if v is not None}
    elif isinstance(d, list):
        return [strip_none(x) for x in d]
    else:
        return d

class ToolScenarioRunner(ToolScenarioRunnerProtocol):
    def run_scenario(self, node: Any, scenario_id: str, scenario_registry: dict, node_scenarios_dir: Path = None, correlation_id: str = None) -> Any:
        scenario = next((s for s in scenario_registry.get("scenarios", []) if s["id"] == scenario_id), None)
        if not scenario:
            raise ValueError(f"Scenario with id '{scenario_id}' not found.")
        entrypoint = scenario.get("entrypoint")
        if not entrypoint:
            raise ValueError(f"Scenario '{scenario_id}' missing entrypoint.")
        scenario_path = Path(entrypoint)
        if not scenario_path.is_absolute():
            if node_scenarios_dir is None:
                raise ValueError("node_scenarios_dir must be provided for relative scenario entrypoints.")
            scenario_path = node_scenarios_dir / Path(entrypoint).name
        with open(scenario_path, "r") as f:
            scenario_yaml = yaml.safe_load(f)
        input_data = scenario_yaml["chain"][0]["input"]
        expect_data = scenario_yaml["chain"][0].get("expect", {})
        partial = scenario_yaml["chain"][0].get("partial", False)
        # At the start of each scenario, emit a colored INFO entry
        emit_log_event_sync(LogLevelEnum.INFO, f"=== SCENARIO START: {scenario_id} ===", make_log_context(correlation_id=correlation_id))
        emit_log_event_sync(LogLevelEnum.DEBUG, input_data, make_log_context(correlation_id=correlation_id))
        result = node.run(input_data)
        if hasattr(result, 'model_dump'):
            result_dict = result.model_dump(mode='json')
        else:
            result_dict = result
        pretty_model = strip_none(result_dict)
        emit_log_event_sync(LogLevelEnum.DEBUG, pretty_model, make_log_context(correlation_id=correlation_id))
        # Canonical model-driven validation
        output_model_cls = getattr(node, 'output_state_class', None)
        if output_model_cls is None:
            # Fallback: try to import from node.models.state
            try:
                output_model_cls = __import__(f"{node.__module__}.models.state", fromlist=["TemplateNodeOutputState"]).TemplateNodeOutputState
            except Exception:
                output_model_cls = None
        try:
            if output_model_cls is not None:
                try:
                    model_instance = output_model_cls(**result_dict)
                    expect_instance = output_model_cls(**expect_data)
                    model_json = model_instance.model_dump(mode='json', exclude_none=True)
                    expect_json = expect_instance.model_dump(mode='json', exclude_none=True)
                    emit_log_event_sync(LogLevelEnum.DEBUG, f"model_json after dump (exclude_none=True): {model_json}", make_log_context(correlation_id=correlation_id))
                    emit_log_event_sync(LogLevelEnum.DEBUG, f"expect_json after dump (exclude_none=True): {expect_json}", make_log_context(correlation_id=correlation_id))
                    # Explicitly clean version fields
                    if 'version' in model_json and isinstance(model_json['version'], dict):
                        model_json['version'] = {k: v for k, v in model_json['version'].items() if v is not None}
                    if 'version' in expect_json and isinstance(expect_json['version'], dict):
                        expect_json['version'] = {k: v for k, v in expect_json['version'].items() if v is not None}
                    pretty_model = strip_none(model_json)
                    pretty_expect = strip_none(expect_json)
                    emit_log_event_sync(LogLevelEnum.DEBUG, f"Cleaned model_json: {pretty_model}", make_log_context(correlation_id=correlation_id))
                    emit_log_event_sync(LogLevelEnum.DEBUG, f"Cleaned expect_json: {pretty_expect}", make_log_context(correlation_id=correlation_id))
                    if partial:
                        ok, msg = deep_partial_compare(model_json, expect_json)
                        if not ok:
                            return pretty_model, msg
                    else:
                        if model_json != expect_json:
                            return pretty_model, f"Output mismatch:\nExpected: {pretty_expect}\nGot: {pretty_model}"
                    emit_log_event_sync(LogLevelEnum.PASS, f"Scenario '{scenario_id}' output matches expected.", make_log_context(correlation_id=correlation_id))
                    # At the end of each scenario, emit a colored SUCCESS entry if pass, or ERROR if fail
                    if error is None:
                        emit_log_event_sync(LogLevelEnum.SUCCESS, f"=== SCENARIO END: {scenario_id} (PASS) ===", make_log_context(correlation_id=correlation_id))
                    return pretty_model, None
                except (ValidationError, AssertionError) as e:
                    emit_log_event_sync(LogLevelEnum.FAIL, f"Scenario '{scenario_id}': {e}", make_log_context(correlation_id=correlation_id))
                    return pretty_model, str(e)
            else:
                # Fallback: deep dict equality
                if partial:
                    ok, msg = deep_partial_compare(result_dict, expect_data)
                    if not ok:
                        emit_log_event_sync(LogLevelEnum.FAIL, f"Scenario '{scenario_id}': {msg}", make_log_context(correlation_id=correlation_id))
                        return pretty_model, msg
                else:
                    if result_dict != expect_data:
                        emit_log_event_sync(LogLevelEnum.FAIL, f"Scenario '{scenario_id}': Output mismatch.\nExpected: {expect_data}\nGot: {result_dict}", make_log_context(correlation_id=correlation_id))
                        return pretty_model, f"Output mismatch.\nExpected: {expect_data}\nGot: {pretty_model}"
                emit_log_event_sync(LogLevelEnum.PASS, f"Scenario '{scenario_id}' output matches expected.", make_log_context(correlation_id=correlation_id))
                return pretty_model, None
        except Exception as e:
            emit_log_event_sync(LogLevelEnum.FAIL, f"Scenario '{scenario_id}': {e}", make_log_context(correlation_id=correlation_id))
            return None, str(e)

tool_scenario_runner = ToolScenarioRunner() 