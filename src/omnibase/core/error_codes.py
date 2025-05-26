# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: error_codes.py
# version: 1.0.0
# uuid: 4dbf1549-9218-47b6-9188-3589104a38f5
# author: OmniNode Team
# created_at: 2025-05-25T16:50:14.043960
# last_modified_at: 2025-05-25T22:11:50.165848
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 2169ab95a8612c7ab87a2015a94c9d110046d8d9d45d76142fe96ae4a00c114a
# entrypoint: python@error_codes.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.error_codes
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

from enum import Enum
from typing import Any, Dict, Type, Union

from omnibase.model.enum_onex_status import OnexStatus


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


class OnexError(Exception):
    """
    Base exception class for ONEX errors with error code support.

    All ONEX nodes should use this or subclasses for error handling
    to ensure consistent error reporting and CLI exit code mapping.
    """

    def __init__(
        self,
        message: str,
        error_code: Union[OnexErrorCode, str, None] = None,
        status: OnexStatus = OnexStatus.ERROR,
        **kwargs: Any,
    ) -> None:
        """
        Initialize an ONEX error with error code and status.

        Args:
            message: Human-readable error message
            error_code: Canonical error code (optional)
            status: OnexStatus for this error (default: ERROR)
            **kwargs: Additional context information
        """
        super().__init__(message)
        self.error_code = error_code
        self.status = status
        self.context = kwargs

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
            return f"[{error_code_str}] {super().__str__()}"
        return super().__str__()


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
        import sys

        exit_code = get_exit_code_for_status(status)

        if message:
            if status in (OnexStatus.ERROR, OnexStatus.UNKNOWN):
                print(f"ERROR: {message}", file=sys.stderr)
            elif status == OnexStatus.WARNING:
                print(f"WARNING: {message}", file=sys.stderr)
            else:
                print(message)

        sys.exit(exit_code)

    @staticmethod
    def exit_with_error(error: OnexError) -> None:
        """
        Exit the CLI with the appropriate exit code for the given error.

        Args:
            error: The OnexError to handle
        """
        import sys

        exit_code = error.get_exit_code()
        print(f"ERROR: {error}", file=sys.stderr)
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
        KeyError: If component is not registered
    """
    if component not in _ERROR_CODE_REGISTRIES:
        raise KeyError(f"No error codes registered for component: {component}")
    return _ERROR_CODE_REGISTRIES[component]


def list_registered_components() -> list[str]:
    """
    List all registered component identifiers.

    Returns:
        List of component identifiers that have registered error codes
    """
    return list(_ERROR_CODE_REGISTRIES.keys())
