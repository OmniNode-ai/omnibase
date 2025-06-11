import pytest
import yaml
from typing import Any, Callable, Tuple, TypeVar, Generic, Type
import asyncio
import pydantic
from pathlib import Path
from pydantic import BaseModel
import os
import importlib
import hashlib

from omnibase.constants import (
    NODE_KEY,
    INPUT_KEY,
    EXPECT_KEY,
    VERSION_KEY,
    OUTPUT_FIELD_KEY,
    MESSAGE_KEY,
    FIELD_REQUIRED_ERROR_MSG,
    BACKEND_KEY,
    ERROR_VALUE,
    CHAIN_KEY,
    ERROR_TYPE_KEY,
    ERROR_MODULE_KEY,
    ERROR_MESSAGE_KEY,
    START_ASYNC_EVENT_HANDLERS_ATTR,
    SCENARIO_PATH_KEY,
    SEMVER_MAJOR_KEY,
    MISSING_KEY_MSG,
    VERSION_MISMATCH_MSG,
    SCENARIOS_DIRNAME,
    SNAPSHOTS_DIRNAME,
    REGENERATE_SNAPSHOTS_OPTION,
    GET_ACTIVE_REGISTRY_CONFIG_METHOD,
    NO_REGISTRY_TOOLS_ERROR_MSG,
    CONFIG_KEY,
    REGISTRY_TOOLS_KEY,
    SCENARIO_CONFIG_VERSION_KEY,
    MISMATCH_KEY_MSG,
    VALUE_MISMATCH_MSG,
    VERSION_PARSE_ERROR_MSG,
    YAML_FILE_EXTENSION,
    YAML_PYTHON_NAME_TAG,
    YAML_UNSAFE_LOADER,
)
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync, make_log_context
from omnibase.model.model_scenario import ScenarioConfigModel
from omnibase.enums.metadata import ToolRegistryModeEnum
from omnibase.protocol.protocol_logger import ProtocolLogger
from omnibase.model.model_tool_collection import ToolCollection
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.protocol.protocol_registry_resolver import ProtocolRegistryResolver
# from omnibase.protocol.protocol_testing_scenario_harness import ProtocolTestingScenarioHarness
# NOTE: Do not inherit from ProtocolTestingScenarioHarness (Protocol) due to MRO issues with Generic.

OutputModelT = TypeVar('OutputModelT', bound=BaseModel)

def debug_log(msg, context=None):
    emit_log_event_sync(LogLevelEnum.DEBUG, f"[TestingScenarioHarness] {msg}", context=context or {})

