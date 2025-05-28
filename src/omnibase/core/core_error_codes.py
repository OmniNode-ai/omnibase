# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: core_error_codes.py
# version: 1.0.0
# uuid: e5028d69-3575-43b8-8691-6ce5b343b43b
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.416682
# last_modified_at: 2025-05-28T17:20:04.229167
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 44a3038f4bf99ed65b011dee06bb84f94107f9bf96e25ec3e3e7b42195742824
# entrypoint: python@core_error_codes.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.core_error_codes
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Shared error codes and exit code mapping for all ONEX nodes.

This module provides the foundation for consistent error handling and CLI exit
code mapping across the entire ONEX ecosystem. All nodes should use these
patterns for error handling and CLI integration.

Exit Code Conventions:
- 0: Success (OnexStatus.SUCCESS)
- 1: General error (OnexStatus.ERROR, OnexStatus.UNKNOWN)
- 2: Warning (OnexStatus.WARNING)
- 3: Partial success (OnexStatus.PARTIAL)
- 4: Skipped (OnexStatus.SKIPPED)
- 5: Fixed (OnexStatus.FIXED)
- 6: Info (OnexStatus.INFO)

Error Code Format: ONEX_<COMPONENT>_<NUMBER>_<DESCRIPTION>
"""

import re
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Type, Union

from pydantic import BaseModel, ConfigDict, Field

from omnibase.enums import OnexStatus

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class CLIExitCode(int, Enum):
    """Standard CLI exit codes for ONEX operations."""

    SUCCESS = 0
    ERROR = 1
    WARNING = 2
    PARTIAL = 3
    SKIPPED = 4
    FIXED = 5
    INFO = 6


# Global mapping from OnexStatus to CLI exit codes
STATUS_TO_EXIT_CODE: Dict[OnexStatus, CLIExitCode] = {
    OnexStatus.SUCCESS: CLIExitCode.SUCCESS,
    OnexStatus.ERROR: CLIExitCode.ERROR,
    OnexStatus.WARNING: CLIExitCode.WARNING,
    OnexStatus.PARTIAL: CLIExitCode.PARTIAL,
    OnexStatus.SKIPPED: CLIExitCode.SKIPPED,
    OnexStatus.FIXED: CLIExitCode.FIXED,
    OnexStatus.INFO: CLIExitCode.INFO,
    OnexStatus.UNKNOWN: CLIExitCode.ERROR,  # Treat unknown as error
}


def get_exit_code_for_status(status: OnexStatus) -> int:
    """
    Get the appropriate CLI exit code for an OnexStatus.

    This is the canonical function for mapping OnexStatus values to CLI exit codes
    across all ONEX nodes and tools.

    Args:
        status: The OnexStatus to map

    Returns:
        The corresponding CLI exit code (integer)

    Example:
        >>> get_exit_code_for_status(OnexStatus.SUCCESS)
        0
        >>> get_exit_code_for_status(OnexStatus.ERROR)
        1
        >>> get_exit_code_for_status(OnexStatus.WARNING)
        2
    """
    return STATUS_TO_EXIT_CODE.get(status, CLIExitCode.ERROR).value


class OnexErrorCode(str, Enum):
    """
    Base class for ONEX error codes.

    All node-specific error code enums should inherit from this class
    to ensure consistent behavior and interface.

    Subclasses should implement the abstract methods to provide
    component-specific information.
    """

    def get_component(self) -> str:
        """Get the component identifier for this error code."""
        raise NotImplementedError("Subclasses must implement get_component()")

    def get_number(self) -> int:
        """Get the numeric identifier for this error code."""
        raise NotImplementedError("Subclasses must implement get_number()")

    def get_description(self) -> str:
        """Get a human-readable description for this error code."""
        raise NotImplementedError("Subclasses must implement get_description()")

    def get_exit_code(self) -> int:
        """
        Get the appropriate CLI exit code for this error.

        Default implementation returns ERROR (1). Subclasses can override
        for more specific mapping.
        """
        return CLIExitCode.ERROR.value


class CoreErrorCode(OnexErrorCode):
    """
    Core error codes that can be reused across all ONEX components.

    These provide common error patterns that don't need to be redefined
    in each node's error_codes.py module.
    """

    # Generic validation errors (001-020)
    INVALID_PARAMETER = "ONEX_CORE_001_INVALID_PARAMETER"
    MISSING_REQUIRED_PARAMETER = "ONEX_CORE_002_MISSING_REQUIRED_PARAMETER"
    PARAMETER_TYPE_MISMATCH = "ONEX_CORE_003_PARAMETER_TYPE_MISMATCH"
    PARAMETER_OUT_OF_RANGE = "ONEX_CORE_004_PARAMETER_OUT_OF_RANGE"
    VALIDATION_FAILED = "ONEX_CORE_005_VALIDATION_FAILED"
    VALIDATION_ERROR = "ONEX_CORE_006_VALIDATION_ERROR"

    # File system errors (021-040)
    FILE_NOT_FOUND = "ONEX_CORE_021_FILE_NOT_FOUND"
    FILE_READ_ERROR = "ONEX_CORE_022_FILE_READ_ERROR"
    FILE_WRITE_ERROR = "ONEX_CORE_023_FILE_WRITE_ERROR"
    DIRECTORY_NOT_FOUND = "ONEX_CORE_024_DIRECTORY_NOT_FOUND"
    PERMISSION_DENIED = "ONEX_CORE_025_PERMISSION_DENIED"

    # Configuration errors (041-060)
    INVALID_CONFIGURATION = "ONEX_CORE_041_INVALID_CONFIGURATION"
    CONFIGURATION_NOT_FOUND = "ONEX_CORE_042_CONFIGURATION_NOT_FOUND"
    CONFIGURATION_PARSE_ERROR = "ONEX_CORE_043_CONFIGURATION_PARSE_ERROR"

    # Registry errors (061-080)
    REGISTRY_NOT_FOUND = "ONEX_CORE_061_REGISTRY_NOT_FOUND"
    REGISTRY_INITIALIZATION_FAILED = "ONEX_CORE_062_REGISTRY_INITIALIZATION_FAILED"
    ITEM_NOT_REGISTERED = "ONEX_CORE_063_ITEM_NOT_REGISTERED"
    DUPLICATE_REGISTRATION = "ONEX_CORE_064_DUPLICATE_REGISTRATION"

    # Runtime errors (081-100)
    OPERATION_FAILED = "ONEX_CORE_081_OPERATION_FAILED"
    TIMEOUT_EXCEEDED = "ONEX_CORE_082_TIMEOUT_EXCEEDED"
    RESOURCE_UNAVAILABLE = "ONEX_CORE_083_RESOURCE_UNAVAILABLE"
    UNSUPPORTED_OPERATION = "ONEX_CORE_084_UNSUPPORTED_OPERATION"
    RESOURCE_NOT_FOUND = "ONEX_CORE_085_RESOURCE_NOT_FOUND"
    INVALID_STATE = "ONEX_CORE_086_INVALID_STATE"

    # Test and development errors (101-120)
    TEST_SETUP_FAILED = "ONEX_CORE_101_TEST_SETUP_FAILED"
    TEST_ASSERTION_FAILED = "ONEX_CORE_102_TEST_ASSERTION_FAILED"
    MOCK_CONFIGURATION_ERROR = "ONEX_CORE_103_MOCK_CONFIGURATION_ERROR"
    TEST_DATA_INVALID = "ONEX_CORE_104_TEST_DATA_INVALID"

    # Import and dependency errors (121-140)
    MODULE_NOT_FOUND = "ONEX_CORE_121_MODULE_NOT_FOUND"
    DEPENDENCY_UNAVAILABLE = "ONEX_CORE_122_DEPENDENCY_UNAVAILABLE"
    VERSION_INCOMPATIBLE = "ONEX_CORE_123_VERSION_INCOMPATIBLE"

    # Abstract method and implementation errors (141-160)
    METHOD_NOT_IMPLEMENTED = "ONEX_CORE_141_METHOD_NOT_IMPLEMENTED"
    ABSTRACT_METHOD_CALLED = "ONEX_CORE_142_ABSTRACT_METHOD_CALLED"

    def get_component(self) -> str:
        """Get the component identifier for this error code."""
        return "CORE"

    def get_number(self) -> int:
        """Get the numeric identifier for this error code."""
        # Extract number from error code string (e.g., "ONEX_CORE_001_..." -> 1)
        match = re.search(r"ONEX_CORE_(\d+)_", self.value)
        return int(match.group(1)) if match else 0

    def get_description(self) -> str:
        """Get a human-readable description for this error code."""
        return get_core_error_description(self)

    def get_exit_code(self) -> int:
        """Get the appropriate CLI exit code for this error."""
        return get_exit_code_for_core_error(self)


# Mapping from core error codes to exit codes
CORE_ERROR_CODE_TO_EXIT_CODE: Dict[CoreErrorCode, CLIExitCode] = {
    # Validation errors -> ERROR
    CoreErrorCode.INVALID_PARAMETER: CLIExitCode.ERROR,
    CoreErrorCode.MISSING_REQUIRED_PARAMETER: CLIExitCode.ERROR,
    CoreErrorCode.PARAMETER_TYPE_MISMATCH: CLIExitCode.ERROR,
    CoreErrorCode.PARAMETER_OUT_OF_RANGE: CLIExitCode.ERROR,
    CoreErrorCode.VALIDATION_FAILED: CLIExitCode.ERROR,
    # File system errors -> ERROR
    CoreErrorCode.FILE_NOT_FOUND: CLIExitCode.ERROR,
    CoreErrorCode.FILE_READ_ERROR: CLIExitCode.ERROR,
    CoreErrorCode.FILE_WRITE_ERROR: CLIExitCode.ERROR,
    CoreErrorCode.DIRECTORY_NOT_FOUND: CLIExitCode.ERROR,
    CoreErrorCode.PERMISSION_DENIED: CLIExitCode.ERROR,
    # Configuration errors -> ERROR
    CoreErrorCode.INVALID_CONFIGURATION: CLIExitCode.ERROR,
    CoreErrorCode.CONFIGURATION_NOT_FOUND: CLIExitCode.ERROR,
    CoreErrorCode.CONFIGURATION_PARSE_ERROR: CLIExitCode.ERROR,
    # Registry errors -> ERROR
    CoreErrorCode.REGISTRY_NOT_FOUND: CLIExitCode.ERROR,
    CoreErrorCode.REGISTRY_INITIALIZATION_FAILED: CLIExitCode.ERROR,
    CoreErrorCode.ITEM_NOT_REGISTERED: CLIExitCode.ERROR,
    CoreErrorCode.DUPLICATE_REGISTRATION: CLIExitCode.WARNING,
    # Runtime errors -> ERROR
    CoreErrorCode.OPERATION_FAILED: CLIExitCode.ERROR,
    CoreErrorCode.TIMEOUT_EXCEEDED: CLIExitCode.ERROR,
    CoreErrorCode.RESOURCE_UNAVAILABLE: CLIExitCode.ERROR,
    CoreErrorCode.UNSUPPORTED_OPERATION: CLIExitCode.ERROR,
    CoreErrorCode.RESOURCE_NOT_FOUND: CLIExitCode.ERROR,
    CoreErrorCode.INVALID_STATE: CLIExitCode.ERROR,
}


def get_exit_code_for_core_error(error_code: CoreErrorCode) -> int:
    """
    Get the appropriate CLI exit code for a core error code.

    Args:
        error_code: The CoreErrorCode to map

    Returns:
        The corresponding CLI exit code (integer)
    """
    return CORE_ERROR_CODE_TO_EXIT_CODE.get(error_code, CLIExitCode.ERROR).value


def get_core_error_description(error_code: CoreErrorCode) -> str:
    """
    Get a human-readable description for a core error code.

    Args:
        error_code: The CoreErrorCode to describe

    Returns:
        A human-readable description of the error
    """
    descriptions = {
        CoreErrorCode.INVALID_PARAMETER: "Invalid parameter value",
        CoreErrorCode.MISSING_REQUIRED_PARAMETER: "Required parameter missing",
        CoreErrorCode.PARAMETER_TYPE_MISMATCH: "Parameter type mismatch",
        CoreErrorCode.PARAMETER_OUT_OF_RANGE: "Parameter value out of range",
        CoreErrorCode.VALIDATION_FAILED: "Validation failed",
        CoreErrorCode.FILE_NOT_FOUND: "File not found",
        CoreErrorCode.FILE_READ_ERROR: "Cannot read file",
        CoreErrorCode.FILE_WRITE_ERROR: "Cannot write file",
        CoreErrorCode.DIRECTORY_NOT_FOUND: "Directory not found",
        CoreErrorCode.PERMISSION_DENIED: "Permission denied",
        CoreErrorCode.INVALID_CONFIGURATION: "Invalid configuration",
        CoreErrorCode.CONFIGURATION_NOT_FOUND: "Configuration not found",
        CoreErrorCode.CONFIGURATION_PARSE_ERROR: "Configuration parse error",
        CoreErrorCode.REGISTRY_NOT_FOUND: "Registry not found",
        CoreErrorCode.REGISTRY_INITIALIZATION_FAILED: "Registry initialization failed",
        CoreErrorCode.ITEM_NOT_REGISTERED: "Item not registered",
        CoreErrorCode.DUPLICATE_REGISTRATION: "Duplicate registration",
        CoreErrorCode.OPERATION_FAILED: "Operation failed",
        CoreErrorCode.TIMEOUT_EXCEEDED: "Timeout exceeded",
        CoreErrorCode.RESOURCE_UNAVAILABLE: "Resource unavailable",
        CoreErrorCode.UNSUPPORTED_OPERATION: "Unsupported operation",
        CoreErrorCode.RESOURCE_NOT_FOUND: "Resource not found",
        CoreErrorCode.INVALID_STATE: "Invalid state",
    }
    return descriptions.get(error_code, "Unknown error")


class OnexErrorModel(BaseModel):
    """
    Pydantic model for ONEX error serialization and validation.

    This model provides structured error information with validation,
    serialization, and schema generation capabilities.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "File not found: config.yaml",
                "error_code": "ONEX_CORE_021_FILE_NOT_FOUND",
                "status": "error",
                "correlation_id": "req-123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2025-05-25T22:30:00Z",
                "context": {"file_path": "/path/to/config.yaml"},
            }
        }
    )

    message: str = Field(
        ...,
        description="Human-readable error message",
        json_schema_extra={"example": "File not found: config.yaml"},
    )
    error_code: Optional[Union[str, OnexErrorCode]] = Field(
        default=None,
        description="Canonical error code for this error",
        json_schema_extra={"example": "ONEX_CORE_021_FILE_NOT_FOUND"},
    )
    status: OnexStatus = Field(
        default=OnexStatus.ERROR,
        description="OnexStatus for this error",
        json_schema_extra={"example": "error"},
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="Optional correlation ID for request tracking",
        json_schema_extra={"example": "req-123e4567-e89b-12d3-a456-426614174000"},
    )
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the error occurred",
        json_schema_extra={"example": "2025-05-25T22:30:00Z"},
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context information for the error",
        json_schema_extra={"example": {"file_path": "/path/to/config.yaml"}},
    )


