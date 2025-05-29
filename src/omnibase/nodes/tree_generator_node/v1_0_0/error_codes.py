# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.990774'
# description: Stamped by PythonHandler
# entrypoint: python://error_codes.py
# hash: db50423af4e2ac524be6dfdfd80753bad2eb191bdb68a31bb800be4d82434a8e
# last_modified_at: '2025-05-29T11:50:11.957606+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: error_codes.py
# namespace: omnibase.error_codes
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: be42386a-c871-4b91-b2b4-3c8b0203fc40
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Error codes and exit code mapping for tree generator node.

This module defines canonical error codes for the tree generator node and provides
mapping functionality to convert OnexStatus values to appropriate CLI exit codes.

Exit Code Conventions:
- 0: Success (OnexStatus.SUCCESS)
- 1: General error (OnexStatus.ERROR, OnexStatus.UNKNOWN)
- 2: Warning (OnexStatus.WARNING)
- 3: Partial success (OnexStatus.PARTIAL)
- 4: Skipped (OnexStatus.SKIPPED)
- 5: Fixed (OnexStatus.FIXED)
- 6: Info (OnexStatus.INFO)

Error Code Format: ONEX_TREE_<NUMBER>_<DESCRIPTION>
"""

import re
from typing import Any, Dict

from omnibase.core.core_error_codes import (
    CLIExitCode,
    OnexError,
    OnexErrorCode,
    register_error_codes,
)


class TreeGeneratorErrorCode(OnexErrorCode):
    """Canonical error codes for tree generator node operations."""

    # Directory errors (001-020)
    DIRECTORY_NOT_FOUND = "ONEX_TREE_001_DIRECTORY_NOT_FOUND"
    DIRECTORY_READ_ERROR = "ONEX_TREE_002_DIRECTORY_READ_ERROR"
    PERMISSION_DENIED = "ONEX_TREE_003_PERMISSION_DENIED"
    INVALID_DIRECTORY_PATH = "ONEX_TREE_004_INVALID_DIRECTORY_PATH"

    # File system errors (021-040)
    OUTPUT_FILE_WRITE_ERROR = "ONEX_TREE_021_OUTPUT_FILE_WRITE_ERROR"
    OUTPUT_DIRECTORY_CREATE_ERROR = "ONEX_TREE_022_OUTPUT_DIRECTORY_CREATE_ERROR"
    MANIFEST_PARSE_ERROR = "ONEX_TREE_023_MANIFEST_PARSE_ERROR"
    MANIFEST_VALIDATION_ERROR = "ONEX_TREE_024_MANIFEST_VALIDATION_ERROR"

    # Discovery errors (041-060)
    ARTIFACT_DISCOVERY_FAILED = "ONEX_TREE_041_ARTIFACT_DISCOVERY_FAILED"
    METADATA_EXTRACTION_FAILED = "ONEX_TREE_042_METADATA_EXTRACTION_FAILED"
    HANDLER_NOT_FOUND = "ONEX_TREE_043_HANDLER_NOT_FOUND"
    HANDLER_EXECUTION_FAILED = "ONEX_TREE_044_HANDLER_EXECUTION_FAILED"

    # Validation errors (061-080)
    TREE_VALIDATION_FAILED = "ONEX_TREE_061_TREE_VALIDATION_FAILED"
    SCHEMA_VERSION_MISMATCH = "ONEX_TREE_062_SCHEMA_VERSION_MISMATCH"
    ARTIFACT_COUNT_MISMATCH = "ONEX_TREE_063_ARTIFACT_COUNT_MISMATCH"
    MISSING_REQUIRED_ARTIFACTS = "ONEX_TREE_064_MISSING_REQUIRED_ARTIFACTS"

    # Configuration errors (081-100)
    INVALID_OUTPUT_FORMAT = "ONEX_TREE_081_INVALID_OUTPUT_FORMAT"
    INVALID_CONFIGURATION = "ONEX_TREE_082_INVALID_CONFIGURATION"
    MISSING_REQUIRED_PARAMETER = "ONEX_TREE_083_MISSING_REQUIRED_PARAMETER"
    UNSUPPORTED_OPERATION = "ONEX_TREE_084_UNSUPPORTED_OPERATION"

    def get_component(self) -> str:
        """Get the component identifier for this error code."""
        return "TREE"

    def get_number(self) -> int:
        """Get the numeric identifier for this error code."""
        # Extract number from error code string (e.g., "ONEX_TREE_001_..." -> 1)
        match = re.search(r"ONEX_TREE_(\d+)_", self.value)
        return int(match.group(1)) if match else 0

    def get_description(self) -> str:
        """Get a human-readable description for this error code."""
        return get_error_description(self)

    def get_exit_code(self) -> int:
        """Get the appropriate CLI exit code for this error."""
        return get_exit_code_for_error(self)


# Mapping from error codes to exit codes (for specific error handling)
ERROR_CODE_TO_EXIT_CODE: Dict[TreeGeneratorErrorCode, CLIExitCode] = {
    # Directory errors -> ERROR
    TreeGeneratorErrorCode.DIRECTORY_NOT_FOUND: CLIExitCode.ERROR,
    TreeGeneratorErrorCode.DIRECTORY_READ_ERROR: CLIExitCode.ERROR,
    TreeGeneratorErrorCode.PERMISSION_DENIED: CLIExitCode.ERROR,
    TreeGeneratorErrorCode.INVALID_DIRECTORY_PATH: CLIExitCode.ERROR,
    # File system errors -> ERROR
    TreeGeneratorErrorCode.OUTPUT_FILE_WRITE_ERROR: CLIExitCode.ERROR,
    TreeGeneratorErrorCode.OUTPUT_DIRECTORY_CREATE_ERROR: CLIExitCode.ERROR,
    TreeGeneratorErrorCode.MANIFEST_PARSE_ERROR: CLIExitCode.ERROR,
    TreeGeneratorErrorCode.MANIFEST_VALIDATION_ERROR: CLIExitCode.ERROR,
    # Discovery errors -> ERROR
    TreeGeneratorErrorCode.ARTIFACT_DISCOVERY_FAILED: CLIExitCode.ERROR,
    TreeGeneratorErrorCode.METADATA_EXTRACTION_FAILED: CLIExitCode.ERROR,
    TreeGeneratorErrorCode.HANDLER_NOT_FOUND: CLIExitCode.ERROR,
    TreeGeneratorErrorCode.HANDLER_EXECUTION_FAILED: CLIExitCode.ERROR,
    # Validation errors -> WARNING (may be recoverable)
    TreeGeneratorErrorCode.TREE_VALIDATION_FAILED: CLIExitCode.WARNING,
    TreeGeneratorErrorCode.SCHEMA_VERSION_MISMATCH: CLIExitCode.WARNING,
    TreeGeneratorErrorCode.ARTIFACT_COUNT_MISMATCH: CLIExitCode.WARNING,
    TreeGeneratorErrorCode.MISSING_REQUIRED_ARTIFACTS: CLIExitCode.WARNING,
    # Configuration errors -> ERROR
    TreeGeneratorErrorCode.INVALID_OUTPUT_FORMAT: CLIExitCode.ERROR,
    TreeGeneratorErrorCode.INVALID_CONFIGURATION: CLIExitCode.ERROR,
    TreeGeneratorErrorCode.MISSING_REQUIRED_PARAMETER: CLIExitCode.ERROR,
    TreeGeneratorErrorCode.UNSUPPORTED_OPERATION: CLIExitCode.ERROR,
}


def get_exit_code_for_error(error_code: TreeGeneratorErrorCode) -> int:
    """
    Get the appropriate CLI exit code for a specific error code.

    Args:
        error_code: The TreeGeneratorErrorCode to map

    Returns:
        The corresponding CLI exit code (integer)

    Example:
        >>> get_exit_code_for_error(TreeGeneratorErrorCode.DIRECTORY_NOT_FOUND)
        1
        >>> get_exit_code_for_error(TreeGeneratorErrorCode.TREE_VALIDATION_FAILED)
        2
    """
    return ERROR_CODE_TO_EXIT_CODE.get(error_code, CLIExitCode.ERROR).value


def get_error_description(error_code: TreeGeneratorErrorCode) -> str:
    """
    Get a human-readable description for an error code.

    Args:
        error_code: The TreeGeneratorErrorCode to describe

    Returns:
        A human-readable description of the error
    """
    descriptions = {
        TreeGeneratorErrorCode.DIRECTORY_NOT_FOUND: "Target directory does not exist",
        TreeGeneratorErrorCode.DIRECTORY_READ_ERROR: "Cannot read target directory",
        TreeGeneratorErrorCode.PERMISSION_DENIED: "Insufficient directory permissions",
        TreeGeneratorErrorCode.INVALID_DIRECTORY_PATH: "Invalid directory path",
        TreeGeneratorErrorCode.OUTPUT_FILE_WRITE_ERROR: "Cannot write output file",
        TreeGeneratorErrorCode.OUTPUT_DIRECTORY_CREATE_ERROR: "Cannot create output directory",
        TreeGeneratorErrorCode.MANIFEST_PARSE_ERROR: "Cannot parse manifest file",
        TreeGeneratorErrorCode.MANIFEST_VALIDATION_ERROR: "Manifest validation failed",
        TreeGeneratorErrorCode.ARTIFACT_DISCOVERY_FAILED: "Artifact discovery failed",
        TreeGeneratorErrorCode.METADATA_EXTRACTION_FAILED: "Metadata extraction failed",
        TreeGeneratorErrorCode.HANDLER_NOT_FOUND: "No handler for file type",
        TreeGeneratorErrorCode.HANDLER_EXECUTION_FAILED: "Handler execution failed",
        TreeGeneratorErrorCode.TREE_VALIDATION_FAILED: "Tree validation failed",
        TreeGeneratorErrorCode.SCHEMA_VERSION_MISMATCH: "Schema version incompatible",
        TreeGeneratorErrorCode.ARTIFACT_COUNT_MISMATCH: "Artifact count mismatch",
        TreeGeneratorErrorCode.MISSING_REQUIRED_ARTIFACTS: "Missing required artifacts",
        TreeGeneratorErrorCode.INVALID_OUTPUT_FORMAT: "Invalid output format",
        TreeGeneratorErrorCode.INVALID_CONFIGURATION: "Invalid configuration",
        TreeGeneratorErrorCode.MISSING_REQUIRED_PARAMETER: "Required parameter missing",
        TreeGeneratorErrorCode.UNSUPPORTED_OPERATION: "Operation not supported",
    }
    return descriptions.get(error_code, "Unknown error")


class TreeGeneratorError(OnexError):
    """Base exception class for tree generator node errors with error code support."""

    def __init__(
        self, message: str, error_code: TreeGeneratorErrorCode, **kwargs: Any
    ) -> None:
        """
        Initialize a tree generator error with error code.

        Args:
            message: Human-readable error message
            error_code: Canonical error code
            **kwargs: Additional context information
        """
        super().__init__(message, error_code=error_code, **kwargs)


# Specific exception classes for different error categories
class TreeGeneratorDirectoryError(TreeGeneratorError):
    """Directory related errors."""

    pass


class TreeGeneratorFileSystemError(TreeGeneratorError):
    """File system related errors."""

    pass


class TreeGeneratorDiscoveryError(TreeGeneratorError):
    """Discovery related errors."""

    pass


class TreeGeneratorValidationError(TreeGeneratorError):
    """Validation related errors."""

    pass


class TreeGeneratorConfigurationError(TreeGeneratorError):
    """Configuration related errors."""

    pass


# Register tree generator error codes with the global registry

register_error_codes("tree_generator", TreeGeneratorErrorCode)
