# Project-level canonical constants for ONEX/OmniBase
# Use these for protocol-wide, cross-node, cross-tool values

ONEX_CANONICAL_SCENARIO_PASS_MSG = "All scenarios passed."
ONEX_CANONICAL_SCENARIO_FAIL_MSG = "One or more scenarios failed."

# === Generic config keys ===
CONFIG_KEY = "config"
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
CONTRACT_FILENAME = "contract.yaml"
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
