# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: bce80393-5102-454d-b8ac-2f310f63550b
# name: metadata_constants.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:05.835070
# last_modified_at: 2025-05-19T16:20:05.835072
# description: Stamped Python file: metadata_constants.py
# state_contract: none
# lifecycle: active
# hash: f69cab1f0694a80f4eb3e98b17f5aa7aef3d0ea29cc6133d54babacbdebd8907
# entrypoint: {'type': 'python', 'target': 'metadata_constants.py'}
# namespace: onex.stamped.metadata_constants.py
# meta_type: tool
# === /OmniNode:Metadata ===

# Canonical metadata and schema version constants
METADATA_VERSION = "0.1.0"
SCHEMA_VERSION = "1.1.0"

# Entrypoint type constants (for convenience, but prefer using EntrypointType Enum)
ENTRYPOINT_TYPE_PYTHON = "python"
ENTRYPOINT_TYPE_CLI = "cli"
ENTRYPOINT_TYPE_DOCKER = "docker"

# Canonical metadata block delimiters and config keys for all supported file types

# Python
PY_META_OPEN = "# === OmniNode:Metadata ==="
PY_META_CLOSE = "# === /OmniNode:Metadata ==="

# YAML
YAML_META_OPEN = "# === OmniNode:Metadata ==="
YAML_META_CLOSE = "# === /OmniNode:Metadata ==="

# Markdown
MD_META_OPEN = "<!-- === OmniNode:Metadata ==="
MD_META_CLOSE = "=== /OmniNode:Metadata === -->"

# JSON
JSON_META_OPEN = "// === OmniNode:Metadata ==="
JSON_META_CLOSE = "// === /OmniNode:Metadata ==="

# Config keys
META_TYPE_KEY = "meta_type"
SCHEMA_VERSION_KEY = "schema_version"
METADATA_VERSION_KEY = "metadata_version"
UUID_KEY = "uuid"
NAME_KEY = "name"
VERSION_KEY = "version"
AUTHOR_KEY = "author"
CREATED_AT_KEY = "created_at"
LAST_MODIFIED_AT_KEY = "last_modified_at"
DESCRIPTION_KEY = "description"
STATE_CONTRACT_KEY = "state_contract"
LIFECYCLE_KEY = "lifecycle"
HASH_KEY = "hash"
ENTRYPOINT_KEY = "entrypoint"
NAMESPACE_KEY = "namespace"