class TestingScenarioHarness(Generic[OutputModelT]):
    def __init__(self, output_model: Type[OutputModelT], registry_resolver: ProtocolRegistryResolver):
        self.output_model = output_model
        self.registry_resolver = registry_resolver
        debug_log(f"Initialized with output_model={output_model}")

    def _compare_outputs(self, output, expected):
        """
        Compare only the fields present in the expected output (partial match).
        Allows for canonical model evolution and extra fields in actual output.
        """
        if isinstance(expected, dict) and isinstance(output, dict):
            for key, value in expected.items():
                if key not in output:
                    return False, f"{MISSING_KEY_MSG} {key}"
                # Recursively compare nested dicts
                if isinstance(value, dict) and isinstance(output[key], dict):
                    match, msg = self._compare_outputs(output[key], value)
                    if not match:
                        return False, f"{MISMATCH_KEY_MSG} {key}: {msg}"
                else:
                    if output[key] != value:
                        return False, f"{VALUE_MISMATCH_MSG} {key}: {output[key]} != {value}"
            return True, ""
        else:
            return output == expected, f"{VALUE_MISMATCH_MSG} {output} != {expected}"

    def _partial_model_compare(self, actual_model, expected_dict):
        """
        Compare only the fields present in the expected dict, using the canonical Pydantic model.
        Handles type coercion (e.g., version string vs. SemVerModel) and nested models.
        """
        for key, expected_value in expected_dict.items():
            if not hasattr(actual_model, key):
                return False, f"{MISSING_KEY_MSG} {key} in actual output model"
            actual_value = getattr(actual_model, key)
            # If expected is a dict and actual is a model, recurse
            if isinstance(expected_value, dict) and hasattr(actual_value, 'model_dump'):
                match, msg = self._partial_model_compare(actual_value, expected_value)
                if not match:
                    return False, f"{MISMATCH_KEY_MSG} {key}: {msg}"
            # If expected is a string and actual is a SemVerModel, coerce and compare
            elif key == VERSION_KEY or key == SEMVER_MAJOR_KEY and hasattr(actual_value, 'major'):
                # Accept both string and dict for version
                from omnibase.model.model_semver import SemVerModel
                try:
                    expected_semver = SemVerModel.parse(expected_value) if isinstance(expected_value, str) else SemVerModel(**expected_value)
                    if actual_value != expected_semver:
                        return False, f"{VERSION_MISMATCH_MSG} {actual_value} != {expected_semver}"
                except Exception as e:
                    return False, f"{VERSION_PARSE_ERROR_MSG} {e}"
            # If expected is a dict and actual is a dict, recurse
            elif isinstance(expected_value, dict) and isinstance(actual_value, dict):
                match, msg = self._partial_model_compare(actual_value, expected_value)
                if not match:
                    return False, f"{MISMATCH_KEY_MSG} {key}: {msg}"
            # If expected is a wildcard string
            elif isinstance(expected_value, str) and expected_value.startswith('*') and expected_value.endswith('*'):
                if expected_value.strip('*') not in str(actual_value):
                    return False, f"{VALUE_MISMATCH_MSG} {key}: {actual_value} does not contain {expected_value.strip('*')}"
            elif isinstance(expected_value, str) and expected_value == '*':
                continue  # Accept any value
            # Otherwise, compare directly
            else:
                if actual_value != expected_value:
                    return False, f"{VALUE_MISMATCH_MSG} {key}: {actual_value} != {expected_value}"
        return True, ""

    async def run_scenario_test(
        self,
        node_class: type,
        scenario_path: str,
        tool_bootstrap: Any,
        tool_backend_selection: Any,
        tool_health_check: Any,
        input_validation_tool: Any,
        output_field_tool: Any,
        config: Any = None,
        async_event_handler_attr: str = START_ASYNC_EVENT_HANDLERS_ATTR,
        output_comparator: Callable = None,
        registry_class: type = None,
        expected_version: str = None,
    ) -> Tuple[Any, Any]:
        """
        Generic scenario test harness for ONEX nodes.
        Requires explicit registry_class and (optionally) expected_version.
        """
        context = {SCENARIO_PATH_KEY: str(scenario_path)}
        with open(scenario_path, "rb") as f:
            scenario_bytes = f.read()
            scenario_hash = hashlib.sha256(scenario_bytes).hexdigest()
        emit_log_event_sync(LogLevelEnum.INFO, f"Scenario hash: {scenario_hash}", context=context)
        scenario = yaml.unsafe_load(scenario_bytes)
        emit_log_event_sync(LogLevelEnum.DEBUG, f"[DEBUG] Parsed scenario YAML: {scenario}", context)
        # Detect scenario format
        is_chain = CHAIN_KEY in scenario and isinstance(scenario[CHAIN_KEY], list)
        is_single = 'input_state' in scenario and 'expected_output' in scenario
        registry = None
        registry_injected = False
        if is_chain:
            config_block = scenario.get(CONFIG_KEY, {})
            actual_version = config_block.get(SCENARIO_CONFIG_VERSION_KEY)
            if not expected_version:
                raise ValueError(f"Scenario config missing required {SCENARIO_CONFIG_VERSION_KEY} field: {scenario_path}")
            if actual_version != expected_version:
                raise ValueError(f"Scenario config version mismatch: expected {expected_version}, got {actual_version} in {scenario_path}")
            try:
                registry = self.registry_resolver.resolve_registry(registry_class, scenario_path=scenario_path)
                registry_injected = True
            except Exception as e:
                debug_log(f"[DEBUG] Could not resolve registry for chain-based scenario {scenario_path}: {e}")
                raise
            chain = scenario.get(CHAIN_KEY, [])
            assert chain, f"{MISSING_KEY_MSG} {CHAIN_KEY} in scenario: {scenario_path}"
            step = chain[0]
            node_name = step[NODE_KEY]
            input_data = step[INPUT_KEY]
            expected = step.get(EXPECT_KEY)
            if expected is None:
                pytest.skip(f"{MISSING_KEY_MSG} '{EXPECT_KEY}' in scenario: {scenario_path}")
        elif is_single:
            input_data = scenario['input_state']
            expected = scenario['expected_output']
            node_name = scenario.get('node_name', 'unknown')
            # For single-step scenarios, try registry, but tolerate failure
            try:
                registry = self.registry_resolver.resolve_registry(registry_class, scenario_path=scenario_path)
                registry_injected = True
            except Exception as e:
                debug_log(f"[DEBUG] No registry_tools found for single-step scenario {scenario_path}: {e}. Proceeding without registry.")
                registry = None
                registry_injected = False
        else:
            raise ValueError(f"Unrecognized scenario format in {scenario_path}")
        # --- Node instantiation with registry injection ---
        node_kwargs = dict(
            tool_bootstrap=tool_bootstrap,
            tool_backend_selection=tool_backend_selection,
            tool_health_check=tool_health_check,
            input_validation_tool=input_validation_tool,
            output_field_tool=output_field_tool,
            config=config,
        )
        import inspect
        node_sig = inspect.signature(node_class)
        if 'registry' in node_sig.parameters and registry_injected:
            node_kwargs['registry'] = registry
        node = node_class(**node_kwargs)
        if async_event_handler_attr and hasattr(node, async_event_handler_attr):
            handler = getattr(node, async_event_handler_attr)
            if asyncio.iscoroutinefunction(handler):
                await handler()
            else:
                handler()
        input_model = getattr(node_class, '__annotations__', {}).get('run', None)
        try:
            if hasattr(node_class, 'run') and hasattr(node_class.run, '__annotations__'):
                input_model_type = node_class.run.__annotations__.get('input_state', None)
                if input_model_type is not None:
                    input_instance = input_model_type(**input_data)
                else:
                    input_instance = input_data
            else:
                input_instance = input_data
            output = node.run(input_instance)
            output = self._make_yaml_safe(output)
            if output_comparator:
                output_comparator(output, expected)
            debug_log(f"Validating output with {self.output_model}", context)
            actual_model = self.output_model.model_validate(output)
            if not isinstance(expected, dict):
                assert actual_model == expected, f"Output mismatch: {actual_model} != {expected}"
            else:
                match, msg = self._partial_model_compare(actual_model, expected)
                assert match, msg
            return output, expected
        except Exception as exc:
            error_output = {
                ERROR_TYPE_KEY: type(exc).__name__,
                ERROR_MODULE_KEY: type(exc).__module__,
                ERROR_MESSAGE_KEY: str(exc),
            }
            if isinstance(exc, (pydantic.ValidationError, getattr(pydantic, 'PydanticUserError', type(None)))):
                error_output["validation_errors"] = exc.errors() if hasattr(exc, 'errors') else None
            error_output = self._make_yaml_safe(error_output)
            debug_log(f"Exception during scenario test: {error_output}", context)
            return error_output, expected

    def _make_yaml_safe(self, obj):
        """
        Recursively convert obj to a YAML-serializable structure (dict, list, str, int, float, bool, None).
        Handles Pydantic models, exceptions, and other common non-serializable types.
        """
        import pydantic
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        if isinstance(obj, dict):
            return {self._make_yaml_safe(k): self._make_yaml_safe(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple, set)):
            return [self._make_yaml_safe(v) for v in obj]
        if hasattr(obj, 'model_dump') and callable(getattr(obj, 'model_dump')):
            return self._make_yaml_safe(obj.model_dump())
        if hasattr(obj, 'dict') and callable(getattr(obj, 'dict')):
            # Fallback for legacy Pydantic v1 models
            return self._make_yaml_safe(obj.dict())
        if isinstance(obj, Exception):
            return {
                ERROR_TYPE_KEY: type(obj).__name__,
                ERROR_MODULE_KEY: type(obj).__module__,
                ERROR_MESSAGE_KEY: str(obj),
            }
        return str(obj)

