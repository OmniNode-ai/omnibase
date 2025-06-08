# Project-level canonical constants for ONEX/OmniBase
# Use these for protocol-wide, cross-node, cross-tool values

import yaml

ONEX_CANONICAL_SCENARIO_PASS_MSG = "All scenarios passed."
ONEX_CANONICAL_SCENARIO_FAIL_MSG = "One or more scenarios failed."

# === Generic config keys ===
CONFIG_KEY = "config"
REGISTRY_TOOLS_KEY = "registry_tools"
SCENARIO_CONFIG_VERSION_KEY = "scenario_config_version"
ARGS_KEY = "args"
LOG_FORMAT_KEY = "log_format"
MESSAGE_KEY = "message"
RESULT_KEY = "result"
CUSTOM_KEY = "custom"
INTEGRATION_KEY = "integration"
PROCESSED_KEY = "processed"
VERSION_KEY = "version"
BACKEND_KEY = "backend"

# === Argument flags ===
BOOTSTRAP_ARG = "--bootstrap"
HEALTH_CHECK_ARG = "--health-check"
DEBUG_TRACE_ARG = "--debug-trace"

# === Log format ===
LOG_FORMAT_JSON = "json"

# === Protocol/event types ===
ENDPOINT_UNKNOWN = "unknown"
NODE_ANNOUNCE_EVENT = "NODE_ANNOUNCE"
STRUCTURED_LOG_EVENT = "STRUCTURED_LOG"
TOOL_PROXY_INVOKE_EVENT = "TOOL_PROXY_INVOKE"
TOOL_PROXY_RESULT_EVENT = "TOOL_PROXY_RESULT"

# === Misc ===
DEFAULT_PROCESSED_VALUE = "test"
HEALTH_CHECK_RESULT_PREFIX = "[HEALTH CHECK RESULT]"
NODE_METADATA_FILENAME = "node.onex.yaml"
CONTRACT_FILENAME = "node.onex.yaml"
SCENARIOS_INDEX_FILENAME = "index.yaml"
SCENARIOS_DIRNAME = "scenarios"

# === New constants ===
ONEX_TRACE_ENV_KEY = "ONEX_TRACE"
BUS_ID_KEY = "bus_id"
STATUS_KEY = "status"
SCENARIOS_KEY = "scenarios"
STATUS_OK_VALUE = "ok"
INPUT_VALIDATION_SUCCEEDED_MSG = "Input validation succeeded"
CUSTOM_OUTPUT_INPUT_VALUE = "custom_output"
CUSTOM_OUTPUT_VALUE = "output"
TEST_INPUT_VALUE = "test"
OPTIONAL_INPUT_VALUE = "optional"
OPTIONAL_FIELD_KEY = "optional_field"
OUTPUT_FIELD_KEY = "output_field"
EXTERNAL_DEPENDENCY_KEY = "external_dependency"
SCENARIOS_FIELD = "scenarios"

# === Error keys ===
ERROR_TYPE_KEY = "type"
ERROR_LOC_KEY = "loc"
ERROR_MSG_KEY = "msg"
BACKEND_ERROR_VALUE = "error"
ERROR_TYPE_MISSING_VALUE = "missing"
VALIDATION_ERROR_LOG_PREFIX = "ValidationError in run:"
EXCEPTION_ERROR_LOG_PREFIX = "Exception in run:"

# === New constants ===
ERROR_TYPE_MISSING_VALUE = "missing"
VALIDATION_ERROR_LOG_PREFIX = "ValidationError in run:"
EXCEPTION_ERROR_LOG_PREFIX = "Exception in run:"

# Canonical event bus input field keys
INPUT_FIELD_KEY = "input_field"

# === Canonical Scenario Input Keys (shared across all ONEX nodes) ===
# Use these for scenario-driven node logic and tests.
TEST_DEGRADED = "test_degraded"
TEST_BOOTSTRAP = "test_bootstrap"
TEST_CHAIN = "test_chain"
TEST_MULTI = "test_multi"
TEST_INTROSPECT = "test_introspect"
TEST_HEALTH = "test_health"
TEST_ASYNC_HANDLER = "test_async_handler"
TEST = "test"

# === Canonical CLI Argument Flags (shared across all ONEX nodes) ===
from enum import Enum
class NodeArgEnum(str, Enum):
    """Canonical CLI argument flags for ONEX nodes."""
    BOOTSTRAP = "--bootstrap"
    HEALTH_CHECK = "--health-check"
    INTROSPECT = "--introspect"

