# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.514998'
# description: Stamped by PythonHandler
# entrypoint: python://error_codes
# hash: 797075f98ad459c98d0fcb5a8528c7d12f4292479c78bf30e5023ead80b09ce5
# last_modified_at: '2025-05-29T14:13:59.720628+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: error_codes.py
# namespace: python://omnibase.nodes.schema_generator_node.v1_0_0.error_codes
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 0a646f8e-7b1b-4528-a324-79d8460dc2b2
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Error codes and exit code mapping for schema generator node.

This module defines canonical error codes for the schema generator node and provides
mapping functionality to convert OnexStatus values to appropriate CLI exit codes.

Exit Code Conventions:
- 0: Success (OnexStatus.SUCCESS)
- 1: General error (OnexStatus.ERROR, OnexStatus.UNKNOWN)
- 2: Warning (OnexStatus.WARNING)
- 3: Partial success (OnexStatus.PARTIAL)
- 4: Skipped (OnexStatus.SKIPPED)
- 5: Fixed (OnexStatus.FIXED)
- 6: Info (OnexStatus.INFO)

Error Code Format: ONEX_SCHEMA_<NUMBER>_<DESCRIPTION>
"""

import re
from typing import Any, Dict

from omnibase.core.core_error_codes import (
    CLIExitCode,
    OnexError,
    OnexErrorCode,
    register_error_codes,
)


class SchemaGeneratorErrorCode(OnexErrorCode):
    """Canonical error codes for schema generator node operations."""

    # Output directory errors (001-020)
    OUTPUT_DIRECTORY_NOT_FOUND = "ONEX_SCHEMA_001_OUTPUT_DIRECTORY_NOT_FOUND"
    OUTPUT_DIRECTORY_CREATE_ERROR = "ONEX_SCHEMA_002_OUTPUT_DIRECTORY_CREATE_ERROR"
    OUTPUT_DIRECTORY_PERMISSION_DENIED = (
        "ONEX_SCHEMA_003_OUTPUT_DIRECTORY_PERMISSION_DENIED"
    )
    INVALID_OUTPUT_PATH = "ONEX_SCHEMA_004_INVALID_OUTPUT_PATH"

    # Model errors (021-040)
    MODEL_NOT_FOUND = "ONEX_SCHEMA_021_MODEL_NOT_FOUND"
    MODEL_IMPORT_ERROR = "ONEX_SCHEMA_022_MODEL_IMPORT_ERROR"
    MODEL_VALIDATION_ERROR = "ONEX_SCHEMA_023_MODEL_VALIDATION_ERROR"
    INVALID_MODEL_NAME = "ONEX_SCHEMA_024_INVALID_MODEL_NAME"
    MODEL_SCHEMA_GENERATION_FAILED = "ONEX_SCHEMA_025_MODEL_SCHEMA_GENERATION_FAILED"

    # Schema generation errors (041-060)
    SCHEMA_SERIALIZATION_ERROR = "ONEX_SCHEMA_041_SCHEMA_SERIALIZATION_ERROR"
    SCHEMA_VALIDATION_ERROR = "ONEX_SCHEMA_042_SCHEMA_VALIDATION_ERROR"
    SCHEMA_FILE_WRITE_ERROR = "ONEX_SCHEMA_043_SCHEMA_FILE_WRITE_ERROR"
    SCHEMA_FORMAT_ERROR = "ONEX_SCHEMA_044_SCHEMA_FORMAT_ERROR"

    # Metadata errors (061-080)
    METADATA_GENERATION_FAILED = "ONEX_SCHEMA_061_METADATA_GENERATION_FAILED"
    METADATA_VALIDATION_ERROR = "ONEX_SCHEMA_062_METADATA_VALIDATION_ERROR"
    SCHEMA_ID_GENERATION_FAILED = "ONEX_SCHEMA_063_SCHEMA_ID_GENERATION_FAILED"
    SCHEMA_VERSION_MISMATCH = "ONEX_SCHEMA_064_SCHEMA_VERSION_MISMATCH"

    # Configuration errors (081-100)
    INVALID_CONFIGURATION = "ONEX_SCHEMA_081_INVALID_CONFIGURATION"
    MISSING_REQUIRED_PARAMETER = "ONEX_SCHEMA_082_MISSING_REQUIRED_PARAMETER"
    UNSUPPORTED_OPERATION = "ONEX_SCHEMA_083_UNSUPPORTED_OPERATION"
    INVALID_MODEL_FILTER = "ONEX_SCHEMA_084_INVALID_MODEL_FILTER"

    def get_component(self) -> str:
        """Get the component identifier for this error code."""
        return "SCHEMA"

    def get_number(self) -> int:
        """Get the numeric identifier for this error code."""
        # Extract number from error code string (e.g., "ONEX_SCHEMA_001_..." -> 1)
        match = re.search(r"ONEX_SCHEMA_(\d+)_", self.value)
        return int(match.group(1)) if match else 0

    def get_description(self) -> str:
        """Get a human-readable description for this error code."""
        return get_error_description(self)

    def get_exit_code(self) -> int:
        """Get the appropriate CLI exit code for this error."""
        return get_exit_code_for_error(self)


# Mapping from error codes to exit codes (for specific error handling)
ERROR_CODE_TO_EXIT_CODE: Dict[SchemaGeneratorErrorCode, CLIExitCode] = {
    # Output directory errors -> ERROR
    SchemaGeneratorErrorCode.OUTPUT_DIRECTORY_NOT_FOUND: CLIExitCode.ERROR,
    SchemaGeneratorErrorCode.OUTPUT_DIRECTORY_CREATE_ERROR: CLIExitCode.ERROR,
    SchemaGeneratorErrorCode.OUTPUT_DIRECTORY_PERMISSION_DENIED: CLIExitCode.ERROR,
    SchemaGeneratorErrorCode.INVALID_OUTPUT_PATH: CLIExitCode.ERROR,
    # Model errors -> ERROR
    SchemaGeneratorErrorCode.MODEL_NOT_FOUND: CLIExitCode.ERROR,
    SchemaGeneratorErrorCode.MODEL_IMPORT_ERROR: CLIExitCode.ERROR,
    SchemaGeneratorErrorCode.MODEL_VALIDATION_ERROR: CLIExitCode.ERROR,
    SchemaGeneratorErrorCode.INVALID_MODEL_NAME: CLIExitCode.ERROR,
    SchemaGeneratorErrorCode.MODEL_SCHEMA_GENERATION_FAILED: CLIExitCode.ERROR,
    # Schema generation errors -> ERROR
    SchemaGeneratorErrorCode.SCHEMA_SERIALIZATION_ERROR: CLIExitCode.ERROR,
    SchemaGeneratorErrorCode.SCHEMA_VALIDATION_ERROR: CLIExitCode.ERROR,
    SchemaGeneratorErrorCode.SCHEMA_FILE_WRITE_ERROR: CLIExitCode.ERROR,
    SchemaGeneratorErrorCode.SCHEMA_FORMAT_ERROR: CLIExitCode.ERROR,
    # Metadata errors -> WARNING (may be recoverable)
    SchemaGeneratorErrorCode.METADATA_GENERATION_FAILED: CLIExitCode.WARNING,
    SchemaGeneratorErrorCode.METADATA_VALIDATION_ERROR: CLIExitCode.WARNING,
    SchemaGeneratorErrorCode.SCHEMA_ID_GENERATION_FAILED: CLIExitCode.WARNING,
    SchemaGeneratorErrorCode.SCHEMA_VERSION_MISMATCH: CLIExitCode.WARNING,
    # Configuration errors -> ERROR
    SchemaGeneratorErrorCode.INVALID_CONFIGURATION: CLIExitCode.ERROR,
    SchemaGeneratorErrorCode.MISSING_REQUIRED_PARAMETER: CLIExitCode.ERROR,
    SchemaGeneratorErrorCode.UNSUPPORTED_OPERATION: CLIExitCode.ERROR,
    SchemaGeneratorErrorCode.INVALID_MODEL_FILTER: CLIExitCode.ERROR,
}


def get_exit_code_for_error(error_code: SchemaGeneratorErrorCode) -> int:
    """
    Get the appropriate CLI exit code for a specific error code.

    Args:
        error_code: The SchemaGeneratorErrorCode to map

    Returns:
        The corresponding CLI exit code (integer)

    Example:
        >>> get_exit_code_for_error(SchemaGeneratorErrorCode.MODEL_NOT_FOUND)
        1
        >>> get_exit_code_for_error(SchemaGeneratorErrorCode.METADATA_GENERATION_FAILED)
        2
    """
    return ERROR_CODE_TO_EXIT_CODE.get(error_code, CLIExitCode.ERROR).value


def get_error_description(error_code: SchemaGeneratorErrorCode) -> str:
    """
    Get a human-readable description for an error code.

    Args:
        error_code: The SchemaGeneratorErrorCode to describe

    Returns:
        A human-readable description of the error
    """
    descriptions = {
        SchemaGeneratorErrorCode.OUTPUT_DIRECTORY_NOT_FOUND: "Output directory does not exist",
        SchemaGeneratorErrorCode.OUTPUT_DIRECTORY_CREATE_ERROR: "Cannot create output directory",
        SchemaGeneratorErrorCode.OUTPUT_DIRECTORY_PERMISSION_DENIED: "Insufficient output directory permissions",
        SchemaGeneratorErrorCode.INVALID_OUTPUT_PATH: "Invalid output path",
        SchemaGeneratorErrorCode.MODEL_NOT_FOUND: "Model not found",
        SchemaGeneratorErrorCode.MODEL_IMPORT_ERROR: "Cannot import model",
        SchemaGeneratorErrorCode.MODEL_VALIDATION_ERROR: "Model validation failed",
        SchemaGeneratorErrorCode.INVALID_MODEL_NAME: "Invalid model name",
        SchemaGeneratorErrorCode.MODEL_SCHEMA_GENERATION_FAILED: "Model schema generation failed",
        SchemaGeneratorErrorCode.SCHEMA_SERIALIZATION_ERROR: "Schema serialization failed",
        SchemaGeneratorErrorCode.SCHEMA_VALIDATION_ERROR: "Schema validation failed",
        SchemaGeneratorErrorCode.SCHEMA_FILE_WRITE_ERROR: "Cannot write schema file",
        SchemaGeneratorErrorCode.SCHEMA_FORMAT_ERROR: "Schema format error",
        SchemaGeneratorErrorCode.METADATA_GENERATION_FAILED: "Metadata generation failed",
        SchemaGeneratorErrorCode.METADATA_VALIDATION_ERROR: "Metadata validation failed",
        SchemaGeneratorErrorCode.SCHEMA_ID_GENERATION_FAILED: "Schema ID generation failed",
        SchemaGeneratorErrorCode.SCHEMA_VERSION_MISMATCH: "Schema version incompatible",
        SchemaGeneratorErrorCode.INVALID_CONFIGURATION: "Invalid configuration",
        SchemaGeneratorErrorCode.MISSING_REQUIRED_PARAMETER: "Required parameter missing",
        SchemaGeneratorErrorCode.UNSUPPORTED_OPERATION: "Operation not supported",
        SchemaGeneratorErrorCode.INVALID_MODEL_FILTER: "Invalid model filter",
    }
    return descriptions.get(error_code, "Unknown error")


class SchemaGeneratorError(OnexError):
    """Base exception class for schema generator node errors with error code support."""

    def __init__(
        self, message: str, error_code: SchemaGeneratorErrorCode, **kwargs: Any
    ) -> None:
        """
        Initialize a schema generator error with error code.

        Args:
            message: Human-readable error message
            error_code: Canonical error code
            **kwargs: Additional context information
        """
        super().__init__(message, error_code=error_code, **kwargs)


# Specific exception classes for different error categories
class SchemaGeneratorDirectoryError(SchemaGeneratorError):
    """Output directory related errors."""

    pass


class SchemaGeneratorModelError(SchemaGeneratorError):
    """Model related errors."""

    pass


class SchemaGeneratorGenerationError(SchemaGeneratorError):
    """Schema generation related errors."""

    pass


class SchemaGeneratorMetadataError(SchemaGeneratorError):
    """Metadata related errors."""

    pass


class SchemaGeneratorConfigurationError(SchemaGeneratorError):
    """Configuration related errors."""

    pass


# Register schema generator error codes with the global registry

register_error_codes("schema_generator", SchemaGeneratorErrorCode)