# Export a default instance for injection/use
# No default export; require explicit injection in test setup

def run_scenario_regression_tests(node_class, registry_class, expected_version=None, config_fixture_name=None):
    """
    Generic scenario regression harness for ONEX nodes.
    Requires explicit registry_class and (optionally) expected_version.
    Discovers all valid scenario YAMLs, parameterizes a test for each, and compares outputs to snapshots.
    Usage (in node test file):
        from omnibase.testing.testing_scenario_harness import run_scenario_regression_tests
        test_scenario_yaml = run_scenario_regression_tests(NodeKafkaEventBus, RegistryNodeKafkaEventBus, expected_version="1.0.0")
    """
    node_module = importlib.import_module(node_class.__module__)
    node_version_dir = Path(node_module.__file__).parent
    scenario_dir = node_version_dir / SCENARIOS_DIRNAME
    snapshot_dir = node_version_dir / SNAPSHOTS_DIRNAME
    snapshot_dir.mkdir(exist_ok=True, parents=True)
    all_paths = list(scenario_dir.glob(f"*{YAML_FILE_EXTENSION}"))

    # Write debug info to a file
    debug_log(f"[DEBUG] node_version_dir: {node_version_dir}")
    debug_log(f"[DEBUG] scenario_dir: {scenario_dir}")
    debug_log(f"[DEBUG] snapshot_dir: {snapshot_dir}")
    debug_log(f"[DEBUG] all_paths: {[str(p) for p in all_paths]}")

    def is_valid_scenario(path):
        try:
            if path.name in ('__init__.py', 'index.yaml'):
                return False
            with open(path, 'r') as f:
                data = yaml.unsafe_load(f)
            # Chain-based scenario
            chain = data.get(CHAIN_KEY, [])
            if chain and isinstance(chain, list):
                step = chain[0]
                if EXPECT_KEY not in step:
                    debug_log(f"[DEBUG] Skipping {path}: no '{EXPECT_KEY}' in first step")
                    return False
                debug_log(f"[DEBUG] Including chain-based scenario: {path}")
                return True
            # Single input/output scenario
            if 'input_state' in data and 'expected_output' in data:
                debug_log(f"[DEBUG] Including single input/output scenario: {path}")
                return True
            debug_log(f"[DEBUG] Skipping {path}: not a recognized scenario format")
            return False
        except Exception as e:
            debug_log(f"[DEBUG] Skipping {path}: exception {e}")
            return False

    scenario_paths = [p for p in all_paths if is_valid_scenario(p)]
    debug_log(f"[DEBUG] scenario_paths (valid): {[str(p) for p in scenario_paths]}")

    def get_snapshot_path(scenario_path):
        scenario_file = Path(scenario_path)
        return snapshot_dir / f"snapshot_{scenario_file.stem}{YAML_FILE_EXTENSION}"

    def load_snapshot(snapshot_path):
        if not snapshot_path.exists():
            return None
        with open(snapshot_path, "r") as f:
            return yaml.unsafe_load(f)

    def save_snapshot(snapshot_path, data):
        with open(snapshot_path, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False)

    @pytest.mark.parametrize(
        "scenario_path",
        [pytest.param(str(p), id=Path(p).name) for p in scenario_paths],
    )
    @pytest.mark.asyncio
    async def test_scenario_yaml(
        scenario_path,
        tool_bootstrap_fixture,
        tool_backend_selection,
        tool_health_check_fixture,
        input_validation_tool,
        output_field_tool,
        scenario_test_harness,
        request,
        **kwargs,
    ):
        config = kwargs.get(config_fixture_name) if config_fixture_name else None
        output, expected = await scenario_test_harness.run_scenario_test(
            node_class=node_class,
            scenario_path=scenario_path,
            tool_bootstrap=tool_bootstrap_fixture,
            tool_backend_selection=tool_backend_selection,
            tool_health_check=tool_health_check_fixture,
            input_validation_tool=input_validation_tool,
            output_field_tool=output_field_tool,
            config=config,
            registry_class=registry_class,
            expected_version=expected_version,
        )
        snapshot_path = get_snapshot_path(scenario_path)
        regenerate = request.config.getoption(REGENERATE_SNAPSHOTS_OPTION) if request else False
        if regenerate or not snapshot_path.exists():
            save_snapshot(snapshot_path, output)
        else:
            snapshot = load_snapshot(snapshot_path)
            assert output == snapshot, f"{VALUE_MISMATCH_MSG} snapshot: {snapshot_path}\nExpected: {snapshot}\nActual: {output}"

    return test_scenario_yaml

def make_testing_scenario_harness(output_model: Type[BaseModel], registry_resolver: ProtocolRegistryResolver):
    return TestingScenarioHarness(output_model, registry_resolver)

# Register a custom constructor for !python/name: tags for ONEX scenario registry_tools compatibility
# This will just return the string value, not resolve to an object

def python_name_constructor(loader, node):
    return loader.construct_scalar(node)

yaml.add_constructor(YAML_PYTHON_NAME_TAG, python_name_constructor, Loader=YAML_UNSAFE_LOADER) 