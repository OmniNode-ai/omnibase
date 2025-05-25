# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: constants.py
# version: 1.0.0
# uuid: f6b996f0-4269-4a4d-8744-69b592d280b9
# author: OmniNode Team
# created_at: 2025-05-24T12:24:48.694116
# last_modified_at: 2025-05-24T16:48:46.753191
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 9fb555b3d2f9630ded55e94fc6dbf75caa952a02fa96b760110f4ffd68161d38
# entrypoint: python@constants.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.constants
# meta_type: tool
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Constants for tree generator node.
Centralizes all string literals, messages, and configuration values.
"""

# Status constants
STATUS_SUCCESS = "success"
STATUS_ERROR = "failure"

# Message templates
MSG_SUCCESS_TEMPLATE = "Successfully generated .onextree manifest at {path}"
MSG_ERROR_DIRECTORY_NOT_FOUND = "Root directory does not exist: {path}"
MSG_ERROR_PERMISSION_DENIED = "Permission denied accessing directory: {path}"
MSG_ERROR_OUTPUT_PATH_INVALID = "Invalid output path: {path}"
MSG_ERROR_UNKNOWN = "Unknown error occurred during tree generation: {error}"

# File and directory constants
DEFAULT_OUTPUT_FILENAME = ".onextree"
HIDDEN_FILES_TO_INCLUDE = {".onexignore", ".wip"}
HIDDEN_DIRS_TO_EXCLUDE = {".git", "__pycache__", ".pytest_cache"}

# Node metadata
NODE_NAME = "tree_generator_node"
NODE_VERSION = "1.0.0"

# Event types
EVENT_NODE_START = "NODE_START"
EVENT_NODE_SUCCESS = "NODE_SUCCESS"
EVENT_NODE_FAILURE = "NODE_FAILURE"

# Validation constants
MIN_ARTIFACTS_FOR_WARNING = 0
MAX_VALIDATION_ERRORS_TO_DISPLAY = 10