# === Canonical Model/Event Field Keys ===
EVENT_TYPE_KEY = "event_type"  # Used in OnexEvent and protocol messages
CORRELATION_ID_KEY = "correlation_id"  # Used for distributed tracing and event correlation
BOOTSTRAP_SERVERS_KEY = "bootstrap_servers"  # Used in event bus/Kafka config

# === Canonical Protocol Method Names ===
PUBLISH_ASYNC_METHOD = "publish_async"  # Used for protocol reflection/introspection

# === Canonical Error Messages ===
FIELD_REQUIRED_ERROR_MSG = "Field required"  # Used for missing/invalid required fields

# === Canonical Debug/CLI Args and Markers ===
DEBUG_TRACE_ARG = "--debug-trace"  # Used for enabling trace mode via CLI
UNREACHABLE_SERVER_MARKER = "unreachable"  # Used to simulate unreachable Kafka server in degraded mode tests

# === Protocol-wide Input Validation Error Messages ===
INPUT_MISSING_REQUIRED_FIELD_ERROR = "Input is missing a required field."
INPUT_REQUIRED_FIELD_ERROR_TEMPLATE = "Input is missing required field: {missing_field}"

# === Canonical Filenames and Scenario/Test Keys ===
CONTRACT_FILENAME = "node.onex.yaml"
SCENARIOS_DIRNAME = "scenarios"
SCENARIO_FILE_GLOB = "scenario_*.yaml"
NODE_KEY = "node"
INPUT_KEY = "input"
EXPECT_KEY = "expect"
VERSION_KEY = "version"
MESSAGE_KEY = "message"
FIELD_REQUIRED_ERROR_MSG = "Field required"
BACKEND_KEY = "backend"
ERROR_VALUE = "error"

# === Canonical Test/Scenario Harness Constants ===
START_ASYNC_EVENT_HANDLERS_ATTR = "start_async_event_handlers"
SCENARIO_PATH_KEY = "scenario_path"
SCENARIO_ID_KEY = "scenario_id"
SCENARIO_HASH_KEY = "scenario_hash"
SEMVER_MAJOR_KEY = "major"
MISSING_KEY_MSG = "Missing key:"
VERSION_MISMATCH_MSG = "Version mismatch:"
CHAIN_KEY = "chain"
ERROR_TYPE_KEY = "error_type"
ERROR_MODULE_KEY = "error_module"
ERROR_MESSAGE_KEY = "message"
SNAPSHOTS_DIRNAME = "snapshots"
REGENERATE_SNAPSHOTS_OPTION = "--regenerate-snapshots"

# === New constants ===
ENTRYPOINT_KEY = "entrypoint"
STORE_TRUE = "store_true"
SERVE_ARG = "--serve"
SERVE_ASYNC_ARG = "--serve-async"
DRY_RUN_ARG = "--dry-run"
MAIN_MODULE_NAME = "__main__"

# === New constants ===
ERROR_KEY = "error"
NODE_ID_KEY = "node_id"
NODE_NAME_KEY = "node_name"
NODE_VERSION_KEY = "node_version"

# === New constants ===
BACKEND_SELECTION_KEY = "backend_selection"
INPUT_VALIDATION_KEY = "input_validation"
OUTPUT_FIELD_KEY = "output_field"
BOOTSTRAP_KEY = "bootstrap"
HEALTH_CHECK_KEY = "health_check"
NODE_TEMPLATE_ID = "node_template"

# === New constants ===
EVENT_ID_KEY = "event_id"
TIMESTAMP_KEY = "timestamp"

# === New constants ===
KAFKA_KEY = "kafka"
INMEMORY_KEY = "inmemory"

# === Canonical Method Names ===
GET_ACTIVE_REGISTRY_CONFIG_METHOD = "get_active_registry_config"  # Used for scenario registry config selection

# === Canonical Error Messages ===
NO_REGISTRY_TOOLS_ERROR_MSG = "No registry_tools or registry_configs found in scenario config."  # Used for scenario registry config validation

# === New constants ===
MISMATCH_KEY_MSG = "Mismatch in key:"
VALUE_MISMATCH_MSG = "Value mismatch:"
VERSION_PARSE_ERROR_MSG = "Version parse error:"

YAML_FILE_EXTENSION = '.yaml'

YAML_PYTHON_NAME_TAG = '!python/name:'
YAML_UNSAFE_LOADER = yaml.UnsafeLoader
