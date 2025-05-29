# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.979663'
# description: Stamped by PythonHandler
# entrypoint: python://constants.py
# hash: a74d003d0e5bb86147f46fc5b75be1cde73e1638c2657a761101e60e681f0843
# last_modified_at: '2025-05-29T11:50:11.950478+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: constants.py
# namespace: omnibase.constants
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 502281c0-f119-4c0f-8bd7-43a3b9fc82eb
# version: 1.0.0
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