class OnexError(Exception):
    """
    Exception class for ONEX errors with Pydantic model integration.

    This class combines standard Python exception behavior with Pydantic
    model features through composition, providing validation, serialization,
    and schema generation while maintaining exception compatibility.

    All ONEX nodes should use this or subclasses for error handling
    to ensure consistent error reporting and CLI exit code mapping.
    """

    def __init__(
        self,
        message: str,
        error_code: Union[OnexErrorCode, str, None] = None,
        status: OnexStatus = OnexStatus.ERROR,
        correlation_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        **context: Any,
    ) -> None:
        """
        Initialize an ONEX error with error code and status.

        Args:
            message: Human-readable error message
            error_code: Canonical error code (optional)
            status: OnexStatus for this error (default: ERROR)
            correlation_id: Optional correlation ID for request tracking
            timestamp: Optional timestamp (defaults to current time)
            **context: Additional context information
        """
        # Initialize the Exception
        super().__init__(message)

        # Create the Pydantic model for structured data
        self.model = OnexErrorModel(
            message=message,
            error_code=error_code,
            status=status,
            correlation_id=correlation_id,
            timestamp=timestamp or datetime.utcnow(),
            context=context,
        )

    @property
    def message(self) -> str:
        """Get the error message."""
        return self.model.message

    @property
    def error_code(self) -> Optional[Union[str, OnexErrorCode]]:
        """Get the error code."""
        return self.model.error_code

    @property
    def status(self) -> OnexStatus:
        """Get the error status."""
        return self.model.status

    @property
    def correlation_id(self) -> Optional[str]:
        """Get the correlation ID."""
        return self.model.correlation_id

    @property
    def timestamp(self) -> Optional[datetime]:
        """Get the timestamp."""
        return self.model.timestamp

    @property
    def context(self) -> Dict[str, Any]:
        """Get the context information."""
        return self.model.context

    def get_exit_code(self) -> int:
        """Get the appropriate CLI exit code for this error."""
        if isinstance(self.error_code, OnexErrorCode):
            return self.error_code.get_exit_code()
        return get_exit_code_for_status(self.status)

    def __str__(self) -> str:
        """String representation including error code if available."""
        if self.error_code:
            # Use .value to get the string value for OnexErrorCode enums
            error_code_str = (
                self.error_code.value
                if hasattr(self.error_code, "value")
                else str(self.error_code)
            )
            return f"[{error_code_str}] {self.message}"
        return self.message

    def model_dump(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return self.model.model_dump()

    def model_dump_json(self) -> str:
        """Convert error to JSON string for logging/telemetry."""
        return self.model.model_dump_json()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization (alias for model_dump)."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert error to JSON string for logging/telemetry (alias for model_dump_json)."""
        return self.model_dump_json()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OnexError":
        """Create OnexError from dictionary."""
        model = OnexErrorModel.model_validate(data)
        return cls(
            message=model.message,
            error_code=model.error_code,
            status=model.status,
            correlation_id=model.correlation_id,
            timestamp=model.timestamp,
            **model.context,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "OnexError":
        """Create OnexError from JSON string."""
        model = OnexErrorModel.model_validate_json(json_str)
        return cls(
            message=model.message,
            error_code=model.error_code,
            status=model.status,
            correlation_id=model.correlation_id,
            timestamp=model.timestamp,
            **model.context,
        )

    @classmethod
    def model_json_schema(cls) -> Dict[str, Any]:
        """Get the JSON schema for OnexError."""
        return OnexErrorModel.model_json_schema()


class CLIAdapter:
    """
    Base CLI adapter class that provides consistent exit code handling.

    All CLI adapters should inherit from this class or implement similar
    exit code mapping functionality.
    """

    @staticmethod
    def exit_with_status(status: OnexStatus, message: str = "") -> None:
        """
        Exit the CLI with the appropriate exit code for the given status.

        Args:
            status: The OnexStatus to map to an exit code
            message: Optional message to print before exiting
        """

        exit_code = get_exit_code_for_status(status)

        if message:
            if status in (OnexStatus.ERROR, OnexStatus.UNKNOWN):
                print(f"{_COMPONENT_NAME}: {message}", file=sys.stderr)
            elif status == OnexStatus.WARNING:
                print(f"{_COMPONENT_NAME}: {message}", file=sys.stderr)
            else:
                print(f"{_COMPONENT_NAME}: {message}", file=sys.stderr)

        sys.exit(exit_code)

    @staticmethod
    def exit_with_error(error: OnexError) -> None:
        """
        Exit the CLI with the appropriate exit code for the given error.

        Args:
            error: The OnexError to handle
        """

        exit_code = error.get_exit_code()
        print(f"{_COMPONENT_NAME}: {str(error)}", file=sys.stderr)
        sys.exit(exit_code)


# Registry for component-specific error code mappings
_ERROR_CODE_REGISTRIES: Dict[str, Type[OnexErrorCode]] = {}


def register_error_codes(component: str, error_code_enum: Type[OnexErrorCode]) -> None:
    """
    Register error codes for a specific component.

    Args:
        component: Component identifier (e.g., "stamper", "validator")
        error_code_enum: Error code enum class for the component
    """
    _ERROR_CODE_REGISTRIES[component] = error_code_enum


def get_error_codes_for_component(component: str) -> Type[OnexErrorCode]:
    """
    Get the error code enum for a specific component.

    Args:
        component: Component identifier

    Returns:
        The error code enum class for the component

    Raises:
        OnexError: If component is not registered
    """
    if component not in _ERROR_CODE_REGISTRIES:
        raise OnexError(
            f"No error codes registered for component: {component}",
            CoreErrorCode.ITEM_NOT_REGISTERED,
        )
    return _ERROR_CODE_REGISTRIES[component]


def list_registered_components() -> list[str]:
    """
    List all registered component identifiers.

    Returns:
        List of component identifiers that have registered error codes
    """
    return list(_ERROR_CODE_REGISTRIES.keys())
