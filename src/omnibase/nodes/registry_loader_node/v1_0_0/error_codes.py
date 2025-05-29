# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.411181'
# description: Stamped by PythonHandler
# entrypoint: python://error_codes.py
# hash: e1bd9ad23f5d632af1ed2f1a5e06bb9bbcb1b9b764aadbf2a378eff9faf079b9
# last_modified_at: '2025-05-29T11:50:11.559072+00:00'
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
# uuid: 920cc308-558f-4ff8-9d3e-a50a55a41b62
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Error codes and exit code mapping for registry loader node.

This module defines canonical error codes for the registry loader node and provides
mapping functionality to convert OnexStatus values to appropriate CLI exit codes.

Exit Code Conventions:
- 0: Success (OnexStatus.SUCCESS)
- 1: General error (OnexStatus.ERROR, OnexStatus.UNKNOWN)
- 2: Warning (OnexStatus.WARNING)
- 3: Partial success (OnexStatus.PARTIAL)
- 4: Skipped (OnexStatus.SKIPPED)
- 5: Fixed (OnexStatus.FIXED)
- 6: Info (OnexStatus.INFO)

Error Code Format: ONEX_REGISTRY_<NUMBER>_<DESCRIPTION>
"""

import re
from typing import Any, Dict

from omnibase.core.core_error_codes import (
    CLIExitCode,
    OnexError,
    OnexErrorCode,
    register_error_codes,
)


class RegistryLoaderErrorCode(OnexErrorCode):
    """Canonical error codes for registry loader node operations."""

    # Directory errors (001-020)
    DIRECTORY_NOT_FOUND = "ONEX_REGISTRY_001_DIRECTORY_NOT_FOUND"
    DIRECTORY_READ_ERROR = "ONEX_REGISTRY_002_DIRECTORY_READ_ERROR"
    PERMISSION_DENIED = "ONEX_REGISTRY_003_PERMISSION_DENIED"
    INVALID_DIRECTORY_PATH = "ONEX_REGISTRY_004_INVALID_DIRECTORY_PATH"

    # Registry file errors (021-040)
    REGISTRY_FILE_NOT_FOUND = "ONEX_REGISTRY_021_REGISTRY_FILE_NOT_FOUND"
    REGISTRY_FILE_PARSE_ERROR = "ONEX_REGISTRY_022_REGISTRY_FILE_PARSE_ERROR"
    REGISTRY_FILE_VALIDATION_ERROR = "ONEX_REGISTRY_023_REGISTRY_FILE_VALIDATION_ERROR"
    ONEXTREE_FILE_NOT_FOUND = "ONEX_REGISTRY_024_ONEXTREE_FILE_NOT_FOUND"
    ONEXTREE_FILE_PARSE_ERROR = "ONEX_REGISTRY_025_ONEXTREE_FILE_PARSE_ERROR"

    # Artifact discovery errors (041-060)
    ARTIFACT_DISCOVERY_FAILED = "ONEX_REGISTRY_041_ARTIFACT_DISCOVERY_FAILED"
    METADATA_EXTRACTION_FAILED = "ONEX_REGISTRY_042_METADATA_EXTRACTION_FAILED"
    ARTIFACT_TYPE_UNKNOWN = "ONEX_REGISTRY_043_ARTIFACT_TYPE_UNKNOWN"
    ARTIFACT_VERSION_INVALID = "ONEX_REGISTRY_044_ARTIFACT_VERSION_INVALID"

    # Handler errors (061-080)
    HANDLER_NOT_FOUND = "ONEX_REGISTRY_061_HANDLER_NOT_FOUND"
    HANDLER_INITIALIZATION_FAILED = "ONEX_REGISTRY_062_HANDLER_INITIALIZATION_FAILED"
    HANDLER_EXECUTION_FAILED = "ONEX_REGISTRY_063_HANDLER_EXECUTION_FAILED"
    HANDLER_REGISTRY_ERROR = "ONEX_REGISTRY_064_HANDLER_REGISTRY_ERROR"

    # Validation errors (081-100)
    ARTIFACT_VALIDATION_FAILED = "ONEX_REGISTRY_081_ARTIFACT_VALIDATION_FAILED"
    SCHEMA_VERSION_MISMATCH = "ONEX_REGISTRY_082_SCHEMA_VERSION_MISMATCH"
    DUPLICATE_ARTIFACT_ID = "ONEX_REGISTRY_083_DUPLICATE_ARTIFACT_ID"
    MISSING_REQUIRED_METADATA = "ONEX_REGISTRY_084_MISSING_REQUIRED_METADATA"

    # Configuration errors (101-120)
    INVALID_ARTIFACT_TYPE_FILTER = "ONEX_REGISTRY_101_INVALID_ARTIFACT_TYPE_FILTER"
    INVALID_CONFIGURATION = "ONEX_REGISTRY_102_INVALID_CONFIGURATION"
    MISSING_REQUIRED_PARAMETER = "ONEX_REGISTRY_103_MISSING_REQUIRED_PARAMETER"
    UNSUPPORTED_OPERATION = "ONEX_REGISTRY_104_UNSUPPORTED_OPERATION"

    def get_component(self) -> str:
        """Get the component identifier for this error code."""
        return "REGISTRY"

    def get_number(self) -> int:
        """Get the numeric identifier for this error code."""
        # Extract number from error code string (e.g., "ONEX_REGISTRY_001_..." -> 1)
        match = re.search(r"ONEX_REGISTRY_(\d+)_", self.value)
        return int(match.group(1)) if match else 0

    def get_description(self) -> str:
        """Get a human-readable description for this error code."""
        return get_error_description(self)

    def get_exit_code(self) -> int:
        """Get the appropriate CLI exit code for this error."""
        return get_exit_code_for_error(self)


# Mapping from error codes to exit codes (for specific error handling)
ERROR_CODE_TO_EXIT_CODE: Dict[RegistryLoaderErrorCode, CLIExitCode] = {
    # Directory errors -> ERROR
    RegistryLoaderErrorCode.DIRECTORY_NOT_FOUND: CLIExitCode.ERROR,
    RegistryLoaderErrorCode.DIRECTORY_READ_ERROR: CLIExitCode.ERROR,
    RegistryLoaderErrorCode.PERMISSION_DENIED: CLIExitCode.ERROR,
    RegistryLoaderErrorCode.INVALID_DIRECTORY_PATH: CLIExitCode.ERROR,
    # Registry file errors -> ERROR
    RegistryLoaderErrorCode.REGISTRY_FILE_NOT_FOUND: CLIExitCode.ERROR,
    RegistryLoaderErrorCode.REGISTRY_FILE_PARSE_ERROR: CLIExitCode.ERROR,
    RegistryLoaderErrorCode.REGISTRY_FILE_VALIDATION_ERROR: CLIExitCode.ERROR,
    RegistryLoaderErrorCode.ONEXTREE_FILE_NOT_FOUND: CLIExitCode.ERROR,
    RegistryLoaderErrorCode.ONEXTREE_FILE_PARSE_ERROR: CLIExitCode.ERROR,
    # Artifact discovery errors -> WARNING (may be partial success)
    RegistryLoaderErrorCode.ARTIFACT_DISCOVERY_FAILED: CLIExitCode.WARNING,
    RegistryLoaderErrorCode.METADATA_EXTRACTION_FAILED: CLIExitCode.WARNING,
    RegistryLoaderErrorCode.ARTIFACT_TYPE_UNKNOWN: CLIExitCode.WARNING,
    RegistryLoaderErrorCode.ARTIFACT_VERSION_INVALID: CLIExitCode.WARNING,
    # Handler errors -> ERROR
    RegistryLoaderErrorCode.HANDLER_NOT_FOUND: CLIExitCode.ERROR,
    RegistryLoaderErrorCode.HANDLER_INITIALIZATION_FAILED: CLIExitCode.ERROR,
    RegistryLoaderErrorCode.HANDLER_EXECUTION_FAILED: CLIExitCode.ERROR,
    RegistryLoaderErrorCode.HANDLER_REGISTRY_ERROR: CLIExitCode.ERROR,
    # Validation errors -> WARNING (may be recoverable)
    RegistryLoaderErrorCode.ARTIFACT_VALIDATION_FAILED: CLIExitCode.WARNING,
    RegistryLoaderErrorCode.SCHEMA_VERSION_MISMATCH: CLIExitCode.WARNING,
    RegistryLoaderErrorCode.DUPLICATE_ARTIFACT_ID: CLIExitCode.WARNING,
    RegistryLoaderErrorCode.MISSING_REQUIRED_METADATA: CLIExitCode.WARNING,
    # Configuration errors -> ERROR
    RegistryLoaderErrorCode.INVALID_ARTIFACT_TYPE_FILTER: CLIExitCode.ERROR,
    RegistryLoaderErrorCode.INVALID_CONFIGURATION: CLIExitCode.ERROR,
    RegistryLoaderErrorCode.MISSING_REQUIRED_PARAMETER: CLIExitCode.ERROR,
    RegistryLoaderErrorCode.UNSUPPORTED_OPERATION: CLIExitCode.ERROR,
}


def get_exit_code_for_error(error_code: RegistryLoaderErrorCode) -> int:
    """
    Get the appropriate CLI exit code for a specific error code.

    Args:
        error_code: The RegistryLoaderErrorCode to map

    Returns:
        The corresponding CLI exit code (integer)

    Example:
        >>> get_exit_code_for_error(RegistryLoaderErrorCode.DIRECTORY_NOT_FOUND)
        1
        >>> get_exit_code_for_error(RegistryLoaderErrorCode.ARTIFACT_VALIDATION_FAILED)
        2
    """
    return ERROR_CODE_TO_EXIT_CODE.get(error_code, CLIExitCode.ERROR).value


def get_error_description(error_code: RegistryLoaderErrorCode) -> str:
    """
    Get a human-readable description for an error code.

    Args:
        error_code: The RegistryLoaderErrorCode to describe

    Returns:
        A human-readable description of the error
    """
    descriptions = {
        RegistryLoaderErrorCode.DIRECTORY_NOT_FOUND: "Target directory does not exist",
        RegistryLoaderErrorCode.DIRECTORY_READ_ERROR: "Cannot read target directory",
        RegistryLoaderErrorCode.PERMISSION_DENIED: "Insufficient directory permissions",
        RegistryLoaderErrorCode.INVALID_DIRECTORY_PATH: "Invalid directory path",
        RegistryLoaderErrorCode.REGISTRY_FILE_NOT_FOUND: "Registry file not found",
        RegistryLoaderErrorCode.REGISTRY_FILE_PARSE_ERROR: "Cannot parse registry file",
        RegistryLoaderErrorCode.REGISTRY_FILE_VALIDATION_ERROR: "Registry file validation failed",
        RegistryLoaderErrorCode.ONEXTREE_FILE_NOT_FOUND: "Onextree file not found",
        RegistryLoaderErrorCode.ONEXTREE_FILE_PARSE_ERROR: "Cannot parse onextree file",
        RegistryLoaderErrorCode.ARTIFACT_DISCOVERY_FAILED: "Artifact discovery failed",
        RegistryLoaderErrorCode.METADATA_EXTRACTION_FAILED: "Metadata extraction failed",
        RegistryLoaderErrorCode.ARTIFACT_TYPE_UNKNOWN: "Unknown artifact type",
        RegistryLoaderErrorCode.ARTIFACT_VERSION_INVALID: "Invalid artifact version",
        RegistryLoaderErrorCode.HANDLER_NOT_FOUND: "No handler for file type",
        RegistryLoaderErrorCode.HANDLER_INITIALIZATION_FAILED: "Handler initialization failed",
        RegistryLoaderErrorCode.HANDLER_EXECUTION_FAILED: "Handler execution failed",
        RegistryLoaderErrorCode.HANDLER_REGISTRY_ERROR: "Handler registry error",
        RegistryLoaderErrorCode.ARTIFACT_VALIDATION_FAILED: "Artifact validation failed",
        RegistryLoaderErrorCode.SCHEMA_VERSION_MISMATCH: "Schema version incompatible",
        RegistryLoaderErrorCode.DUPLICATE_ARTIFACT_ID: "Duplicate artifact ID",
        RegistryLoaderErrorCode.MISSING_REQUIRED_METADATA: "Missing required metadata",
        RegistryLoaderErrorCode.INVALID_ARTIFACT_TYPE_FILTER: "Invalid artifact type filter",
        RegistryLoaderErrorCode.INVALID_CONFIGURATION: "Invalid configuration",
        RegistryLoaderErrorCode.MISSING_REQUIRED_PARAMETER: "Required parameter missing",
        RegistryLoaderErrorCode.UNSUPPORTED_OPERATION: "Operation not supported",
    }
    return descriptions.get(error_code, "Unknown error")


class RegistryLoaderError(OnexError):
    """Base exception class for registry loader node errors with error code support."""

    def __init__(
        self, message: str, error_code: RegistryLoaderErrorCode, **kwargs: Any
    ) -> None:
        """
        Initialize a registry loader error with error code.

        Args:
            message: Human-readable error message
            error_code: Canonical error code
            **kwargs: Additional context information
        """
        super().__init__(message, error_code=error_code, **kwargs)


# Specific exception classes for different error categories
class RegistryLoaderDirectoryError(RegistryLoaderError):
    """Directory related errors."""

    pass


class RegistryLoaderFileError(RegistryLoaderError):
    """Registry file related errors."""

    pass


class RegistryLoaderDiscoveryError(RegistryLoaderError):
    """Artifact discovery related errors."""

    pass


class RegistryLoaderHandlerError(RegistryLoaderError):
    """Handler related errors."""

    pass


class RegistryLoaderValidationError(RegistryLoaderError):
    """Validation related errors."""

    pass


class RegistryLoaderConfigurationError(RegistryLoaderError):
    """Configuration related errors."""

    pass


# Register registry loader error codes with the global registry

register_error_codes("registry_loader", RegistryLoaderErrorCode)
