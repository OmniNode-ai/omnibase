# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:25.862768'
# description: Stamped by PythonHandler
# entrypoint: python://error_codes.py
# hash: 4140a2cb920da90509b4ae340f9b057b6148693f49489d75d2a4a65ff7f3f91d
# last_modified_at: '2025-05-29T11:50:11.166232+00:00'
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
# uuid: 89c33747-02ab-4746-a8eb-126326ceb52f
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Error codes and exit code mapping for docstring generator node.

This module defines canonical error codes for the docstring generator node and provides
mapping functionality to convert OnexStatus values to appropriate CLI exit codes.

Exit Code Conventions:
- 0: Success (OnexStatus.SUCCESS)
- 1: General error (OnexStatus.ERROR, OnexStatus.UNKNOWN)
- 2: Warning (OnexStatus.WARNING)
- 3: Partial success (OnexStatus.PARTIAL)
- 4: Skipped (OnexStatus.SKIPPED)
- 5: Fixed (OnexStatus.FIXED)
- 6: Info (OnexStatus.INFO)

Error Code Format: ONEX_DOCSTRING_GENERATOR_<NUMBER>_<DESCRIPTION>
"""

import re
from typing import Any, Dict

from omnibase.core.core_error_codes import (
    CLIExitCode,
    OnexError,
    OnexErrorCode,
    register_error_codes,
)


class DocstringGeneratorErrorCode(OnexErrorCode):
    """Canonical error codes for docstring generator node operations."""

    # Input validation errors (001-020)
    INVALID_REQUIRED_FIELD = "ONEX_DOCSTRING_GENERATOR_001_INVALID_REQUIRED_FIELD"
    MISSING_REQUIRED_FIELD = "ONEX_DOCSTRING_GENERATOR_002_MISSING_REQUIRED_FIELD"
    INVALID_OPTIONAL_FIELD = "ONEX_DOCSTRING_GENERATOR_003_INVALID_OPTIONAL_FIELD"
    FIELD_VALIDATION_ERROR = "ONEX_DOCSTRING_GENERATOR_004_FIELD_VALIDATION_ERROR"

    # Processing errors (021-040)
    SCHEMA_PROCESSING_FAILED = "ONEX_DOCSTRING_GENERATOR_021_SCHEMA_PROCESSING_FAILED"
    TEMPLATE_EXECUTION_ERROR = "ONEX_DOCSTRING_GENERATOR_022_TEMPLATE_EXECUTION_ERROR"
    DOCUMENTATION_GENERATION_ERROR = (
        "ONEX_DOCSTRING_GENERATOR_023_DOCUMENTATION_GENERATION_ERROR"
    )
    SCHEMA_PARSING_TIMEOUT = "ONEX_DOCSTRING_GENERATOR_024_SCHEMA_PARSING_TIMEOUT"

    # Handler errors (041-060)
    SCHEMA_LOADER_NOT_FOUND = "ONEX_DOCSTRING_GENERATOR_041_SCHEMA_LOADER_NOT_FOUND"
    TEMPLATE_LOADER_FAILED = "ONEX_DOCSTRING_GENERATOR_042_TEMPLATE_LOADER_FAILED"
    MARKDOWN_GENERATOR_FAILED = "ONEX_DOCSTRING_GENERATOR_043_MARKDOWN_GENERATOR_FAILED"
    JINJA2_RENDERER_ERROR = "ONEX_DOCSTRING_GENERATOR_044_JINJA2_RENDERER_ERROR"

    # Output errors (061-080)
    OUTPUT_GENERATION_FAILED = "ONEX_DOCSTRING_GENERATOR_061_OUTPUT_GENERATION_FAILED"
    OUTPUT_VALIDATION_ERROR = "ONEX_DOCSTRING_GENERATOR_062_OUTPUT_VALIDATION_ERROR"
    OUTPUT_SERIALIZATION_ERROR = (
        "ONEX_DOCSTRING_GENERATOR_063_OUTPUT_SERIALIZATION_ERROR"
    )
    OUTPUT_FORMAT_ERROR = "ONEX_DOCSTRING_GENERATOR_064_OUTPUT_FORMAT_ERROR"

    # Configuration errors (081-100)
    INVALID_CONFIGURATION = "ONEX_DOCSTRING_GENERATOR_081_INVALID_CONFIGURATION"
    MISSING_REQUIRED_PARAMETER = (
        "ONEX_DOCSTRING_GENERATOR_082_MISSING_REQUIRED_PARAMETER"
    )
    UNSUPPORTED_OPERATION = "ONEX_DOCSTRING_GENERATOR_083_UNSUPPORTED_OPERATION"
    SCHEMA_VERSION_MISMATCH = "ONEX_DOCSTRING_GENERATOR_084_SCHEMA_VERSION_MISMATCH"

    def get_component(self) -> str:
        """Get the component identifier for this error code."""
        return "DOCSTRING_GENERATOR"

    def get_number(self) -> int:
        """Get the numeric identifier for this error code."""
        # Extract number from error code string (e.g., "ONEX_DOCSTRING_GENERATOR_001_..." -> 1)
        match = re.search(r"ONEX_DOCSTRING_GENERATOR_(\d+)_", self.value)
        return int(match.group(1)) if match else 0

    def get_description(self) -> str:
        """Get a human-readable description for this error code."""
        return get_error_description(self)

    def get_exit_code(self) -> int:
        """Get the appropriate CLI exit code for this error."""
        return get_exit_code_for_error(self)


# Mapping from error codes to exit codes (for specific error handling)
ERROR_CODE_TO_EXIT_CODE: Dict[DocstringGeneratorErrorCode, CLIExitCode] = {
    # Input validation errors -> ERROR
    DocstringGeneratorErrorCode.INVALID_REQUIRED_FIELD: CLIExitCode.ERROR,
    DocstringGeneratorErrorCode.MISSING_REQUIRED_FIELD: CLIExitCode.ERROR,
    DocstringGeneratorErrorCode.INVALID_OPTIONAL_FIELD: CLIExitCode.ERROR,
    DocstringGeneratorErrorCode.FIELD_VALIDATION_ERROR: CLIExitCode.ERROR,
    # Processing errors -> ERROR
    DocstringGeneratorErrorCode.SCHEMA_PROCESSING_FAILED: CLIExitCode.ERROR,
    DocstringGeneratorErrorCode.TEMPLATE_EXECUTION_ERROR: CLIExitCode.ERROR,
    DocstringGeneratorErrorCode.DOCUMENTATION_GENERATION_ERROR: CLIExitCode.ERROR,
    DocstringGeneratorErrorCode.SCHEMA_PARSING_TIMEOUT: CLIExitCode.ERROR,
    # Handler errors -> ERROR
    DocstringGeneratorErrorCode.SCHEMA_LOADER_NOT_FOUND: CLIExitCode.ERROR,
    DocstringGeneratorErrorCode.TEMPLATE_LOADER_FAILED: CLIExitCode.ERROR,
    DocstringGeneratorErrorCode.MARKDOWN_GENERATOR_FAILED: CLIExitCode.ERROR,
    DocstringGeneratorErrorCode.JINJA2_RENDERER_ERROR: CLIExitCode.ERROR,
    # Output errors -> WARNING (may be recoverable)
    DocstringGeneratorErrorCode.OUTPUT_GENERATION_FAILED: CLIExitCode.WARNING,
    DocstringGeneratorErrorCode.OUTPUT_VALIDATION_ERROR: CLIExitCode.WARNING,
    DocstringGeneratorErrorCode.OUTPUT_SERIALIZATION_ERROR: CLIExitCode.WARNING,
    DocstringGeneratorErrorCode.OUTPUT_FORMAT_ERROR: CLIExitCode.WARNING,
    # Configuration errors -> ERROR
    DocstringGeneratorErrorCode.INVALID_CONFIGURATION: CLIExitCode.ERROR,
    DocstringGeneratorErrorCode.MISSING_REQUIRED_PARAMETER: CLIExitCode.ERROR,
    DocstringGeneratorErrorCode.UNSUPPORTED_OPERATION: CLIExitCode.ERROR,
    DocstringGeneratorErrorCode.SCHEMA_VERSION_MISMATCH: CLIExitCode.ERROR,
}


def get_exit_code_for_error(error_code: DocstringGeneratorErrorCode) -> int:
    """
    Get the appropriate CLI exit code for a specific error code.

    Args:
        error_code: The DocstringGeneratorErrorCode to map

    Returns:
        The corresponding CLI exit code (integer)

    Example:
        >>> get_exit_code_for_error(DocstringGeneratorErrorCode.MISSING_REQUIRED_FIELD)
        1
        >>> get_exit_code_for_error(DocstringGeneratorErrorCode.OUTPUT_VALIDATION_ERROR)
        2
    """
    return ERROR_CODE_TO_EXIT_CODE.get(error_code, CLIExitCode.ERROR).value


def get_error_description(error_code: DocstringGeneratorErrorCode) -> str:
    """
    Get a human-readable description for an error code.

    Args:
        error_code: The DocstringGeneratorErrorCode to describe

    Returns:
        A human-readable description of the error
    """
    descriptions = {
        DocstringGeneratorErrorCode.INVALID_REQUIRED_FIELD: "Invalid required field value",
        DocstringGeneratorErrorCode.MISSING_REQUIRED_FIELD: "Missing required field",
        DocstringGeneratorErrorCode.INVALID_OPTIONAL_FIELD: "Invalid optional field value",
        DocstringGeneratorErrorCode.FIELD_VALIDATION_ERROR: "Field validation failed",
        DocstringGeneratorErrorCode.SCHEMA_PROCESSING_FAILED: "Schema processing failed",
        DocstringGeneratorErrorCode.TEMPLATE_EXECUTION_ERROR: "Template execution error",
        DocstringGeneratorErrorCode.DOCUMENTATION_GENERATION_ERROR: "Documentation generation error",
        DocstringGeneratorErrorCode.SCHEMA_PARSING_TIMEOUT: "Schema parsing timeout",
        DocstringGeneratorErrorCode.SCHEMA_LOADER_NOT_FOUND: "No schema loader found",
        DocstringGeneratorErrorCode.TEMPLATE_LOADER_FAILED: "Template loader failed",
        DocstringGeneratorErrorCode.MARKDOWN_GENERATOR_FAILED: "Markdown generator failed",
        DocstringGeneratorErrorCode.JINJA2_RENDERER_ERROR: "Jinja2 renderer error",
        DocstringGeneratorErrorCode.OUTPUT_GENERATION_FAILED: "Output generation failed",
        DocstringGeneratorErrorCode.OUTPUT_VALIDATION_ERROR: "Output validation failed",
        DocstringGeneratorErrorCode.OUTPUT_SERIALIZATION_ERROR: "Output serialization failed",
        DocstringGeneratorErrorCode.OUTPUT_FORMAT_ERROR: "Output format error",
        DocstringGeneratorErrorCode.INVALID_CONFIGURATION: "Invalid configuration",
        DocstringGeneratorErrorCode.MISSING_REQUIRED_PARAMETER: "Required parameter missing",
        DocstringGeneratorErrorCode.UNSUPPORTED_OPERATION: "Operation not supported",
        DocstringGeneratorErrorCode.SCHEMA_VERSION_MISMATCH: "Schema version incompatible",
    }
    return descriptions.get(error_code, "Unknown error")


class DocstringGeneratorError(OnexError):
    """Base exception class for docstring generator node errors with error code support."""

    def __init__(
        self, message: str, error_code: DocstringGeneratorErrorCode, **kwargs: Any
    ) -> None:
        """
        Initialize a docstring generator error with error code.

        Args:
            message: Human-readable error message
            error_code: Canonical error code
            **kwargs: Additional context information
        """
        super().__init__(message, error_code=error_code, **kwargs)


# Specific exception classes for different error categories
class DocstringGeneratorInputError(DocstringGeneratorError):
    """Input validation related errors."""

    pass


class DocstringGeneratorProcessingError(DocstringGeneratorError):
    """Schema processing related errors."""

    pass


class DocstringGeneratorHandlerError(DocstringGeneratorError):
    """Handler related errors."""

    pass


class DocstringGeneratorOutputError(DocstringGeneratorError):
    """Output related errors."""

    pass


class DocstringGeneratorConfigurationError(DocstringGeneratorError):
    """Configuration related errors."""

    pass


# Register docstring generator error codes with the global registry

register_error_codes("docstring_generator", DocstringGeneratorErrorCode)
