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
# namespace: python://omnibase.nodes.node_registry_node.v1_0_0.error_codes
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
Error codes and exit code mapping for node_registry node.

This module defines canonical error codes for the node_registry node and provides
mapping functionality to convert OnexStatus values to appropriate CLI exit codes.

Exit Code Conventions:
- 0: Success (OnexStatus.SUCCESS)
- 1: General error (OnexStatus.ERROR, OnexStatus.UNKNOWN)
- 2: Warning (OnexStatus.WARNING)
- 3: Partial success (OnexStatus.PARTIAL)
- 4: Skipped (OnexStatus.SKIPPED)
- 5: Fixed (OnexStatus.FIXED)
- 6: Info (OnexStatus.INFO)

Error Code Format: ONEX_NODE_REGISTRY_<NUMBER>_<DESCRIPTION>
"""

import re
from typing import Any, Dict

from omnibase.core.core_error_codes import (
    CLIExitCode,
    OnexError,
    OnexErrorCode,
    register_error_codes,
)


class NodeRegistryErrorCode(OnexErrorCode):
    """Canonical error codes for node_registry node operations."""

    # Input validation errors (001-020)
    INVALID_REQUIRED_FIELD = "ONEX_NODE_REGISTRY_001_INVALID_REQUIRED_FIELD"
    MISSING_REQUIRED_FIELD = "ONEX_NODE_REGISTRY_002_MISSING_REQUIRED_FIELD"
    INVALID_OPTIONAL_FIELD = "ONEX_NODE_REGISTRY_003_INVALID_OPTIONAL_FIELD"
    FIELD_VALIDATION_ERROR = "ONEX_NODE_REGISTRY_004_FIELD_VALIDATION_ERROR"

    # Processing errors (021-040)
    NODE_REGISTRY_PROCESSING_FAILED = (
        "ONEX_NODE_REGISTRY_021_NODE_REGISTRY_PROCESSING_FAILED"
    )
    NODE_REGISTRY_EXECUTION_ERROR = (
        "ONEX_NODE_REGISTRY_022_NODE_REGISTRY_EXECUTION_ERROR"
    )
    NODE_REGISTRY_LOGIC_ERROR = "ONEX_NODE_REGISTRY_023_NODE_REGISTRY_LOGIC_ERROR"
    NODE_REGISTRY_TIMEOUT = "ONEX_NODE_REGISTRY_024_NODE_REGISTRY_TIMEOUT"

    # Handler errors (041-060)
    HANDLER_NOT_FOUND = "ONEX_NODE_REGISTRY_041_HANDLER_NOT_FOUND"
    HANDLER_INITIALIZATION_FAILED = (
        "ONEX_NODE_REGISTRY_042_HANDLER_INITIALIZATION_FAILED"
    )
    HANDLER_EXECUTION_FAILED = "ONEX_NODE_REGISTRY_043_HANDLER_EXECUTION_FAILED"
    HANDLER_REGISTRY_ERROR = "ONEX_NODE_REGISTRY_044_HANDLER_REGISTRY_ERROR"

    # Output errors (061-080)
    OUTPUT_GENERATION_FAILED = "ONEX_NODE_REGISTRY_061_OUTPUT_GENERATION_FAILED"
    OUTPUT_VALIDATION_ERROR = "ONEX_NODE_REGISTRY_062_OUTPUT_VALIDATION_ERROR"
    OUTPUT_SERIALIZATION_ERROR = "ONEX_NODE_REGISTRY_063_OUTPUT_SERIALIZATION_ERROR"
    OUTPUT_FORMAT_ERROR = "ONEX_NODE_REGISTRY_064_OUTPUT_FORMAT_ERROR"

    # Configuration errors (081-100)
    INVALID_CONFIGURATION = "ONEX_NODE_REGISTRY_081_INVALID_CONFIGURATION"
    MISSING_REQUIRED_PARAMETER = "ONEX_NODE_REGISTRY_082_MISSING_REQUIRED_PARAMETER"
    UNSUPPORTED_OPERATION = "ONEX_NODE_REGISTRY_083_UNSUPPORTED_OPERATION"
    NODE_REGISTRY_VERSION_MISMATCH = (
        "ONEX_NODE_REGISTRY_084_NODE_REGISTRY_VERSION_MISMATCH"
    )

    def get_component(self) -> str:
        """Get the component identifier for this error code."""
        return "NODE_REGISTRY"

    def get_number(self) -> int:
        """Get the numeric identifier for this error code."""
        # Extract number from error code string (e.g., "ONEX_NODE_REGISTRY_001_..." -> 1)
        match = re.search(r"ONEX_NODE_REGISTRY_(\d+)_", self.value)
        return int(match.group(1)) if match else 0

    def get_description(self) -> str:
        """Get a human-readable description for this error code."""
        return get_error_description(self)

    def get_exit_code(self) -> int:
        """Get the appropriate CLI exit code for this error."""
        return get_exit_code_for_error(self)


# Mapping from error codes to exit codes (for specific error handling)
ERROR_CODE_TO_EXIT_CODE: Dict[NodeRegistryErrorCode, CLIExitCode] = {
    # Input validation errors -> ERROR
    NodeRegistryErrorCode.INVALID_REQUIRED_FIELD: CLIExitCode.ERROR,
    NodeRegistryErrorCode.MISSING_REQUIRED_FIELD: CLIExitCode.ERROR,
    NodeRegistryErrorCode.INVALID_OPTIONAL_FIELD: CLIExitCode.ERROR,
    NodeRegistryErrorCode.FIELD_VALIDATION_ERROR: CLIExitCode.ERROR,
    # Processing errors -> ERROR
    NodeRegistryErrorCode.NODE_REGISTRY_PROCESSING_FAILED: CLIExitCode.ERROR,
    NodeRegistryErrorCode.NODE_REGISTRY_EXECUTION_ERROR: CLIExitCode.ERROR,
    NodeRegistryErrorCode.NODE_REGISTRY_LOGIC_ERROR: CLIExitCode.ERROR,
    NodeRegistryErrorCode.NODE_REGISTRY_TIMEOUT: CLIExitCode.ERROR,
    # Handler errors -> ERROR
    NodeRegistryErrorCode.HANDLER_NOT_FOUND: CLIExitCode.ERROR,
    NodeRegistryErrorCode.HANDLER_INITIALIZATION_FAILED: CLIExitCode.ERROR,
    NodeRegistryErrorCode.HANDLER_EXECUTION_FAILED: CLIExitCode.ERROR,
    NodeRegistryErrorCode.HANDLER_REGISTRY_ERROR: CLIExitCode.ERROR,
    # Output errors -> WARNING (may be recoverable)
    NodeRegistryErrorCode.OUTPUT_GENERATION_FAILED: CLIExitCode.WARNING,
    NodeRegistryErrorCode.OUTPUT_VALIDATION_ERROR: CLIExitCode.WARNING,
    NodeRegistryErrorCode.OUTPUT_SERIALIZATION_ERROR: CLIExitCode.WARNING,
    NodeRegistryErrorCode.OUTPUT_FORMAT_ERROR: CLIExitCode.WARNING,
    # Configuration errors -> ERROR
    NodeRegistryErrorCode.INVALID_CONFIGURATION: CLIExitCode.ERROR,
    NodeRegistryErrorCode.MISSING_REQUIRED_PARAMETER: CLIExitCode.ERROR,
    NodeRegistryErrorCode.UNSUPPORTED_OPERATION: CLIExitCode.ERROR,
    NodeRegistryErrorCode.NODE_REGISTRY_VERSION_MISMATCH: CLIExitCode.ERROR,
}


def get_exit_code_for_error(error_code: NodeRegistryErrorCode) -> int:
    """
    Get the appropriate CLI exit code for a specific error code.

    Args:
        error_code: The NodeRegistryErrorCode to map

    Returns:
        The corresponding CLI exit code (integer)

    Example:
        >>> get_exit_code_for_error(NodeRegistryErrorCode.MISSING_REQUIRED_FIELD)
        1
        >>> get_exit_code_for_error(NodeRegistryErrorCode.OUTPUT_VALIDATION_ERROR)
        2
    """
    return ERROR_CODE_TO_EXIT_CODE.get(error_code, CLIExitCode.ERROR).value


def get_error_description(error_code: NodeRegistryErrorCode) -> str:
    """
    Get a human-readable description for an error code.

    Args:
        error_code: The NodeRegistryErrorCode to describe

    Returns:
        A human-readable description of the error
    """
    descriptions = {
        NodeRegistryErrorCode.INVALID_REQUIRED_FIELD: "Invalid required field value",
        NodeRegistryErrorCode.MISSING_REQUIRED_FIELD: "Missing required field",
        NodeRegistryErrorCode.INVALID_OPTIONAL_FIELD: "Invalid optional field value",
        NodeRegistryErrorCode.FIELD_VALIDATION_ERROR: "Field validation failed",
        NodeRegistryErrorCode.NODE_REGISTRY_PROCESSING_FAILED: "NodeRegistry processing failed",
        NodeRegistryErrorCode.NODE_REGISTRY_EXECUTION_ERROR: "NodeRegistry execution error",
        NodeRegistryErrorCode.NODE_REGISTRY_LOGIC_ERROR: "NodeRegistry logic error",
        NodeRegistryErrorCode.NODE_REGISTRY_TIMEOUT: "NodeRegistry execution timeout",
        NodeRegistryErrorCode.HANDLER_NOT_FOUND: "No handler for file type",
        NodeRegistryErrorCode.HANDLER_INITIALIZATION_FAILED: "Handler initialization failed",
        NodeRegistryErrorCode.HANDLER_EXECUTION_FAILED: "Handler execution failed",
        NodeRegistryErrorCode.HANDLER_REGISTRY_ERROR: "Handler registry error",
        NodeRegistryErrorCode.OUTPUT_GENERATION_FAILED: "Output generation failed",
        NodeRegistryErrorCode.OUTPUT_VALIDATION_ERROR: "Output validation failed",
        NodeRegistryErrorCode.OUTPUT_SERIALIZATION_ERROR: "Output serialization failed",
        NodeRegistryErrorCode.OUTPUT_FORMAT_ERROR: "Output format error",
        NodeRegistryErrorCode.INVALID_CONFIGURATION: "Invalid configuration",
        NodeRegistryErrorCode.MISSING_REQUIRED_PARAMETER: "Required parameter missing",
        NodeRegistryErrorCode.UNSUPPORTED_OPERATION: "Operation not supported",
        NodeRegistryErrorCode.NODE_REGISTRY_VERSION_MISMATCH: "NodeRegistry version incompatible",
    }
    return descriptions.get(error_code, "Unknown error")


class NodeRegistryError(OnexError):
    """Base exception class for node_registry node errors with error code support."""

    def __init__(
        self, message: str, error_code: NodeRegistryErrorCode, **kwargs: Any
    ) -> None:
        """
        Initialize a node_registry error with error code.

        Args:
            message: Human-readable error message
            error_code: Canonical error code
            **kwargs: Additional context information
        """
        super().__init__(message, error_code=error_code, **kwargs)


# Specific exception classes for different error categories
class NodeRegistryInputError(NodeRegistryError):
    """Input validation related errors."""

    pass


class NodeRegistryProcessingError(NodeRegistryError):
    """NodeRegistry processing related errors."""

    pass


class NodeRegistryHandlerError(NodeRegistryError):
    """Handler related errors."""

    pass


class NodeRegistryOutputError(NodeRegistryError):
    """Output related errors."""

    pass


class NodeRegistryConfigurationError(NodeRegistryError):
    """Configuration related errors."""

    pass


# Register node_registry error codes with the global registry

register_error_codes("node_registry", NodeRegistryErrorCode)
