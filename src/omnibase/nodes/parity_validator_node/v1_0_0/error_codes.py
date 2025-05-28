# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: error_codes.py
# version: 1.0.0
# uuid: 1443c236-9cac-40ed-b6f2-fa018dc0d91d
# author: OmniNode Team
# created_at: 2025-05-28T12:36:26.294873
# last_modified_at: 2025-05-28T17:20:04.749580
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: d1b0d9c9433929e16802d0e15adc0d1a31752d2c3165a9ad626a76b40e77d670
# entrypoint: python@error_codes.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.error_codes
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Error codes for parity validator node.

This module defines comprehensive error codes for all parity validator operations,
following the ONEX error code conventions and providing proper CLI exit code mapping.
"""

import re
from typing import Any, Dict

from omnibase.core.core_error_codes import (
    CLIExitCode,
    OnexError,
    OnexErrorCode,
    register_error_codes,
)


class ParityValidatorErrorCode(OnexErrorCode):
    """Canonical error codes for parity validator node operations."""

    # Directory and file system errors (001-020)
    NODES_DIRECTORY_NOT_FOUND = "ONEX_PARITY_001_NODES_DIRECTORY_NOT_FOUND"
    NODES_DIRECTORY_READ_ERROR = "ONEX_PARITY_002_NODES_DIRECTORY_READ_ERROR"
    PERMISSION_DENIED = "ONEX_PARITY_003_PERMISSION_DENIED"
    INVALID_DIRECTORY_PATH = "ONEX_PARITY_004_INVALID_DIRECTORY_PATH"

    # Node discovery errors (021-040)
    NODE_DISCOVERY_FAILED = "ONEX_PARITY_021_NODE_DISCOVERY_FAILED"
    NODE_IMPORT_ERROR = "ONEX_PARITY_022_NODE_IMPORT_ERROR"
    NODE_INTROSPECTION_FAILED = "ONEX_PARITY_023_NODE_INTROSPECTION_FAILED"
    INVALID_NODE_STRUCTURE = "ONEX_PARITY_024_INVALID_NODE_STRUCTURE"
    NODE_VERSION_DETECTION_FAILED = "ONEX_PARITY_025_NODE_VERSION_DETECTION_FAILED"
    NO_NODES_DISCOVERED = "ONEX_PARITY_026_NO_NODES_DISCOVERED"
    NODE_METADATA_MISSING = "ONEX_PARITY_027_NODE_METADATA_MISSING"
    NODE_CLI_DETECTION_FAILED = "ONEX_PARITY_028_NODE_CLI_DETECTION_FAILED"

    # Validation execution errors (041-060)
    CLI_EXECUTION_FAILED = "ONEX_PARITY_041_CLI_EXECUTION_FAILED"
    NODE_EXECUTION_FAILED = "ONEX_PARITY_042_NODE_EXECUTION_FAILED"
    PARITY_CHECK_FAILED = "ONEX_PARITY_043_PARITY_CHECK_FAILED"
    SCHEMA_VALIDATION_FAILED = "ONEX_PARITY_044_SCHEMA_VALIDATION_FAILED"
    ERROR_CODE_VALIDATION_FAILED = "ONEX_PARITY_045_ERROR_CODE_VALIDATION_FAILED"
    CONTRACT_VALIDATION_FAILED = "ONEX_PARITY_046_CONTRACT_VALIDATION_FAILED"
    VALIDATION_TIMEOUT = "ONEX_PARITY_047_VALIDATION_TIMEOUT"
    VALIDATION_INTERRUPTED = "ONEX_PARITY_048_VALIDATION_INTERRUPTED"
    INTROSPECTION_VALIDATION_FAILED = "ONEX_PARITY_049_INTROSPECTION_VALIDATION_FAILED"
    OUTPUT_COMPARISON_FAILED = "ONEX_PARITY_050_OUTPUT_COMPARISON_FAILED"

    # Result processing errors (061-080)
    RESULT_AGGREGATION_FAILED = "ONEX_PARITY_061_RESULT_AGGREGATION_FAILED"
    REPORT_GENERATION_FAILED = "ONEX_PARITY_062_REPORT_GENERATION_FAILED"
    SUMMARY_CALCULATION_FAILED = "ONEX_PARITY_063_SUMMARY_CALCULATION_FAILED"
    RESULT_SERIALIZATION_FAILED = "ONEX_PARITY_064_RESULT_SERIALIZATION_FAILED"
    PERFORMANCE_METRICS_FAILED = "ONEX_PARITY_065_PERFORMANCE_METRICS_FAILED"
    VALIDATION_RESULT_INVALID = "ONEX_PARITY_066_VALIDATION_RESULT_INVALID"

    # Configuration and parameter errors (081-100)
    INVALID_VALIDATION_TYPE = "ONEX_PARITY_081_INVALID_VALIDATION_TYPE"
    INVALID_NODE_FILTER = "ONEX_PARITY_082_INVALID_NODE_FILTER"
    MISSING_REQUIRED_PARAMETER = "ONEX_PARITY_083_MISSING_REQUIRED_PARAMETER"
    INVALID_CONFIGURATION = "ONEX_PARITY_084_INVALID_CONFIGURATION"
    UNSUPPORTED_OPERATION = "ONEX_PARITY_085_UNSUPPORTED_OPERATION"
    VALIDATION_TYPE_CONFLICT = "ONEX_PARITY_086_VALIDATION_TYPE_CONFLICT"
    NODE_FILTER_NO_MATCHES = "ONEX_PARITY_087_NODE_FILTER_NO_MATCHES"
    INVALID_PERFORMANCE_CONFIG = "ONEX_PARITY_088_INVALID_PERFORMANCE_CONFIG"

    def get_component(self) -> str:
        """Get the component identifier for this error code."""
        return "PARITY"

    def get_number(self) -> int:
        """Get the numeric identifier for this error code."""
        # Extract number from error code string (e.g., "ONEX_PARITY_001_..." -> 1)
        match = re.search(r"ONEX_PARITY_(\d+)_", self.value)
        return int(match.group(1)) if match else 0

    def get_description(self) -> str:
        """Get a human-readable description for this error code."""
        return get_error_description(self)

    def get_exit_code(self) -> int:
        """Get the appropriate CLI exit code for this error."""
        return get_exit_code_for_error(self)


# Mapping from error codes to exit codes (for specific error handling)
ERROR_CODE_TO_EXIT_CODE: Dict[ParityValidatorErrorCode, CLIExitCode] = {
    # Directory and file system errors -> ERROR
    ParityValidatorErrorCode.NODES_DIRECTORY_NOT_FOUND: CLIExitCode.ERROR,
    ParityValidatorErrorCode.NODES_DIRECTORY_READ_ERROR: CLIExitCode.ERROR,
    ParityValidatorErrorCode.PERMISSION_DENIED: CLIExitCode.ERROR,
    ParityValidatorErrorCode.INVALID_DIRECTORY_PATH: CLIExitCode.ERROR,
    # Node discovery errors -> ERROR (except NO_NODES_DISCOVERED which is WARNING)
    ParityValidatorErrorCode.NODE_DISCOVERY_FAILED: CLIExitCode.ERROR,
    ParityValidatorErrorCode.NODE_IMPORT_ERROR: CLIExitCode.ERROR,
    ParityValidatorErrorCode.NODE_INTROSPECTION_FAILED: CLIExitCode.ERROR,
    ParityValidatorErrorCode.INVALID_NODE_STRUCTURE: CLIExitCode.ERROR,
    ParityValidatorErrorCode.NODE_VERSION_DETECTION_FAILED: CLIExitCode.ERROR,
    ParityValidatorErrorCode.NO_NODES_DISCOVERED: CLIExitCode.WARNING,
    ParityValidatorErrorCode.NODE_METADATA_MISSING: CLIExitCode.ERROR,
    ParityValidatorErrorCode.NODE_CLI_DETECTION_FAILED: CLIExitCode.ERROR,
    # Validation execution errors -> WARNING (validation failures) or ERROR (system failures)
    ParityValidatorErrorCode.CLI_EXECUTION_FAILED: CLIExitCode.ERROR,
    ParityValidatorErrorCode.NODE_EXECUTION_FAILED: CLIExitCode.ERROR,
    ParityValidatorErrorCode.PARITY_CHECK_FAILED: CLIExitCode.WARNING,
    ParityValidatorErrorCode.SCHEMA_VALIDATION_FAILED: CLIExitCode.WARNING,
    ParityValidatorErrorCode.ERROR_CODE_VALIDATION_FAILED: CLIExitCode.WARNING,
    ParityValidatorErrorCode.CONTRACT_VALIDATION_FAILED: CLIExitCode.WARNING,
    ParityValidatorErrorCode.VALIDATION_TIMEOUT: CLIExitCode.ERROR,
    ParityValidatorErrorCode.VALIDATION_INTERRUPTED: CLIExitCode.ERROR,
    ParityValidatorErrorCode.INTROSPECTION_VALIDATION_FAILED: CLIExitCode.WARNING,
    ParityValidatorErrorCode.OUTPUT_COMPARISON_FAILED: CLIExitCode.ERROR,
    # Result processing errors -> ERROR
    ParityValidatorErrorCode.RESULT_AGGREGATION_FAILED: CLIExitCode.ERROR,
    ParityValidatorErrorCode.REPORT_GENERATION_FAILED: CLIExitCode.ERROR,
    ParityValidatorErrorCode.SUMMARY_CALCULATION_FAILED: CLIExitCode.ERROR,
    ParityValidatorErrorCode.RESULT_SERIALIZATION_FAILED: CLIExitCode.ERROR,
    ParityValidatorErrorCode.PERFORMANCE_METRICS_FAILED: CLIExitCode.WARNING,
    ParityValidatorErrorCode.VALIDATION_RESULT_INVALID: CLIExitCode.ERROR,
    # Configuration and parameter errors -> ERROR (except NODE_FILTER_NO_MATCHES which is WARNING)
    ParityValidatorErrorCode.INVALID_VALIDATION_TYPE: CLIExitCode.ERROR,
    ParityValidatorErrorCode.INVALID_NODE_FILTER: CLIExitCode.ERROR,
    ParityValidatorErrorCode.MISSING_REQUIRED_PARAMETER: CLIExitCode.ERROR,
    ParityValidatorErrorCode.INVALID_CONFIGURATION: CLIExitCode.ERROR,
    ParityValidatorErrorCode.UNSUPPORTED_OPERATION: CLIExitCode.ERROR,
    ParityValidatorErrorCode.VALIDATION_TYPE_CONFLICT: CLIExitCode.ERROR,
    ParityValidatorErrorCode.NODE_FILTER_NO_MATCHES: CLIExitCode.WARNING,
    ParityValidatorErrorCode.INVALID_PERFORMANCE_CONFIG: CLIExitCode.ERROR,
}


def get_exit_code_for_error(error_code: ParityValidatorErrorCode) -> int:
    """
    Get the appropriate CLI exit code for a specific error code.

    Args:
        error_code: The ParityValidatorErrorCode to map

    Returns:
        The corresponding CLI exit code (integer)

    Example:
        >>> get_exit_code_for_error(ParityValidatorErrorCode.NODES_DIRECTORY_NOT_FOUND)
        1
        >>> get_exit_code_for_error(ParityValidatorErrorCode.PARITY_CHECK_FAILED)
        2
    """
    return ERROR_CODE_TO_EXIT_CODE.get(error_code, CLIExitCode.ERROR).value


def get_error_description(error_code: ParityValidatorErrorCode) -> str:
    """
    Get a human-readable description for an error code.

    Args:
        error_code: The ParityValidatorErrorCode to describe

    Returns:
        A human-readable description of the error
    """
    descriptions = {
        ParityValidatorErrorCode.NODES_DIRECTORY_NOT_FOUND: "Nodes directory does not exist",
        ParityValidatorErrorCode.NODES_DIRECTORY_READ_ERROR: "Cannot read nodes directory",
        ParityValidatorErrorCode.PERMISSION_DENIED: "Insufficient directory permissions",
        ParityValidatorErrorCode.INVALID_DIRECTORY_PATH: "Invalid directory path",
        ParityValidatorErrorCode.NODE_DISCOVERY_FAILED: "Node discovery failed",
        ParityValidatorErrorCode.NODE_IMPORT_ERROR: "Cannot import node module",
        ParityValidatorErrorCode.NODE_INTROSPECTION_FAILED: "Node introspection failed",
        ParityValidatorErrorCode.INVALID_NODE_STRUCTURE: "Invalid node directory structure",
        ParityValidatorErrorCode.NODE_VERSION_DETECTION_FAILED: "Cannot detect node version",
        ParityValidatorErrorCode.NO_NODES_DISCOVERED: "No ONEX nodes discovered",
        ParityValidatorErrorCode.NODE_METADATA_MISSING: "Node metadata missing or invalid",
        ParityValidatorErrorCode.NODE_CLI_DETECTION_FAILED: "Cannot detect node CLI entrypoint",
        ParityValidatorErrorCode.CLI_EXECUTION_FAILED: "CLI execution failed",
        ParityValidatorErrorCode.NODE_EXECUTION_FAILED: "Direct node execution failed",
        ParityValidatorErrorCode.PARITY_CHECK_FAILED: "CLI/Node parity check failed",
        ParityValidatorErrorCode.SCHEMA_VALIDATION_FAILED: "Schema validation failed",
        ParityValidatorErrorCode.ERROR_CODE_VALIDATION_FAILED: "Error code validation failed",
        ParityValidatorErrorCode.CONTRACT_VALIDATION_FAILED: "Contract validation failed",
        ParityValidatorErrorCode.VALIDATION_TIMEOUT: "Validation execution timeout",
        ParityValidatorErrorCode.VALIDATION_INTERRUPTED: "Validation interrupted",
        ParityValidatorErrorCode.INTROSPECTION_VALIDATION_FAILED: "Introspection validation failed",
        ParityValidatorErrorCode.OUTPUT_COMPARISON_FAILED: "Output comparison failed",
        ParityValidatorErrorCode.RESULT_AGGREGATION_FAILED: "Result aggregation failed",
        ParityValidatorErrorCode.REPORT_GENERATION_FAILED: "Report generation failed",
        ParityValidatorErrorCode.SUMMARY_CALCULATION_FAILED: "Summary calculation failed",
        ParityValidatorErrorCode.RESULT_SERIALIZATION_FAILED: "Result serialization failed",
        ParityValidatorErrorCode.PERFORMANCE_METRICS_FAILED: "Performance metrics calculation failed",
        ParityValidatorErrorCode.VALIDATION_RESULT_INVALID: "Validation result format invalid",
        ParityValidatorErrorCode.INVALID_VALIDATION_TYPE: "Invalid validation type",
        ParityValidatorErrorCode.INVALID_NODE_FILTER: "Invalid node filter",
        ParityValidatorErrorCode.MISSING_REQUIRED_PARAMETER: "Required parameter missing",
        ParityValidatorErrorCode.INVALID_CONFIGURATION: "Invalid configuration",
        ParityValidatorErrorCode.UNSUPPORTED_OPERATION: "Operation not supported",
        ParityValidatorErrorCode.VALIDATION_TYPE_CONFLICT: "Conflicting validation types",
        ParityValidatorErrorCode.NODE_FILTER_NO_MATCHES: "Node filter matched no nodes",
        ParityValidatorErrorCode.INVALID_PERFORMANCE_CONFIG: "Invalid performance configuration",
    }
    return descriptions.get(error_code, "Unknown error")


class ParityValidatorError(OnexError):
    """Base exception class for parity validator node errors with error code support."""

    def __init__(
        self, message: str, error_code: ParityValidatorErrorCode, **kwargs: Any
    ) -> None:
        """
        Initialize a parity validator error with error code.

        Args:
            message: Human-readable error message
            error_code: The specific error code
            **kwargs: Additional context information
        """
        super().__init__(message, error_code=error_code, **kwargs)


# Specific exception classes for different error categories
class DirectoryError(ParityValidatorError):
    """Directory and file system related errors."""

    pass


class DiscoveryError(ParityValidatorError):
    """Node discovery related errors."""

    pass


class ValidationError(ParityValidatorError):
    """Validation execution related errors."""

    pass


class ProcessingError(ParityValidatorError):
    """Result processing related errors."""

    pass


class ConfigurationError(ParityValidatorError):
    """Configuration and parameter related errors."""

    pass


# Register parity validator error codes with the global registry
register_error_codes("parity_validator", ParityValidatorErrorCode)
