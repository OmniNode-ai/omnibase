# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.979663'
# description: Stamped by PythonHandler
# entrypoint: python://constants
# hash: fb5d5df3544110bafbf8dd7d4b0fc6b17a0ee8f089ae83e32d9a459cac5bf21e
# last_modified_at: '2025-05-29T14:14:00.089162+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: constants.py
# namespace: python://omnibase.nodes.node_tree_generator.v1_0_0.constants
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
Node-specific constants for the tree generator node.

This file should only contain values unique to this node. All protocol-wide constants (status values, artifact type names, metadata file names, event types, default output filename) are now centralized in shared files:
- Status, artifact types: omnibase.enums
- Metadata file names, output filename: omnibase.metadata.metadata_constants
- Event types: (TODO: centralize if needed)

Version: 1.0.0 (increment with any breaking/additive changes)

# === Node-Specific Constants ===

- MSG_SUCCESS_TEMPLATE: Success message template for manifest generation
- MSG_ERROR_DIRECTORY_NOT_FOUND: Error message for missing root directory
- MSG_ERROR_PERMISSION_DENIED: Error message for directory permission issues
- MSG_ERROR_OUTPUT_PATH_INVALID: Error message for invalid output path
- MSG_ERROR_UNKNOWN: Fallback error message for unknown errors
- MIN_ARTIFACTS_FOR_WARNING: Minimum artifact count before warning is triggered
- MAX_VALIDATION_ERRORS_TO_DISPLAY: Max number of validation errors to display in output
- NODE_NAME: Name of this node (for logging/metadata)
- NODE_VERSION: Version of this node (for logging/metadata)

These constants are unique to the tree generator node and should not be imported by other nodes/tools.
"""

# Message templates (node-specific)
MSG_SUCCESS_TEMPLATE = "Successfully generated .onextree manifest at {path}"
MSG_ERROR_DIRECTORY_NOT_FOUND = "Root directory does not exist: {path}"
MSG_ERROR_PERMISSION_DENIED = "Permission denied accessing directory: {path}"
MSG_ERROR_OUTPUT_PATH_INVALID = "Invalid output path: {path}"
MSG_ERROR_UNKNOWN = "Unknown error occurred during tree generation: {error}"

# Validation constants (node-specific)
MIN_ARTIFACTS_FOR_WARNING = 0
MAX_VALIDATION_ERRORS_TO_DISPLAY = 10

# Node metadata (node-specific)
NODE_NAME = "node_tree_generator"
NODE_VERSION = "1.0.0"
