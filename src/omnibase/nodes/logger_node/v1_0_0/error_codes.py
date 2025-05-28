# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: error_codes.py
# version: 1.0.0
# uuid: 9c2c8e0d-dde7-482e-8c46-2f5414d0cda4
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.957970
# last_modified_at: 2025-05-28T17:20:04.853397
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 93a6cb8d3b801d598e899478aab3593c68477cdf8a8091db621f86baac2f5d3c
# entrypoint: python@error_codes.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.error_codes
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Error codes and exit code mapping for template node.

This module defines canonical error codes for the template node and provides
mapping functionality to convert OnexStatus values to appropriate CLI exit codes.

Exit Code Conventions:
- 0: Success (OnexStatus.SUCCESS)
- 1: General error (OnexStatus.ERROR, OnexStatus.UNKNOWN)
- 2: Warning (OnexStatus.WARNING)
- 3: Partial success (OnexStatus.PARTIAL)
- 4: Skipped (OnexStatus.SKIPPED)
- 5: Fixed (OnexStatus.FIXED)
- 6: Info (OnexStatus.INFO)

Error Code Format: ONEX_TEMPLATE_<NUMBER>_<DESCRIPTION>
"""

import re
from typing import Any, Dict

from omnibase.core.core_error_codes import (
    CLIExitCode,
    OnexError,
    OnexErrorCode,
    register_error_codes,
)


class LoggerErrorCode(OnexErrorCode):
    """Canonical error codes for logger node operations."""

    # Input validation errors (001-020)
    INVALID_LOG_LEVEL = "ONEX_LOGGER_001_INVALID_LOG_LEVEL"
    MISSING_MESSAGE = "ONEX_LOGGER_002_MISSING_MESSAGE"
    INVALID_OUTPUT_FORMAT = "ONEX_LOGGER_003_INVALID_OUTPUT_FORMAT"
    FIELD_VALIDATION_ERROR = "ONEX_LOGGER_004_FIELD_VALIDATION_ERROR"

    # Processing errors (021-040)
    LOG_PROCESSING_FAILED = "ONEX_LOGGER_021_LOG_PROCESSING_FAILED"
    LOG_FORMATTING_ERROR = "ONEX_LOGGER_022_LOG_FORMATTING_ERROR"
    CONTEXT_PARSING_ERROR = "ONEX_LOGGER_023_CONTEXT_PARSING_ERROR"
    TAGS_PARSING_ERROR = "ONEX_LOGGER_024_TAGS_PARSING_ERROR"

    # Handler errors (041-060)
    FORMAT_HANDLER_NOT_FOUND = "ONEX_LOGGER_041_FORMAT_HANDLER_NOT_FOUND"
    HANDLER_INITIALIZATION_FAILED = "ONEX_LOGGER_042_HANDLER_INITIALIZATION_FAILED"
    HANDLER_EXECUTION_FAILED = "ONEX_LOGGER_043_HANDLER_EXECUTION_FAILED"
    HANDLER_REGISTRY_ERROR = "ONEX_LOGGER_044_HANDLER_REGISTRY_ERROR"

    # Output errors (061-080)
    OUTPUT_GENERATION_FAILED = "ONEX_LOGGER_061_OUTPUT_GENERATION_FAILED"
    OUTPUT_VALIDATION_ERROR = "ONEX_LOGGER_062_OUTPUT_VALIDATION_ERROR"
    OUTPUT_SERIALIZATION_ERROR = "ONEX_LOGGER_063_OUTPUT_SERIALIZATION_ERROR"
    OUTPUT_FORMAT_ERROR = "ONEX_LOGGER_064_OUTPUT_FORMAT_ERROR"

    # Configuration errors (081-100)
    INVALID_CONFIGURATION = "ONEX_LOGGER_081_INVALID_CONFIGURATION"
    MISSING_REQUIRED_PARAMETER = "ONEX_LOGGER_082_MISSING_REQUIRED_PARAMETER"
    UNSUPPORTED_OPERATION = "ONEX_LOGGER_083_UNSUPPORTED_OPERATION"
    DEPENDENCY_ERROR = "ONEX_LOGGER_084_DEPENDENCY_ERROR"

    def get_component(self) -> str:
        """Get the component identifier for this error code."""
        return "LOGGER"

    def get_number(self) -> int:
        """Get the numeric identifier for this error code."""
        # Extract number from error code string (e.g., "ONEX_LOGGER_001_..." -> 1)
        match = re.search(r"ONEX_LOGGER_(\d+)_", self.value)
        return int(match.group(1)) if match else 0

    def get_description(self) -> str:
        """Get a human-readable description for this error code."""
        return get_error_description(self)

    def get_exit_code(self) -> int:
        """Get the appropriate CLI exit code for this error."""
        return get_exit_code_for_error(self)


# Mapping from error codes to exit codes (for specific error handling)
ERROR_CODE_TO_EXIT_CODE: Dict[LoggerErrorCode, CLIExitCode] = {
    # Input validation errors -> ERROR
    LoggerErrorCode.INVALID_LOG_LEVEL: CLIExitCode.ERROR,
    LoggerErrorCode.MISSING_MESSAGE: CLIExitCode.ERROR,
    LoggerErrorCode.INVALID_OUTPUT_FORMAT: CLIExitCode.ERROR,
    LoggerErrorCode.FIELD_VALIDATION_ERROR: CLIExitCode.ERROR,
    # Processing errors -> ERROR
    LoggerErrorCode.LOG_PROCESSING_FAILED: CLIExitCode.ERROR,
    LoggerErrorCode.LOG_FORMATTING_ERROR: CLIExitCode.ERROR,
    LoggerErrorCode.CONTEXT_PARSING_ERROR: CLIExitCode.ERROR,
    LoggerErrorCode.TAGS_PARSING_ERROR: CLIExitCode.ERROR,
    # Handler errors -> ERROR
    LoggerErrorCode.FORMAT_HANDLER_NOT_FOUND: CLIExitCode.ERROR,
    LoggerErrorCode.HANDLER_INITIALIZATION_FAILED: CLIExitCode.ERROR,
    LoggerErrorCode.HANDLER_EXECUTION_FAILED: CLIExitCode.ERROR,
    LoggerErrorCode.HANDLER_REGISTRY_ERROR: CLIExitCode.ERROR,
    # Output errors -> WARNING (may be recoverable)
    LoggerErrorCode.OUTPUT_GENERATION_FAILED: CLIExitCode.WARNING,
    LoggerErrorCode.OUTPUT_VALIDATION_ERROR: CLIExitCode.WARNING,
    LoggerErrorCode.OUTPUT_SERIALIZATION_ERROR: CLIExitCode.WARNING,
    LoggerErrorCode.OUTPUT_FORMAT_ERROR: CLIExitCode.WARNING,
    # Configuration errors -> ERROR
    LoggerErrorCode.INVALID_CONFIGURATION: CLIExitCode.ERROR,
    LoggerErrorCode.MISSING_REQUIRED_PARAMETER: CLIExitCode.ERROR,
    LoggerErrorCode.UNSUPPORTED_OPERATION: CLIExitCode.ERROR,
    LoggerErrorCode.DEPENDENCY_ERROR: CLIExitCode.ERROR,
}


def get_exit_code_for_error(error_code: LoggerErrorCode) -> int:
    """
    Get the appropriate CLI exit code for a specific error code.

    Args:
        error_code: The LoggerErrorCode to map

    Returns:
        The corresponding CLI exit code (integer)

    Example:
        >>> get_exit_code_for_error(LoggerErrorCode.MISSING_MESSAGE)
        1
        >>> get_exit_code_for_error(LoggerErrorCode.OUTPUT_VALIDATION_ERROR)
        2
    """
    return ERROR_CODE_TO_EXIT_CODE.get(error_code, CLIExitCode.ERROR).value


def get_error_description(error_code: LoggerErrorCode) -> str:
    """
    Get a human-readable description for an error code.

    Args:
        error_code: The LoggerErrorCode to describe

    Returns:
        A human-readable description of the error
    """
    descriptions = {
        LoggerErrorCode.INVALID_LOG_LEVEL: "Invalid log level specified",
        LoggerErrorCode.MISSING_MESSAGE: "Missing required log message",
        LoggerErrorCode.INVALID_OUTPUT_FORMAT: "Invalid output format specified",
        LoggerErrorCode.FIELD_VALIDATION_ERROR: "Field validation failed",
        LoggerErrorCode.LOG_PROCESSING_FAILED: "Log processing failed",
        LoggerErrorCode.LOG_FORMATTING_ERROR: "Log formatting error",
        LoggerErrorCode.CONTEXT_PARSING_ERROR: "Context parsing error",
        LoggerErrorCode.TAGS_PARSING_ERROR: "Tags parsing error",
        LoggerErrorCode.FORMAT_HANDLER_NOT_FOUND: "No handler for output format",
        LoggerErrorCode.HANDLER_INITIALIZATION_FAILED: "Handler initialization failed",
        LoggerErrorCode.HANDLER_EXECUTION_FAILED: "Handler execution failed",
        LoggerErrorCode.HANDLER_REGISTRY_ERROR: "Handler registry error",
        LoggerErrorCode.OUTPUT_GENERATION_FAILED: "Output generation failed",
        LoggerErrorCode.OUTPUT_VALIDATION_ERROR: "Output validation failed",
        LoggerErrorCode.OUTPUT_SERIALIZATION_ERROR: "Output serialization failed",
        LoggerErrorCode.OUTPUT_FORMAT_ERROR: "Output format error",
        LoggerErrorCode.INVALID_CONFIGURATION: "Invalid configuration",
        LoggerErrorCode.MISSING_REQUIRED_PARAMETER: "Required parameter missing",
        LoggerErrorCode.UNSUPPORTED_OPERATION: "Operation not supported",
        LoggerErrorCode.DEPENDENCY_ERROR: "Dependency error",
    }
    return descriptions.get(error_code, "Unknown error")


class LoggerError(OnexError):
    """Base exception class for logger node errors with error code support."""

    def __init__(
        self, message: str, error_code: LoggerErrorCode, **kwargs: Any
    ) -> None:
        """
        Initialize a logger error with error code.

        Args:
            message: Human-readable error message
            error_code: Canonical error code
            **kwargs: Additional context information
        """
        super().__init__(message, error_code=error_code, **kwargs)


# Specific exception classes for different error categories
class LoggerInputError(LoggerError):
    """Input validation related errors."""

    pass


class LoggerProcessingError(LoggerError):
    """Log processing related errors."""

    pass


class LoggerHandlerError(LoggerError):
    """Handler related errors."""

    pass


class LoggerOutputError(LoggerError):
    """Output related errors."""

    pass


class LoggerConfigurationError(LoggerError):
    """Configuration related errors."""

    pass


# Register logger error codes with the global registry

register_error_codes("logger", LoggerErrorCode)
