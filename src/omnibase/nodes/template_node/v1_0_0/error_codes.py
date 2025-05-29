# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.886622'
# description: Stamped by PythonHandler
# entrypoint: python://error_codes
# hash: 2087f078c6b6f5b78260d09dc767ba1b032f116a3560a86910339e05640d09fe
# last_modified_at: '2025-05-29T14:14:00.015277+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: error_codes.py
# namespace: python://omnibase.nodes.template_node.v1_0_0.error_codes
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 0f343d6f-5866-4597-b6ad-506ef7cfcda7
# version: 1.0.0
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


class TemplateErrorCode(OnexErrorCode):
    """Canonical error codes for template node operations."""

    # Input validation errors (001-020)
    INVALID_REQUIRED_FIELD = "ONEX_TEMPLATE_001_INVALID_REQUIRED_FIELD"
    MISSING_REQUIRED_FIELD = "ONEX_TEMPLATE_002_MISSING_REQUIRED_FIELD"
    INVALID_OPTIONAL_FIELD = "ONEX_TEMPLATE_003_INVALID_OPTIONAL_FIELD"
    FIELD_VALIDATION_ERROR = "ONEX_TEMPLATE_004_FIELD_VALIDATION_ERROR"

    # Processing errors (021-040)
    TEMPLATE_PROCESSING_FAILED = "ONEX_TEMPLATE_021_TEMPLATE_PROCESSING_FAILED"
    TEMPLATE_EXECUTION_ERROR = "ONEX_TEMPLATE_022_TEMPLATE_EXECUTION_ERROR"
    TEMPLATE_LOGIC_ERROR = "ONEX_TEMPLATE_023_TEMPLATE_LOGIC_ERROR"
    TEMPLATE_TIMEOUT = "ONEX_TEMPLATE_024_TEMPLATE_TIMEOUT"

    # Handler errors (041-060)
    HANDLER_NOT_FOUND = "ONEX_TEMPLATE_041_HANDLER_NOT_FOUND"
    HANDLER_INITIALIZATION_FAILED = "ONEX_TEMPLATE_042_HANDLER_INITIALIZATION_FAILED"
    HANDLER_EXECUTION_FAILED = "ONEX_TEMPLATE_043_HANDLER_EXECUTION_FAILED"
    HANDLER_REGISTRY_ERROR = "ONEX_TEMPLATE_044_HANDLER_REGISTRY_ERROR"

    # Output errors (061-080)
    OUTPUT_GENERATION_FAILED = "ONEX_TEMPLATE_061_OUTPUT_GENERATION_FAILED"
    OUTPUT_VALIDATION_ERROR = "ONEX_TEMPLATE_062_OUTPUT_VALIDATION_ERROR"
    OUTPUT_SERIALIZATION_ERROR = "ONEX_TEMPLATE_063_OUTPUT_SERIALIZATION_ERROR"
    OUTPUT_FORMAT_ERROR = "ONEX_TEMPLATE_064_OUTPUT_FORMAT_ERROR"

    # Configuration errors (081-100)
    INVALID_CONFIGURATION = "ONEX_TEMPLATE_081_INVALID_CONFIGURATION"
    MISSING_REQUIRED_PARAMETER = "ONEX_TEMPLATE_082_MISSING_REQUIRED_PARAMETER"
    UNSUPPORTED_OPERATION = "ONEX_TEMPLATE_083_UNSUPPORTED_OPERATION"
    TEMPLATE_VERSION_MISMATCH = "ONEX_TEMPLATE_084_TEMPLATE_VERSION_MISMATCH"

    def get_component(self) -> str:
        """Get the component identifier for this error code."""
        return "TEMPLATE"

    def get_number(self) -> int:
        """Get the numeric identifier for this error code."""
        # Extract number from error code string (e.g., "ONEX_TEMPLATE_001_..." -> 1)
        match = re.search(r"ONEX_TEMPLATE_(\d+)_", self.value)
        return int(match.group(1)) if match else 0

    def get_description(self) -> str:
        """Get a human-readable description for this error code."""
        return get_error_description(self)

    def get_exit_code(self) -> int:
        """Get the appropriate CLI exit code for this error."""
        return get_exit_code_for_error(self)


