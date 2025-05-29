# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T09:34:52.829521'
# description: Stamped by PythonHandler
# entrypoint: python://error_codes
# hash: 7129aa3830ffd059231a4dd7316d7e9e44190770865e67738c4788e350c4b385
# last_modified_at: '2025-05-29T14:13:59.333515+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: error_codes.py
# namespace: python://omnibase.nodes.node_manager_node.v1_0_0.error_codes
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: cab3acb8-2693-405a-8a61-6c6ae90b0966
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Error codes and exit code mapping for node_manager_node.

This module defines canonical error codes for the node manager node and provides
mapping functionality to convert OnexStatus values to appropriate CLI exit codes.

Exit Code Conventions:
- 0: Success (OnexStatus.SUCCESS)
- 1: General error (OnexStatus.ERROR, OnexStatus.UNKNOWN)
- 2: Warning (OnexStatus.WARNING)
- 3: Partial success (OnexStatus.PARTIAL)
- 4: Skipped (OnexStatus.SKIPPED)
- 5: Fixed (OnexStatus.FIXED)
- 6: Info (OnexStatus.INFO)

Error Code Format: ONEX_NODE_MANAGER_<NUMBER>_<DESCRIPTION>
"""

import re
from typing import Any, Dict

from omnibase.core.core_error_codes import (
    CLIExitCode,
    OnexError,
    OnexErrorCode,
    register_error_codes,
)


class NodeManagerErrorCode(OnexErrorCode):
    """Canonical error codes for node manager operations."""

    # Input validation errors (001-020)
    INVALID_NODE_NAME = "ONEX_NODE_MANAGER_001_INVALID_NODE_NAME"
    MISSING_REQUIRED_FIELD = "ONEX_NODE_MANAGER_002_MISSING_REQUIRED_FIELD"
    INVALID_TEMPLATE_SOURCE = "ONEX_NODE_MANAGER_003_INVALID_TEMPLATE_SOURCE"
    INVALID_TARGET_DIRECTORY = "ONEX_NODE_MANAGER_004_INVALID_TARGET_DIRECTORY"
    INVALID_OPERATION = "ONEX_NODE_MANAGER_005_INVALID_OPERATION"

    # Template processing errors (021-040)
    TEMPLATE_NOT_FOUND = "ONEX_NODE_MANAGER_021_TEMPLATE_NOT_FOUND"
    TEMPLATE_COPY_FAILED = "ONEX_NODE_MANAGER_022_TEMPLATE_COPY_FAILED"
    TEMPLATE_PROCESSING_FAILED = "ONEX_NODE_MANAGER_023_TEMPLATE_PROCESSING_FAILED"
    PLACEHOLDER_REPLACEMENT_FAILED = "ONEX_NODE_MANAGER_024_PLACEHOLDER_REPLACEMENT_FAILED"

    # File operation errors (041-060)
    FILE_CREATION_FAILED = "ONEX_NODE_MANAGER_041_FILE_CREATION_FAILED"
    DIRECTORY_CREATION_FAILED = "ONEX_NODE_MANAGER_042_DIRECTORY_CREATION_FAILED"
    FILE_WRITE_FAILED = "ONEX_NODE_MANAGER_043_FILE_WRITE_FAILED"
    PERMISSION_DENIED = "ONEX_NODE_MANAGER_044_PERMISSION_DENIED"
    BACKUP_FAILED = "ONEX_NODE_MANAGER_045_BACKUP_FAILED"

    # Validation errors (061-080)
    NODE_VALIDATION_FAILED = "ONEX_NODE_MANAGER_061_NODE_VALIDATION_FAILED"
    MISSING_REQUIRED_FILES = "ONEX_NODE_MANAGER_062_MISSING_REQUIRED_FILES"
    INVALID_NODE_STRUCTURE = "ONEX_NODE_MANAGER_063_INVALID_NODE_STRUCTURE"
    PARITY_VALIDATION_FAILED = "ONEX_NODE_MANAGER_064_PARITY_VALIDATION_FAILED"

    # Generation errors (081-100)
    STAMPING_FAILED = "ONEX_NODE_MANAGER_081_STAMPING_FAILED"
    ONEXTREE_GENERATION_FAILED = "ONEX_NODE_MANAGER_082_ONEXTREE_GENERATION_FAILED"
    NODE_ALREADY_EXISTS = "ONEX_NODE_MANAGER_083_NODE_ALREADY_EXISTS"
    CLEANUP_FAILED = "ONEX_NODE_MANAGER_084_CLEANUP_FAILED"

    # Maintenance errors (101-120)
    CONTRACT_REGENERATION_FAILED = "ONEX_NODE_MANAGER_101_CONTRACT_REGENERATION_FAILED"
    MANIFEST_REGENERATION_FAILED = "ONEX_NODE_MANAGER_102_MANIFEST_REGENERATION_FAILED"
    NODE_HEALTH_CHECK_FAILED = "ONEX_NODE_MANAGER_103_NODE_HEALTH_CHECK_FAILED"
    CONFIG_SYNCHRONIZATION_FAILED = "ONEX_NODE_MANAGER_104_CONFIG_SYNCHRONIZATION_FAILED"
    NODE_NOT_FOUND = "ONEX_NODE_MANAGER_105_NODE_NOT_FOUND"

    def get_component(self) -> str:
        """Get the component identifier for this error code."""
        return "NODE_MANAGER"

    def get_number(self) -> int:
        """Get the numeric identifier for this error code."""
        # Extract number from error code string (e.g., "ONEX_NODE_MANAGER_001_..." -> 1)
        match = re.search(r"ONEX_NODE_MANAGER_(\d+)_", self.value)
        return int(match.group(1)) if match else 0

    def get_description(self) -> str:
        """Get a human-readable description for this error code."""
        return get_error_description(self)

    def get_exit_code(self) -> int:
        """Get the appropriate CLI exit code for this error."""
        return get_exit_code_for_error(self)


# Mapping from error codes to exit codes (for specific error handling)
ERROR_CODE_TO_EXIT_CODE: Dict[NodeManagerErrorCode, CLIExitCode] = {
    # Input validation errors -> ERROR
    NodeManagerErrorCode.INVALID_NODE_NAME: CLIExitCode.ERROR,
    NodeManagerErrorCode.MISSING_REQUIRED_FIELD: CLIExitCode.ERROR,
    NodeManagerErrorCode.INVALID_TEMPLATE_SOURCE: CLIExitCode.ERROR,
    NodeManagerErrorCode.INVALID_TARGET_DIRECTORY: CLIExitCode.ERROR,
    NodeManagerErrorCode.INVALID_OPERATION: CLIExitCode.ERROR,
    # Template processing errors -> ERROR
    NodeManagerErrorCode.TEMPLATE_NOT_FOUND: CLIExitCode.ERROR,
    NodeManagerErrorCode.TEMPLATE_COPY_FAILED: CLIExitCode.ERROR,
    NodeManagerErrorCode.TEMPLATE_PROCESSING_FAILED: CLIExitCode.ERROR,
    NodeManagerErrorCode.PLACEHOLDER_REPLACEMENT_FAILED: CLIExitCode.ERROR,
    # File operation errors -> ERROR
    NodeManagerErrorCode.FILE_CREATION_FAILED: CLIExitCode.ERROR,
    NodeManagerErrorCode.DIRECTORY_CREATION_FAILED: CLIExitCode.ERROR,
    NodeManagerErrorCode.FILE_WRITE_FAILED: CLIExitCode.ERROR,
    NodeManagerErrorCode.PERMISSION_DENIED: CLIExitCode.ERROR,
    NodeManagerErrorCode.BACKUP_FAILED: CLIExitCode.WARNING,
    # Validation errors -> WARNING (may be recoverable)
    NodeManagerErrorCode.NODE_VALIDATION_FAILED: CLIExitCode.WARNING,
    NodeManagerErrorCode.MISSING_REQUIRED_FILES: CLIExitCode.WARNING,
    NodeManagerErrorCode.INVALID_NODE_STRUCTURE: CLIExitCode.WARNING,
    NodeManagerErrorCode.PARITY_VALIDATION_FAILED: CLIExitCode.WARNING,
    # Generation errors -> mixed
    NodeManagerErrorCode.STAMPING_FAILED: CLIExitCode.WARNING,
    NodeManagerErrorCode.ONEXTREE_GENERATION_FAILED: CLIExitCode.WARNING,
    NodeManagerErrorCode.NODE_ALREADY_EXISTS: CLIExitCode.ERROR,
    NodeManagerErrorCode.CLEANUP_FAILED: CLIExitCode.WARNING,
    # Maintenance errors -> WARNING (may be partially recoverable)
    NodeManagerErrorCode.CONTRACT_REGENERATION_FAILED: CLIExitCode.WARNING,
    NodeManagerErrorCode.MANIFEST_REGENERATION_FAILED: CLIExitCode.WARNING,
    NodeManagerErrorCode.NODE_HEALTH_CHECK_FAILED: CLIExitCode.WARNING,
    NodeManagerErrorCode.CONFIG_SYNCHRONIZATION_FAILED: CLIExitCode.WARNING,
    NodeManagerErrorCode.NODE_NOT_FOUND: CLIExitCode.ERROR,
}


def get_exit_code_for_error(error_code: NodeManagerErrorCode) -> int:
    """
    Get the appropriate CLI exit code for a specific error code.

    Args:
        error_code: The NodeManagerErrorCode to map

    Returns:
        The corresponding CLI exit code (integer)

    Example:
        >>> get_exit_code_for_error(NodeManagerErrorCode.INVALID_NODE_NAME)
        1
        >>> get_exit_code_for_error(NodeManagerErrorCode.STAMPING_FAILED)
        2
    """
    return ERROR_CODE_TO_EXIT_CODE.get(error_code, CLIExitCode.ERROR).value


def get_error_description(error_code: NodeManagerErrorCode) -> str:
    """
    Get a human-readable description for an error code.

    Args:
        error_code: The NodeManagerErrorCode to describe

    Returns:
        A human-readable description of the error
    """
    descriptions = {
        NodeManagerErrorCode.INVALID_NODE_NAME: "Invalid node name format",
        NodeManagerErrorCode.MISSING_REQUIRED_FIELD: "Missing required field",
        NodeManagerErrorCode.INVALID_TEMPLATE_SOURCE: "Invalid template source",
        NodeManagerErrorCode.INVALID_TARGET_DIRECTORY: "Invalid target directory",
        NodeManagerErrorCode.INVALID_OPERATION: "Invalid or unsupported operation",
        NodeManagerErrorCode.TEMPLATE_NOT_FOUND: "Template source not found",
        NodeManagerErrorCode.TEMPLATE_COPY_FAILED: "Failed to copy template structure",
        NodeManagerErrorCode.TEMPLATE_PROCESSING_FAILED: "Template processing failed",
        NodeManagerErrorCode.PLACEHOLDER_REPLACEMENT_FAILED: "Placeholder replacement failed",
        NodeManagerErrorCode.FILE_CREATION_FAILED: "File creation failed",
        NodeManagerErrorCode.DIRECTORY_CREATION_FAILED: "Directory creation failed",
        NodeManagerErrorCode.FILE_WRITE_FAILED: "File write operation failed",
        NodeManagerErrorCode.PERMISSION_DENIED: "Permission denied for file operation",
        NodeManagerErrorCode.BACKUP_FAILED: "Backup creation failed",
        NodeManagerErrorCode.NODE_VALIDATION_FAILED: "Node validation failed",
        NodeManagerErrorCode.MISSING_REQUIRED_FILES: "Missing required node files",
        NodeManagerErrorCode.INVALID_NODE_STRUCTURE: "Invalid node directory structure",
        NodeManagerErrorCode.PARITY_VALIDATION_FAILED: "Parity validation failed",
        NodeManagerErrorCode.STAMPING_FAILED: "File stamping failed",
        NodeManagerErrorCode.ONEXTREE_GENERATION_FAILED: ".onextree generation failed",
        NodeManagerErrorCode.NODE_ALREADY_EXISTS: "Node already exists at target location",
        NodeManagerErrorCode.CLEANUP_FAILED: "Cleanup operation failed",
        NodeManagerErrorCode.CONTRACT_REGENERATION_FAILED: "Contract regeneration failed",
        NodeManagerErrorCode.MANIFEST_REGENERATION_FAILED: "Manifest regeneration failed",
        NodeManagerErrorCode.NODE_HEALTH_CHECK_FAILED: "Node health check failed",
        NodeManagerErrorCode.CONFIG_SYNCHRONIZATION_FAILED: "Configuration synchronization failed",
        NodeManagerErrorCode.NODE_NOT_FOUND: "Node not found at specified location",
    }
    return descriptions.get(error_code, "Unknown error")


class NodeManagerError(OnexError):
    """Base exception class for node manager errors with error code support."""

    def __init__(
        self, message: str, error_code: NodeManagerErrorCode, **kwargs: Any
    ) -> None:
        """
        Initialize a node manager error with error code.

        Args:
            message: Human-readable error message
            error_code: Canonical error code
            **kwargs: Additional context for the error
        """
        super().__init__(message, error_code, **kwargs)
        self.error_code = error_code


class NodeManagerInputError(NodeManagerError):
    """Exception for input validation errors in node manager operations."""

    pass


class NodeManagerProcessingError(NodeManagerError):
    """Exception for processing errors in node manager operations."""

    pass


class NodeManagerFileError(NodeManagerError):
    """Exception for file operation errors in node manager operations."""

    pass


class NodeManagerValidationError(NodeManagerError):
    """Exception for validation errors in node manager operations."""

    pass


class NodeManagerMaintenanceError(NodeManagerError):
    """Exception for maintenance operation errors in node manager operations."""

    pass


# Legacy aliases for backward compatibility
NodeGeneratorErrorCode = NodeManagerErrorCode
NodeGeneratorError = NodeManagerError
NodeGeneratorInputError = NodeManagerInputError
NodeGeneratorProcessingError = NodeManagerProcessingError
NodeGeneratorFileError = NodeManagerFileError
NodeGeneratorValidationError = NodeManagerValidationError
NodeGeneratorPostProcessingError = NodeManagerMaintenanceError

# Register error codes with the global registry
register_error_codes("node_manager", NodeManagerErrorCode)
