# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: error_codes.py
# version: 1.0.0
# uuid: be1500b4-c9a1-429c-af89-0c4335ee7266
# author: OmniNode Team
# created_at: 2025-05-28T12:36:26.595785
# last_modified_at: 2025-05-28T17:20:05.706173
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 3c41c00b6b510834dad683e46bd086c7b405d3cee64cb34eb188e9607b4be3b6
# entrypoint: python@error_codes.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.error_codes
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Error codes and exit code mapping for stamper node.

This module defines canonical error codes for the stamper node and provides
mapping functionality to convert OnexStatus values to appropriate CLI exit codes.

Exit Code Conventions:
- 0: Success (OnexStatus.SUCCESS)
- 1: General error (OnexStatus.ERROR, OnexStatus.UNKNOWN)
- 2: Warning (OnexStatus.WARNING)
- 3: Partial success (OnexStatus.PARTIAL)
- 4: Skipped (OnexStatus.SKIPPED)
- 5: Fixed (OnexStatus.FIXED)
- 6: Info (OnexStatus.INFO)

Error Code Format: ONEX_STAMP_<NUMBER>_<DESCRIPTION>
"""

import re
from typing import Any, Dict

from omnibase.core.core_error_codes import (
    CLIExitCode,
    OnexError,
    OnexErrorCode,
    register_error_codes,
)


class StamperErrorCode(OnexErrorCode):
    """Canonical error codes for stamper node operations."""

    # File system errors (001-020)
    FILE_NOT_FOUND = "ONEX_STAMP_001_FILE_NOT_FOUND"
    FILE_READ_ERROR = "ONEX_STAMP_002_FILE_READ_ERROR"
    FILE_WRITE_ERROR = "ONEX_STAMP_003_FILE_WRITE_ERROR"
    PERMISSION_DENIED = "ONEX_STAMP_004_PERMISSION_DENIED"
    INVALID_FILE_TYPE = "ONEX_STAMP_005_INVALID_FILE_TYPE"

    # Metadata errors (021-040)
    METADATA_PARSE_ERROR = "ONEX_STAMP_021_METADATA_PARSE_ERROR"
    METADATA_VALIDATION_ERROR = "ONEX_STAMP_022_METADATA_VALIDATION_ERROR"
    METADATA_CORRUPTION = "ONEX_STAMP_023_METADATA_CORRUPTION"
    SCHEMA_VERSION_MISMATCH = "ONEX_STAMP_024_SCHEMA_VERSION_MISMATCH"

    # Handler errors (041-060)
    HANDLER_NOT_FOUND = "ONEX_STAMP_041_HANDLER_NOT_FOUND"
    HANDLER_INITIALIZATION_FAILED = "ONEX_STAMP_042_HANDLER_INITIALIZATION_FAILED"
    HANDLER_EXECUTION_FAILED = "ONEX_STAMP_043_HANDLER_EXECUTION_FAILED"

    # Validation errors (061-080)
    IDEMPOTENCY_CHECK_FAILED = "ONEX_STAMP_061_IDEMPOTENCY_CHECK_FAILED"
    HASH_VERIFICATION_FAILED = "ONEX_STAMP_062_HASH_VERIFICATION_FAILED"
    CONTENT_VALIDATION_FAILED = "ONEX_STAMP_063_CONTENT_VALIDATION_FAILED"

    # Configuration errors (081-100)
    INVALID_CONFIGURATION = "ONEX_STAMP_081_INVALID_CONFIGURATION"
    MISSING_REQUIRED_PARAMETER = "ONEX_STAMP_082_MISSING_REQUIRED_PARAMETER"
    UNSUPPORTED_OPERATION = "ONEX_STAMP_083_UNSUPPORTED_OPERATION"

    def get_component(self) -> str:
        """Get the component identifier for this error code."""
        return "STAMP"

    def get_number(self) -> int:
        """Get the numeric identifier for this error code."""
        # Extract number from error code string (e.g., "ONEX_STAMP_001_..." -> 1)
        match = re.search(r"ONEX_STAMP_(\d+)_", self.value)
        return int(match.group(1)) if match else 0

    def get_description(self) -> str:
        """Get a human-readable description for this error code."""
        return get_error_description(self)

    def get_exit_code(self) -> int:
        """Get the appropriate CLI exit code for this error."""
        return get_exit_code_for_error(self)


# Mapping from error codes to exit codes (for specific error handling)
ERROR_CODE_TO_EXIT_CODE: Dict[StamperErrorCode, CLIExitCode] = {
    # File system errors -> ERROR
    StamperErrorCode.FILE_NOT_FOUND: CLIExitCode.ERROR,
    StamperErrorCode.FILE_READ_ERROR: CLIExitCode.ERROR,
    StamperErrorCode.FILE_WRITE_ERROR: CLIExitCode.ERROR,
    StamperErrorCode.PERMISSION_DENIED: CLIExitCode.ERROR,
    StamperErrorCode.INVALID_FILE_TYPE: CLIExitCode.ERROR,
    # Metadata errors -> ERROR
    StamperErrorCode.METADATA_PARSE_ERROR: CLIExitCode.ERROR,
    StamperErrorCode.METADATA_VALIDATION_ERROR: CLIExitCode.ERROR,
    StamperErrorCode.METADATA_CORRUPTION: CLIExitCode.ERROR,
    StamperErrorCode.SCHEMA_VERSION_MISMATCH: CLIExitCode.ERROR,
    # Handler errors -> ERROR
    StamperErrorCode.HANDLER_NOT_FOUND: CLIExitCode.ERROR,
    StamperErrorCode.HANDLER_INITIALIZATION_FAILED: CLIExitCode.ERROR,
    StamperErrorCode.HANDLER_EXECUTION_FAILED: CLIExitCode.ERROR,
    # Validation errors -> WARNING (may be recoverable)
    StamperErrorCode.IDEMPOTENCY_CHECK_FAILED: CLIExitCode.WARNING,
    StamperErrorCode.HASH_VERIFICATION_FAILED: CLIExitCode.WARNING,
    StamperErrorCode.CONTENT_VALIDATION_FAILED: CLIExitCode.WARNING,
    # Configuration errors -> ERROR
    StamperErrorCode.INVALID_CONFIGURATION: CLIExitCode.ERROR,
    StamperErrorCode.MISSING_REQUIRED_PARAMETER: CLIExitCode.ERROR,
    StamperErrorCode.UNSUPPORTED_OPERATION: CLIExitCode.ERROR,
}


def get_exit_code_for_error(error_code: StamperErrorCode) -> int:
    """
    Get the appropriate CLI exit code for a specific error code.

    Args:
        error_code: The StamperErrorCode to map

    Returns:
        The corresponding CLI exit code (integer)

    Example:
        >>> get_exit_code_for_error(StamperErrorCode.FILE_NOT_FOUND)
        1
        >>> get_exit_code_for_error(StamperErrorCode.IDEMPOTENCY_CHECK_FAILED)
        2
    """
    return ERROR_CODE_TO_EXIT_CODE.get(error_code, CLIExitCode.ERROR).value


def get_error_description(error_code: StamperErrorCode) -> str:
    """
    Get a human-readable description for an error code.

    Args:
        error_code: The StamperErrorCode to describe

    Returns:
        A human-readable description of the error
    """
    descriptions = {
        StamperErrorCode.FILE_NOT_FOUND: "Target file does not exist",
        StamperErrorCode.FILE_READ_ERROR: "Cannot read target file",
        StamperErrorCode.FILE_WRITE_ERROR: "Cannot write to target file",
        StamperErrorCode.PERMISSION_DENIED: "Insufficient file permissions",
        StamperErrorCode.INVALID_FILE_TYPE: "Unsupported file type",
        StamperErrorCode.METADATA_PARSE_ERROR: "Cannot parse existing metadata",
        StamperErrorCode.METADATA_VALIDATION_ERROR: "Metadata validation failed",
        StamperErrorCode.METADATA_CORRUPTION: "Metadata block is corrupted",
        StamperErrorCode.SCHEMA_VERSION_MISMATCH: "Schema version incompatible",
        StamperErrorCode.HANDLER_NOT_FOUND: "No handler for file type",
        StamperErrorCode.HANDLER_INITIALIZATION_FAILED: "Handler initialization failed",
        StamperErrorCode.HANDLER_EXECUTION_FAILED: "Handler execution failed",
        StamperErrorCode.IDEMPOTENCY_CHECK_FAILED: "Idempotency verification failed",
        StamperErrorCode.HASH_VERIFICATION_FAILED: "Hash verification failed",
        StamperErrorCode.CONTENT_VALIDATION_FAILED: "Content validation failed",
        StamperErrorCode.INVALID_CONFIGURATION: "Invalid configuration",
        StamperErrorCode.MISSING_REQUIRED_PARAMETER: "Required parameter missing",
        StamperErrorCode.UNSUPPORTED_OPERATION: "Operation not supported",
    }
    return descriptions.get(error_code, "Unknown error")


class StamperError(OnexError):
    """Base exception class for stamper node errors with error code support."""

    def __init__(
        self, message: str, error_code: StamperErrorCode, **kwargs: Any
    ) -> None:
        """
        Initialize a stamper error with error code.

        Args:
            message: Human-readable error message
            error_code: Canonical error code
            **kwargs: Additional context information
        """
        super().__init__(message, error_code=error_code, **kwargs)


# Specific exception classes for different error categories
class StamperFileError(StamperError):
    """File system related errors."""

    pass


class StamperMetadataError(StamperError):
    """Metadata parsing/validation errors."""

    pass


class StamperHandlerError(StamperError):
    """Handler related errors."""

    pass


class StamperValidationError(StamperError):
    """Validation related errors."""

    pass


class StamperConfigurationError(StamperError):
    """Configuration related errors."""

    pass


# Register stamper error codes with the global registry
register_error_codes("stamper", StamperErrorCode)
