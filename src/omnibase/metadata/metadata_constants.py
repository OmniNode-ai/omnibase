# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 148849d9-ad4b-465b-b22d-0ff42521bebc
# name: metadata_constants.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-18T12:37:27.385822
# last_modified_at: 2025-05-18T12:37:27.385824
# description: Stamped Python file: metadata_constants.py
# state_contract: none
# lifecycle: active
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# entrypoint: {'type': 'python', 'target': 'metadata_constants.py'}
# namespace: onex.stamped.metadata_constants.py
# meta_type: tool
# === /OmniNode:Metadata ===

# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 12326d3b-6a2f-4dc5-be78-1ab59ec7c464
# name: metadata_constants.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-18T12:35:25.827961
# last_modified_at: 2025-05-18T12:35:25.827962
# description: Stamped Python file: metadata_constants.py
# state_contract: none
# lifecycle: active
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# entrypoint: {'type': 'python', 'target': 'metadata_constants.py'}
# namespace: onex.stamped.metadata_constants.py
# meta_type: tool
# === /OmniNode:Metadata ===

# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 72e604a9-0a15-43a9-83ec-1de10f8a1b81
# name: metadata_constants.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-18T12:33:36.365243
# last_modified_at: 2025-05-18T12:33:36.365245
# description: Stamped Python file: metadata_constants.py
# state_contract: none
# lifecycle: active
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# entrypoint: {'type': 'python', 'target': 'metadata_constants.py'}
# namespace: onex.stamped.metadata_constants.py
# meta_type: tool
# === /OmniNode:Metadata ===

# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 44826d65-f604-4f3d-b463-6be18e746c40
# name: metadata_constants.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-18T12:32:45.779997
# last_modified_at: 2025-05-18T12:32:45.779998
# description: Stamped Python file: metadata_constants.py
# state_contract: none
# lifecycle: active
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# entrypoint: {'type': 'python', 'target': 'metadata_constants.py'}
# namespace: onex.stamped.metadata_constants.py
# meta_type: tool
# === /OmniNode:Metadata ===

# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: <to-be-generated>
# name: metadata_constants.py
# version: 1.0.0
# author: OmniNode Team
# created_at: <to-be-generated>
# last_modified_at: <to-be-generated>
# description: Canonical constants for metadata and schema versions, and entrypoint types.
# state_contract: none
# lifecycle: active
# hash: 0000000000000000000000000000000000000000000000000000000000000000
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
