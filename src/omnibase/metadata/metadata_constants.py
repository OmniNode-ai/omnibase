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

"""
Canonical ONEX metadata and protocol/config constants.

This file is the single source of truth for all ONEX-wide protocol/config values, including:
- Ignore pattern filenames and directory names (used by all nodes/tools)
- Config keys for metadata blocks and project-level config
- Canonical filenames for project and protocol files
- Metadata block delimiters for all supported file types

All constants here are intended for import by any ONEX tool, node, or test that needs protocol/config values.
Version: 1.0.0 (increment with any breaking/additive changes)

# === Protocol-Critical Values ===

- METADATA_FILE_NODE: Canonical filename for node metadata ("node.onex.yaml")
- METADATA_FILE_CLI_TOOL: Canonical filename for CLI tool metadata ("cli_tool.yaml")
- METADATA_FILE_RUNTIME: Canonical filename for runtime metadata ("runtime.yaml")
- METADATA_FILE_ADAPTER: Canonical filename for adapter metadata ("adapter.yaml")
- METADATA_FILE_CONTRACT: Canonical filename for contract metadata ("contract.yaml")
- METADATA_FILE_PACKAGE: Canonical filename for package metadata ("package.yaml")
- DEFAULT_OUTPUT_FILENAME: Canonical default output filename for ONEX tree manifests (".onextree")
- ONEXIGNORE_FILENAME: Canonical filename for ONEX ignore patterns (".onexignore")
- WIP_DIRNAME: Canonical directory name for work-in-progress files (".wip")
- PYCACHE_DIRNAME: Canonical directory name for Python cache ("__pycache__")
- DEFAULT_ONEX_IGNORE_PATTERNS: Canonical default ignore patterns for ONEX tools
- PROJECT_ONEX_YAML_FILENAME: Canonical filename for project-level ONEX config
- [Other config keys]: See below for canonical config key constants

All ONEX nodes/tools MUST use these values for protocol compliance.
"""

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

# Project-level and protocol/config keys
PROJECT_ONEX_YAML_FILENAME = "project.onex.yaml"
ENTRYPOINT_KEY = "entrypoint"
TOOLS_KEY = "tools"
NAMESPACE_KEY = "namespace"
METADATA_VERSION_KEY = "metadata_version"
PROTOCOL_VERSION_KEY = "protocol_version"
SCHEMA_VERSION_KEY = "schema_version"
COPYRIGHT_KEY = "copyright"
NAME_KEY = "name"
AUTHOR_KEY = "author"
DESCRIPTION_KEY = "description"
LIFECYCLE_KEY = "lifecycle"
LICENSE_KEY = "license"
CREATED_AT_KEY = "created_at"
LAST_MODIFIED_AT_KEY = "last_modified_at"

# Canonical filenames and directory names used across ONEX tools
ONEXIGNORE_FILENAME = ".onexignore"
WIP_DIRNAME = ".wip"
PYCACHE_DIRNAME = "__pycache__"

# Canonical default ignore patterns for ONEX tools (used if no config is present)
DEFAULT_ONEX_IGNORE_PATTERNS = [
    ONEXIGNORE_FILENAME,
    WIP_DIRNAME,
    PYCACHE_DIRNAME,
]

# Canonical metadata file names for ONEX artifact types (used by all nodes/tools)
METADATA_FILE_NODE = "node.onex.yaml"
METADATA_FILE_CLI_TOOL = "cli_tool.yaml"
METADATA_FILE_RUNTIME = "runtime.yaml"
METADATA_FILE_ADAPTER = "adapter.yaml"
METADATA_FILE_CONTRACT = "contract.yaml"
METADATA_FILE_PACKAGE = "package.yaml"

# Canonical default output filename for ONEX tree manifests
DEFAULT_OUTPUT_FILENAME = ".onextree"
