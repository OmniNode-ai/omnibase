# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode.ai
# schema_version: 0.1.0
# name: metadata_constants.py
# version: 1.0.0
# uuid: 9c02cda0-ee63-4d2c-8cb3-42bb8b62b7c3
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.164312
# last_modified_at: 2025-05-21T16:42:46.129813
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: e967cdf8c53c40b17dc19a456e58a4907d4e3f3261f77d0c08a179d89e736fd0
# entrypoint: python@metadata_constants.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.metadata_constants
# meta_type: tool
# === /OmniNode:Metadata ===

import os

# Canonical metadata and schema version constants
METADATA_VERSION = "0.1.0"
SCHEMA_VERSION = "1.1.0"


def get_namespace_prefix() -> str:
    """
    Return the canonical namespace prefix for this codebase.
    Checks environment variable OMNINODE_NAMESPACE_PREFIX, then config, then defaults to 'omnibase'.
    """
    return os.environ.get("OMNINODE_NAMESPACE_PREFIX", "omnibase")


# Entrypoint type constants (for convenience, but prefer using EntrypointType Enum)
ENTRYPOINT_TYPE_PYTHON = "python"
ENTRYPOINT_TYPE_CLI = "cli"
ENTRYPOINT_TYPE_DOCKER = "docker"

# Canonical metadata block delimiters and config keys for all supported file types

# Python
PY_META_OPEN = "# === OmniNode:Metadata ==="
PY_META_CLOSE = "# === /OmniNode:Metadata ==="

# YAML
YAML_META_OPEN = "---"
YAML_META_CLOSE = "..."

# Markdown
MD_META_OPEN = "<!-- === OmniNode:Metadata ==="
MD_META_CLOSE = "<!-- === /OmniNode:Metadata === -->"

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
