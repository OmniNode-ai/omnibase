# === Node Protocol Constants (ONEX Standard) ===
# Centralized constants for node metadata keys, CLI argument names, handler names, extensions, and error messages.
# Import this module in all node implementations and tests to ensure protocol consistency.

from omnibase.enums import NodeStatusEnum

# --- Metadata Keys ---
NODE_ID = "node_id"
REGISTRY_ID = "registry_id"
TRUST_STATE = "trust_state"
TTL = "ttl"
REASON = "reason"
METADATA_BLOCK = "metadata_block"
INPUTS = "inputs"
OUTPUTS = "outputs"
GRAPH_BINDING = "graph_binding"
# STATUS: Use NodeStatusEnum for all status values

# --- CLI Argument Names ---
ARG_ACTION = "action"
ARG_NODE_ID = "--node-id"
ARG_INTROSPECT = "--introspect"

# --- Handler/Test Names (shared with tests) ---
TEST_HANDLER_NAME = "TestHandler"
NAMED_HANDLER_NAME = "NamedHandler"
AUTO_HANDLER_NAME = "AutoHandler"
LOW_PRIORITY_HANDLER = "LowPriority"
HIGH_PRIORITY_HANDLER = "HighPriority"
ORIGINAL_HANDLER = "Original"
OVERRIDE_HANDLER = "Override"
SPECIAL_HANDLER = "SpecialHandler"

# --- File Extensions (shared with tests) ---
TEST_EXTENSION = ".test"
AUTO_EXTENSION = ".auto"
CONFLICT_EXTENSION = ".conflict"
SPECIAL_CONFIG = "special.config"

# --- Named Handler Keys (shared with tests) ---
MY_PROCESSOR = "my_processor"
NAMED1 = "named1"

# --- Special Handler Keys (shared with tests) ---
SPECIAL1 = "special1"

# --- Error Messages (shared) ---
ERR_MISSING_NODE_ID = "Missing or empty node_id in NODE_ANNOUNCE event"
ERR_NODE_NOT_FOUND = "Node {node_id} not found in registry."
ERR_UNKNOWN_ACTION = "Unknown action: {action}"

# --- Test/Protocol Argument Keys and Values ---
SOURCE_TEST = "test"
SOURCE_CORE = "core"
SOURCE_PLUGIN = "plugin"
SOURCE_RUNTIME = "runtime"
HANDLER_ARG_CUSTOM_PARAM = "custom_param"
HANDLER_ARG_TEST_VALUE = "test_value"
HANDLER_TYPE_EXTENSION = "extension"
HANDLER_TYPE_NAMED = "named"
HANDLER_TYPE_SPECIAL = "special"

# Add more as needed for protocol evolution 