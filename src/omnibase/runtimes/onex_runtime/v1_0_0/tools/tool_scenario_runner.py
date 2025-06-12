from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import ValidationError
import uuid
from datetime import datetime
import asyncio

from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.protocol.tool_scenario_runner_protocol import (
    ToolScenarioRunnerProtocol,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import (
    emit_log_event_sync,
    make_log_context,
)
# strip_none function defined locally below
# deep_partial_compare function defined locally below
from omnibase.model.model_scenario import ScenarioConfigModel
from omnibase.model.model_scenario_precondition import (
    ModelScenarioPreConditionResult, 
    ModelServicePreConditionResult,
    PreConditionStatusEnum
)
from omnibase.registry.registry_external_service_manager import get_external_service_manager
from omnibase.enums.enum_dependency_mode import DependencyModeEnum


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
    async def validate_preconditions(
        self,
        scenario_config: ScenarioConfigModel,
        skip_preconditions: bool = False
    ) -> ModelScenarioPreConditionResult:
        """
        Validate pre-conditions for a scenario before execution.
        Checks external service availability when dependency_mode is 'real'.
        """
        start_time = datetime.now()
        scenario_name = scenario_config.scenario_name
        
        # Check if pre-conditions should be skipped
        if skip_preconditions:
            return ModelScenarioPreConditionResult(
                scenario_name=scenario_name,
                overall_status=PreConditionStatusEnum.SKIPPED,
                services_checked=[],
                total_check_time_ms=0.0,
                required_services_healthy=True,
                skipped_reason="Pre-conditions explicitly skipped via --skip-preconditions flag"
            )
        
        # If dependency mode is mock, skip external service checks
        if scenario_config.dependency_mode == DependencyModeEnum.MOCK:
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds() * 1000
            
            return ModelScenarioPreConditionResult(
                scenario_name=scenario_name,
                overall_status=PreConditionStatusEnum.SKIPPED,
                services_checked=[],
                total_check_time_ms=total_time,
                required_services_healthy=True,
                skipped_reason="Dependency mode is 'mock' - no external services to check"
            )
        
        # Real dependency mode - check external services
        if not scenario_config.external_services:
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds() * 1000
            
            return ModelScenarioPreConditionResult(
                scenario_name=scenario_name,
                overall_status=PreConditionStatusEnum.HEALTHY,
                services_checked=[],
                total_check_time_ms=total_time,
                required_services_healthy=True,
                skipped_reason="No external services configured"
            )
        
        # Perform health checks on external services
        service_manager = get_external_service_manager()
        service_results = []
        required_services_count = 0
        optional_services_count = 0
        all_required_healthy = True
        
        for service_name, service_config in scenario_config.external_services.items():
            is_required = service_config.required
            if is_required:
                required_services_count += 1
            else:
                optional_services_count += 1
            
            try:
                # Perform health check
                health_result = await service_manager.validate_service_availability(service_config)
                
                # Convert to pre-condition result
                precondition_result = ModelServicePreConditionResult.from_health_result(
                    health_result, is_required
                )
                service_results.append(precondition_result)
                
                # Track if required services are healthy
                if is_required and not health_result.is_healthy:
                    all_required_healthy = False
                    
            except Exception as e:
                # Handle health check errors
                error_result = ModelServicePreConditionResult(
                    service_name=service_name,
                    status=PreConditionStatusEnum.ERROR,
                    is_required=is_required,
                    error_message=str(e),
                    timestamp=datetime.now()
                )
                service_results.append(error_result)
                
                if is_required:
                    all_required_healthy = False
        
        # Calculate overall status
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        
        if all_required_healthy:
            overall_status = PreConditionStatusEnum.HEALTHY
        else:
            overall_status = PreConditionStatusEnum.UNHEALTHY
        
        return ModelScenarioPreConditionResult(
            scenario_name=scenario_name,
            overall_status=overall_status,
            services_checked=service_results,
            total_check_time_ms=total_time,
            required_services_healthy=all_required_healthy,
            required_services_count=required_services_count,
            optional_services_count=optional_services_count
        )

    def run_scenario(
        self,
        node: Any,
        scenario_id: str,
        scenario_registry: dict,
        node_scenarios_dir: Path = None,
        correlation_id: str = None,
        skip_preconditions: bool = False,
    ) -> Any:
        scenario = next(
            (
                s
                for s in scenario_registry.get("scenarios", [])
                if s["id"] == scenario_id
            ),
            None,
        )
        if not scenario:
            raise ValueError(f"Scenario with id '{scenario_id}' not found.")
        entrypoint = scenario.get("entrypoint")
        if not entrypoint:
            raise ValueError(f"Scenario '{scenario_id}' missing entrypoint.")
        scenario_path = Path(entrypoint)
        if not scenario_path.is_absolute():
            if node_scenarios_dir is None:
                raise ValueError(
                    "node_scenarios_dir must be provided for relative scenario entrypoints."
                )
            scenario_path = node_scenarios_dir / Path(entrypoint).name
        
        with open(scenario_path, "r") as f:
            scenario_yaml = yaml.safe_load(f)
        
        # Parse scenario configuration for pre-condition validation
        try:
            scenario_config = ScenarioConfigModel(**scenario_yaml)
        except ValidationError as e:
            emit_log_event_sync(
                LogLevelEnum.WARNING,
                f"Could not parse scenario config for pre-condition validation: {e}",
                make_log_context(correlation_id=correlation_id),
            )
            scenario_config = None
        
        # === PRE-CONDITION VALIDATION ===
        if scenario_config and not skip_preconditions:
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"=== PRE-CONDITION VALIDATION: {scenario_id} ===",
                make_log_context(correlation_id=correlation_id),
            )
            
            try:
                # Run pre-condition validation
                precondition_result = asyncio.run(
                    self.validate_preconditions(scenario_config, skip_preconditions)
                )
                
                # Log pre-condition summary
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    precondition_result.get_summary_message(),
                    make_log_context(correlation_id=correlation_id),
                )
                
                # Log detailed service status
                for log_entry in precondition_result.get_detailed_log_entries():
                    emit_log_event_sync(
                        LogLevelEnum.DEBUG,
                        log_entry,
                        make_log_context(correlation_id=correlation_id),
                    )
                
                # Check if scenario should be skipped
                if precondition_result.should_skip_scenario():
                    emit_log_event_sync(
                        LogLevelEnum.WARNING,
                        f"=== SCENARIO SKIPPED: {scenario_id} (Pre-conditions failed) ===",
                        make_log_context(correlation_id=correlation_id),
                    )
                    return {
                        "status": "skipped",
                        "reason": "pre_conditions_failed",
                        "precondition_result": precondition_result.model_dump(),
                        "message": precondition_result.get_summary_message()
                    }, None
                    
            except Exception as e:
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    f"Pre-condition validation failed: {e}",
                    make_log_context(correlation_id=correlation_id),
                )
                # Continue with scenario execution despite pre-condition error
        
        # === SCENARIO EXECUTION ===
        input_data = scenario_yaml["chain"][0]["input"]
        expect_data = scenario_yaml["chain"][0].get("expect", {})
        partial = scenario_yaml["chain"][0].get("partial", False)
        
        # At the start of each scenario, emit a colored INFO entry
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"=== SCENARIO START: {scenario_id} ===",
            make_log_context(correlation_id=correlation_id),
        )
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            input_data,
            make_log_context(correlation_id=correlation_id),
        )
        result = node.run(input_data)
        if hasattr(result, "model_dump"):
            result_dict = result.model_dump(mode="json")
        else:
            result_dict = result
        pretty_model = strip_none(result_dict)
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            pretty_model,
            make_log_context(correlation_id=correlation_id),
        )
        # Canonical model-driven validation
        output_model_cls = getattr(node, "output_state_class", None)
        if output_model_cls is None:
            # Fallback: try to import from node.models.state
            try:
                output_model_cls = __import__(
                    f"{node.__module__}.models.state",
                    fromlist=["NodeTemplateOutputState"],
                ).NodeTemplateOutputState
            except Exception:
                output_model_cls = None
        try:
            if output_model_cls is not None:
                try:
                    model_instance = output_model_cls(**result_dict)
                    expect_instance = output_model_cls(**expect_data)
                    model_json = model_instance.model_dump(
                        mode="json", exclude_none=True
                    )
                    expect_json = expect_instance.model_dump(
                        mode="json", exclude_none=True
                    )
                    emit_log_event_sync(
                        LogLevelEnum.DEBUG,
                        f"model_json after dump (exclude_none=True): {model_json}",
                        make_log_context(correlation_id=correlation_id),
                    )
                    emit_log_event_sync(
                        LogLevelEnum.DEBUG,
                        f"expect_json after dump (exclude_none=True): {expect_json}",
                        make_log_context(correlation_id=correlation_id),
                    )
                    error = None
                    if partial:
                        ok, msg = deep_partial_compare(model_json, expect_json)
                        if not ok:
                            error = msg
                    else:
                        if model_json != expect_json:
                            error = f"Output mismatch.\nExpected: {expect_json}\nGot: {model_json}"
                    if error:
                        emit_log_event_sync(
                            LogLevelEnum.FAIL,
                            f"Scenario '{scenario_id}': {error}",
                            make_log_context(correlation_id=correlation_id),
                        )
                        emit_log_event_sync(
                            LogLevelEnum.ERROR,
                            f"=== SCENARIO END: {scenario_id} (FAIL) ===",
                            make_log_context(correlation_id=correlation_id),
                        )
                        return pretty_model, error
                    emit_log_event_sync(
                        LogLevelEnum.PASS,
                        f"Scenario '{scenario_id}' output matches expected.",
                        make_log_context(correlation_id=correlation_id),
                    )
                    # At the end of each scenario, emit a colored SUCCESS entry if pass, or ERROR if fail
                    if error is None:
                        emit_log_event_sync(
                            LogLevelEnum.SUCCESS,
                            f"=== SCENARIO END: {scenario_id} (PASS) ===",
                            make_log_context(correlation_id=correlation_id),
                        )
                    return pretty_model, None
                except (ValidationError, AssertionError) as e:
                    emit_log_event_sync(
                        LogLevelEnum.FAIL,
                        f"Scenario '{scenario_id}': {e}",
                        make_log_context(correlation_id=correlation_id),
                    )
                    return pretty_model, str(e)
            else:
                # Fallback: deep dict equality
                if partial:
                    ok, msg = deep_partial_compare(result_dict, expect_data)
                    if not ok:
                        emit_log_event_sync(
                            LogLevelEnum.FAIL,
                            f"Scenario '{scenario_id}': {msg}",
                            make_log_context(correlation_id=correlation_id),
                        )
                        return pretty_model, msg
                else:
                    if result_dict != expect_data:
                        emit_log_event_sync(
                            LogLevelEnum.FAIL,
                            f"Scenario '{scenario_id}': Output mismatch.\nExpected: {expect_data}\nGot: {result_dict}",
                            make_log_context(correlation_id=correlation_id),
                        )
                        return (
                            pretty_model,
                            f"Output mismatch.\nExpected: {expect_data}\nGot: {pretty_model}",
                        )
                emit_log_event_sync(
                    LogLevelEnum.PASS,
                    f"Scenario '{scenario_id}' output matches expected.",
                    make_log_context(correlation_id=correlation_id),
                )
                return pretty_model, None
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.FAIL,
                f"Scenario '{scenario_id}': {e}",
                make_log_context(correlation_id=correlation_id),
            )
            return None, str(e)


tool_scenario_runner = ToolScenarioRunner()