# Mapping from error codes to exit codes (for specific error handling)
ERROR_CODE_TO_EXIT_CODE: Dict[TemplateErrorCode, CLIExitCode] = {
    # Input validation errors -> ERROR
    TemplateErrorCode.INVALID_REQUIRED_FIELD: CLIExitCode.ERROR,
    TemplateErrorCode.MISSING_REQUIRED_FIELD: CLIExitCode.ERROR,
    TemplateErrorCode.INVALID_OPTIONAL_FIELD: CLIExitCode.ERROR,
    TemplateErrorCode.FIELD_VALIDATION_ERROR: CLIExitCode.ERROR,
    # Processing errors -> ERROR
    TemplateErrorCode.TEMPLATE_PROCESSING_FAILED: CLIExitCode.ERROR,
    TemplateErrorCode.TEMPLATE_EXECUTION_ERROR: CLIExitCode.ERROR,
    TemplateErrorCode.TEMPLATE_LOGIC_ERROR: CLIExitCode.ERROR,
    TemplateErrorCode.TEMPLATE_TIMEOUT: CLIExitCode.ERROR,
    # Handler errors -> ERROR
    TemplateErrorCode.HANDLER_NOT_FOUND: CLIExitCode.ERROR,
    TemplateErrorCode.HANDLER_INITIALIZATION_FAILED: CLIExitCode.ERROR,
    TemplateErrorCode.HANDLER_EXECUTION_FAILED: CLIExitCode.ERROR,
    TemplateErrorCode.HANDLER_REGISTRY_ERROR: CLIExitCode.ERROR,
    # Output errors -> WARNING (may be recoverable)
    TemplateErrorCode.OUTPUT_GENERATION_FAILED: CLIExitCode.WARNING,
    TemplateErrorCode.OUTPUT_VALIDATION_ERROR: CLIExitCode.WARNING,
    TemplateErrorCode.OUTPUT_SERIALIZATION_ERROR: CLIExitCode.WARNING,
    TemplateErrorCode.OUTPUT_FORMAT_ERROR: CLIExitCode.WARNING,
    # Configuration errors -> ERROR
    TemplateErrorCode.INVALID_CONFIGURATION: CLIExitCode.ERROR,
    TemplateErrorCode.MISSING_REQUIRED_PARAMETER: CLIExitCode.ERROR,
    TemplateErrorCode.UNSUPPORTED_OPERATION: CLIExitCode.ERROR,
    TemplateErrorCode.TEMPLATE_VERSION_MISMATCH: CLIExitCode.ERROR,
}


def get_exit_code_for_error(error_code: TemplateErrorCode) -> int:
    """
    Get the appropriate CLI exit code for a specific error code.

    Args:
        error_code: The TemplateErrorCode to map

    Returns:
        The corresponding CLI exit code (integer)

    Example:
        >>> get_exit_code_for_error(TemplateErrorCode.MISSING_REQUIRED_FIELD)
        1
        >>> get_exit_code_for_error(TemplateErrorCode.OUTPUT_VALIDATION_ERROR)
        2
    """
    return ERROR_CODE_TO_EXIT_CODE.get(error_code, CLIExitCode.ERROR).value


def get_error_description(error_code: TemplateErrorCode) -> str:
    """
    Get a human-readable description for an error code.

    Args:
        error_code: The TemplateErrorCode to describe

    Returns:
        A human-readable description of the error
    """
    descriptions = {
        TemplateErrorCode.INVALID_REQUIRED_FIELD: "Invalid required field value",
        TemplateErrorCode.MISSING_REQUIRED_FIELD: "Missing required field",
        TemplateErrorCode.INVALID_OPTIONAL_FIELD: "Invalid optional field value",
        TemplateErrorCode.FIELD_VALIDATION_ERROR: "Field validation failed",
        TemplateErrorCode.TEMPLATE_PROCESSING_FAILED: "Template processing failed",
        TemplateErrorCode.TEMPLATE_EXECUTION_ERROR: "Template execution error",
        TemplateErrorCode.TEMPLATE_LOGIC_ERROR: "Template logic error",
        TemplateErrorCode.TEMPLATE_TIMEOUT: "Template execution timeout",
        TemplateErrorCode.HANDLER_NOT_FOUND: "No handler for file type",
        TemplateErrorCode.HANDLER_INITIALIZATION_FAILED: "Handler initialization failed",
        TemplateErrorCode.HANDLER_EXECUTION_FAILED: "Handler execution failed",
        TemplateErrorCode.HANDLER_REGISTRY_ERROR: "Handler registry error",
        TemplateErrorCode.OUTPUT_GENERATION_FAILED: "Output generation failed",
        TemplateErrorCode.OUTPUT_VALIDATION_ERROR: "Output validation failed",
        TemplateErrorCode.OUTPUT_SERIALIZATION_ERROR: "Output serialization failed",
        TemplateErrorCode.OUTPUT_FORMAT_ERROR: "Output format error",
        TemplateErrorCode.INVALID_CONFIGURATION: "Invalid configuration",
        TemplateErrorCode.MISSING_REQUIRED_PARAMETER: "Required parameter missing",
        TemplateErrorCode.UNSUPPORTED_OPERATION: "Operation not supported",
        TemplateErrorCode.TEMPLATE_VERSION_MISMATCH: "Template version incompatible",
    }
    return descriptions.get(error_code, "Unknown error")


class TemplateError(OnexError):
    """Base exception class for template node errors with error code support."""

    def __init__(
        self, message: str, error_code: TemplateErrorCode, **kwargs: Any
    ) -> None:
        """
        Initialize a template error with error code.

        Args:
            message: Human-readable error message
            error_code: Canonical error code
            **kwargs: Additional context information
        """
        super().__init__(message, error_code=error_code, **kwargs)


# Specific exception classes for different error categories
class TemplateInputError(TemplateError):
    """Input validation related errors."""

    pass


class TemplateProcessingError(TemplateError):
    """Template processing related errors."""

    pass


class TemplateHandlerError(TemplateError):
    """Handler related errors."""

    pass


class TemplateOutputError(TemplateError):
    """Output related errors."""

    pass


class TemplateConfigurationError(TemplateError):
    """Configuration related errors."""

    pass


# Register template error codes with the global registry

register_error_codes("template", TemplateErrorCode)
