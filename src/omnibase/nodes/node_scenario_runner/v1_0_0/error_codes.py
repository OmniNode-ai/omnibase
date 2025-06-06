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
# namespace: python://omnibase.nodes.node_scenario_runner_node.v1_0_0.error_codes
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
Error codes and exit code mapping for node_scenario_runner node.

This module defines canonical error codes for the node_scenario_runner node and provides
mapping functionality to convert OnexStatus values to appropriate CLI exit codes.

Exit Code Conventions:
- 0: Success (OnexStatus.SUCCESS)
- 1: General error (OnexStatus.ERROR, OnexStatus.UNKNOWN)
- 2: Warning (OnexStatus.WARNING)
- 3: Partial success (OnexStatus.PARTIAL)
- 4: Skipped (OnexStatus.SKIPPED)
- 5: Fixed (OnexStatus.FIXED)
- 6: Info (OnexStatus.INFO)

Error Code Format: ONEX_NODE_SCENARIO_RUNNER_<NUMBER>_<DESCRIPTION>
"""

import re
from typing import Any, Dict

from omnibase.core.core_error_codes import (
    CLIExitCode,
    OnexError,
    OnexErrorCode,
    register_error_codes,
)


class NodeScenarioRunnerErrorCode(OnexErrorCode):
    """Canonical error codes for node_scenario_runner node operations."""

    # Input validation errors (001-020)
    INVALID_REQUIRED_FIELD = "ONEX_NODE_SCENARIO_RUNNER_001_INVALID_REQUIRED_FIELD"
    MISSING_REQUIRED_FIELD = "ONEX_NODE_SCENARIO_RUNNER_002_MISSING_REQUIRED_FIELD"
    INVALID_OPTIONAL_FIELD = "ONEX_NODE_SCENARIO_RUNNER_003_INVALID_OPTIONAL_FIELD"
    FIELD_VALIDATION_ERROR = "ONEX_NODE_SCENARIO_RUNNER_004_FIELD_VALIDATION_ERROR"

    # Processing errors (021-040)
    NODE_SCENARIO_RUNNER_PROCESSING_FAILED = (
        "ONEX_NODE_SCENARIO_RUNNER_021_NODE_SCENARIO_RUNNER_PROCESSING_FAILED"
    )
    NODE_SCENARIO_RUNNER_EXECUTION_ERROR = (
        "ONEX_NODE_SCENARIO_RUNNER_022_NODE_SCENARIO_RUNNER_EXECUTION_ERROR"
    )
    NODE_SCENARIO_RUNNER_LOGIC_ERROR = (
        "ONEX_NODE_SCENARIO_RUNNER_023_NODE_SCENARIO_RUNNER_LOGIC_ERROR"
    )
    NODE_SCENARIO_RUNNER_TIMEOUT = (
        "ONEX_NODE_SCENARIO_RUNNER_024_NODE_SCENARIO_RUNNER_TIMEOUT"
    )

    # Handler errors (041-060)
    HANDLER_NOT_FOUND = "ONEX_NODE_SCENARIO_RUNNER_041_HANDLER_NOT_FOUND"
    HANDLER_INITIALIZATION_FAILED = (
        "ONEX_NODE_SCENARIO_RUNNER_042_HANDLER_INITIALIZATION_FAILED"
    )
    HANDLER_EXECUTION_FAILED = "ONEX_NODE_SCENARIO_RUNNER_043_HANDLER_EXECUTION_FAILED"
    HANDLER_REGISTRY_ERROR = "ONEX_NODE_SCENARIO_RUNNER_044_HANDLER_REGISTRY_ERROR"

    # Output errors (061-080)
    OUTPUT_GENERATION_FAILED = "ONEX_NODE_SCENARIO_RUNNER_061_OUTPUT_GENERATION_FAILED"
    OUTPUT_VALIDATION_ERROR = "ONEX_NODE_SCENARIO_RUNNER_062_OUTPUT_VALIDATION_ERROR"
    OUTPUT_SERIALIZATION_ERROR = (
        "ONEX_NODE_SCENARIO_RUNNER_063_OUTPUT_SERIALIZATION_ERROR"
    )
    OUTPUT_FORMAT_ERROR = "ONEX_NODE_SCENARIO_RUNNER_064_OUTPUT_FORMAT_ERROR"

    # Configuration errors (081-100)
    INVALID_CONFIGURATION = "ONEX_NODE_SCENARIO_RUNNER_081_INVALID_CONFIGURATION"
    MISSING_REQUIRED_PARAMETER = (
        "ONEX_NODE_SCENARIO_RUNNER_082_MISSING_REQUIRED_PARAMETER"
    )
    UNSUPPORTED_OPERATION = "ONEX_NODE_SCENARIO_RUNNER_083_UNSUPPORTED_OPERATION"
    NODE_SCENARIO_RUNNER_VERSION_MISMATCH = (
        "ONEX_NODE_SCENARIO_RUNNER_084_NODE_SCENARIO_RUNNER_VERSION_MISMATCH"
    )

    def get_component(self) -> str:
        """Get the component identifier for this error code."""
        return "NODE_SCENARIO_RUNNER"

    def get_number(self) -> int:
        """Get the numeric identifier for this error code."""
        # Extract number from error code string (e.g., "ONEX_NODE_SCENARIO_RUNNER_001_..." -> 1)
        match = re.search(r"ONEX_NODE_SCENARIO_RUNNER_(\d+)_", self.value)
        return int(match.group(1)) if match else 0

    def get_description(self) -> str:
        """Get a human-readable description for this error code."""
        return get_error_description(self)

    def get_exit_code(self) -> int:
        """Get the appropriate CLI exit code for this error."""
        return get_exit_code_for_error(self)


# Mapping from error codes to exit codes (for specific error handling)
ERROR_CODE_TO_EXIT_CODE: Dict[NodeScenarioRunnerErrorCode, CLIExitCode] = {
    # Input validation errors -> ERROR
    NodeScenarioRunnerErrorCode.INVALID_REQUIRED_FIELD: CLIExitCode.ERROR,
    NodeScenarioRunnerErrorCode.MISSING_REQUIRED_FIELD: CLIExitCode.ERROR,
    NodeScenarioRunnerErrorCode.INVALID_OPTIONAL_FIELD: CLIExitCode.ERROR,
    NodeScenarioRunnerErrorCode.FIELD_VALIDATION_ERROR: CLIExitCode.ERROR,
    # Processing errors -> ERROR
    NodeScenarioRunnerErrorCode.NODE_SCENARIO_RUNNER_PROCESSING_FAILED: CLIExitCode.ERROR,
    NodeScenarioRunnerErrorCode.NODE_SCENARIO_RUNNER_EXECUTION_ERROR: CLIExitCode.ERROR,
    NodeScenarioRunnerErrorCode.NODE_SCENARIO_RUNNER_LOGIC_ERROR: CLIExitCode.ERROR,
    NodeScenarioRunnerErrorCode.NODE_SCENARIO_RUNNER_TIMEOUT: CLIExitCode.ERROR,
    # Handler errors -> ERROR
    NodeScenarioRunnerErrorCode.HANDLER_NOT_FOUND: CLIExitCode.ERROR,
    NodeScenarioRunnerErrorCode.HANDLER_INITIALIZATION_FAILED: CLIExitCode.ERROR,
    NodeScenarioRunnerErrorCode.HANDLER_EXECUTION_FAILED: CLIExitCode.ERROR,
    NodeScenarioRunnerErrorCode.HANDLER_REGISTRY_ERROR: CLIExitCode.ERROR,
    # Output errors -> WARNING (may be recoverable)
    NodeScenarioRunnerErrorCode.OUTPUT_GENERATION_FAILED: CLIExitCode.WARNING,
    NodeScenarioRunnerErrorCode.OUTPUT_VALIDATION_ERROR: CLIExitCode.WARNING,
    NodeScenarioRunnerErrorCode.OUTPUT_SERIALIZATION_ERROR: CLIExitCode.WARNING,
    NodeScenarioRunnerErrorCode.OUTPUT_FORMAT_ERROR: CLIExitCode.WARNING,
    # Configuration errors -> ERROR
    NodeScenarioRunnerErrorCode.INVALID_CONFIGURATION: CLIExitCode.ERROR,
    NodeScenarioRunnerErrorCode.MISSING_REQUIRED_PARAMETER: CLIExitCode.ERROR,
    NodeScenarioRunnerErrorCode.UNSUPPORTED_OPERATION: CLIExitCode.ERROR,
    NodeScenarioRunnerErrorCode.NODE_SCENARIO_RUNNER_VERSION_MISMATCH: CLIExitCode.ERROR,
}


def get_exit_code_for_error(error_code: NodeScenarioRunnerErrorCode) -> int:
    """
    Get the appropriate CLI exit code for a specific error code.

    Args:
        error_code: The NodeScenarioRunnerErrorCode to map

    Returns:
        The corresponding CLI exit code (integer)

    Example:
        >>> get_exit_code_for_error(NodeScenarioRunnerErrorCode.MISSING_REQUIRED_FIELD)
        1
        >>> get_exit_code_for_error(NodeScenarioRunnerErrorCode.OUTPUT_VALIDATION_ERROR)
        2
    """
    return ERROR_CODE_TO_EXIT_CODE.get(error_code, CLIExitCode.ERROR).value


def get_error_description(error_code: NodeScenarioRunnerErrorCode) -> str:
    """
    Get a human-readable description for an error code.

    Args:
        error_code: The NodeScenarioRunnerErrorCode to describe

    Returns:
        A human-readable description of the error
    """
    descriptions = {
        NodeScenarioRunnerErrorCode.INVALID_REQUIRED_FIELD: "Invalid required field value",
        NodeScenarioRunnerErrorCode.MISSING_REQUIRED_FIELD: "Missing required field",
        NodeScenarioRunnerErrorCode.INVALID_OPTIONAL_FIELD: "Invalid optional field value",
        NodeScenarioRunnerErrorCode.FIELD_VALIDATION_ERROR: "Field validation failed",
        NodeScenarioRunnerErrorCode.NODE_SCENARIO_RUNNER_PROCESSING_FAILED: "NodeScenarioRunner processing failed",
        NodeScenarioRunnerErrorCode.NODE_SCENARIO_RUNNER_EXECUTION_ERROR: "NodeScenarioRunner execution error",
        NodeScenarioRunnerErrorCode.NODE_SCENARIO_RUNNER_LOGIC_ERROR: "NodeScenarioRunner logic error",
        NodeScenarioRunnerErrorCode.NODE_SCENARIO_RUNNER_TIMEOUT: "NodeScenarioRunner execution timeout",
        NodeScenarioRunnerErrorCode.HANDLER_NOT_FOUND: "No handler for file type",
        NodeScenarioRunnerErrorCode.HANDLER_INITIALIZATION_FAILED: "Handler initialization failed",
        NodeScenarioRunnerErrorCode.HANDLER_EXECUTION_FAILED: "Handler execution failed",
        NodeScenarioRunnerErrorCode.HANDLER_REGISTRY_ERROR: "Handler registry error",
        NodeScenarioRunnerErrorCode.OUTPUT_GENERATION_FAILED: "Output generation failed",
        NodeScenarioRunnerErrorCode.OUTPUT_VALIDATION_ERROR: "Output validation failed",
        NodeScenarioRunnerErrorCode.OUTPUT_SERIALIZATION_ERROR: "Output serialization failed",
        NodeScenarioRunnerErrorCode.OUTPUT_FORMAT_ERROR: "Output format error",
        NodeScenarioRunnerErrorCode.INVALID_CONFIGURATION: "Invalid configuration",
        NodeScenarioRunnerErrorCode.MISSING_REQUIRED_PARAMETER: "Required parameter missing",
        NodeScenarioRunnerErrorCode.UNSUPPORTED_OPERATION: "Operation not supported",
        NodeScenarioRunnerErrorCode.NODE_SCENARIO_RUNNER_VERSION_MISMATCH: "NodeScenarioRunner version incompatible",
    }
    return descriptions.get(error_code, "Unknown error")


class NodeScenarioRunnerError(OnexError):
    """Base exception class for node_scenario_runner node errors with error code support."""

    def __init__(
        self, message: str, error_code: NodeScenarioRunnerErrorCode, **kwargs: Any
    ) -> None:
        """
        Initialize a node_scenario_runner error with error code.

        Args:
            message: Human-readable error message
            error_code: Canonical error code
            **kwargs: Additional context information
        """
        super().__init__(message, error_code=error_code, **kwargs)


# Specific exception classes for different error categories
class NodeScenarioRunnerInputError(NodeScenarioRunnerError):
    """Input validation related errors."""

    pass


class NodeScenarioRunnerProcessingError(NodeScenarioRunnerError):
    """NodeScenarioRunner processing related errors."""

    pass


class NodeScenarioRunnerHandlerError(NodeScenarioRunnerError):
    """Handler related errors."""

    pass


class NodeScenarioRunnerOutputError(NodeScenarioRunnerError):
    """Output related errors."""

    pass


class NodeScenarioRunnerConfigurationError(NodeScenarioRunnerError):
    """Configuration related errors."""

    pass


# Register node_scenario_runner error codes with the global registry

register_error_codes("node_scenario_runner", NodeScenarioRunnerErrorCode)
