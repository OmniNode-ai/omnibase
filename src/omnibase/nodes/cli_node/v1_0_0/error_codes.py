# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.753922'
# description: Stamped by PythonHandler
# entrypoint: python://error_codes
# hash: 8a5a8b9be460e1b4541764cbd1a990dae4539c260bbb28e3ec57af5b733db16c
# last_modified_at: '2025-05-29T14:13:58.985618+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: error_codes.py
# namespace: python://omnibase.nodes.cli_node.v1_0_0.error_codes
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: aa0826f6-7bea-4bee-9304-4a3a27b73cce
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
CLI Node Error Codes.

Error codes specific to the CLI node for command routing and node management.
"""

from typing import Dict, Optional

from omnibase.core.core_error_codes import (
    CoreErrorCode,
    OnexError,
    OnexErrorCode,
    register_error_codes,
)


class CLIErrorCode(OnexErrorCode):
    """
    Error codes specific to CLI node operations.

    All CLI error codes follow the pattern: ONEX_CLI_XXX_DESCRIPTION
    """

    # Command validation errors (001-020)
    UNKNOWN_COMMAND = "ONEX_CLI_001_UNKNOWN_COMMAND"
    MISSING_TARGET_NODE = "ONEX_CLI_002_MISSING_TARGET_NODE"
    INVALID_COMMAND_ARGS = "ONEX_CLI_003_INVALID_COMMAND_ARGS"
    INVALID_JSON_ARGS = "ONEX_CLI_004_INVALID_JSON_ARGS"

    # Node discovery and registration errors (021-040)
    NODE_NOT_FOUND = "ONEX_CLI_021_NODE_NOT_FOUND"
    NODE_IMPORT_FAILED = "ONEX_CLI_022_NODE_IMPORT_FAILED"
    NODE_REGISTRATION_FAILED = "ONEX_CLI_023_NODE_REGISTRATION_FAILED"
    DISCOVERY_SERVICE_UNAVAILABLE = "ONEX_CLI_024_DISCOVERY_SERVICE_UNAVAILABLE"

    # Node execution errors (041-060)
    NODE_EXECUTION_FAILED = "ONEX_CLI_041_NODE_EXECUTION_FAILED"
    NODE_MISSING_MAIN = "ONEX_CLI_042_NODE_MISSING_MAIN"
    NODE_INTROSPECTION_FAILED = "ONEX_CLI_043_NODE_INTROSPECTION_FAILED"
    NODE_TIMEOUT = "ONEX_CLI_044_NODE_TIMEOUT"

    # Event bus errors (061-080)
    EVENT_BUS_ERROR = "ONEX_CLI_061_EVENT_BUS_ERROR"
    EVENT_PUBLISH_FAILED = "ONEX_CLI_062_EVENT_PUBLISH_FAILED"
    EVENT_SUBSCRIPTION_FAILED = "ONEX_CLI_063_EVENT_SUBSCRIPTION_FAILED"

    # System errors (081-100)
    SYSTEM_INFO_UNAVAILABLE = "ONEX_CLI_081_SYSTEM_INFO_UNAVAILABLE"
    HANDLER_REGISTRY_ERROR = "ONEX_CLI_082_HANDLER_REGISTRY_ERROR"
    VERSION_RESOLVER_ERROR = "ONEX_CLI_083_VERSION_RESOLVER_ERROR"

    def get_number(self) -> int:
        """Extract the numeric code from the error code string."""
        try:
            # Extract number from format ONEX_CLI_XXX_...
            parts = self.value.split("_")
            if len(parts) >= 3:
                return int(parts[2])
        except (ValueError, IndexError):
            pass
        return 0

    def get_description(self) -> str:
        """Get human-readable description of the error."""
        descriptions: Dict[CLIErrorCode, str] = {
            CLIErrorCode.UNKNOWN_COMMAND: "Unknown or unsupported command",
            CLIErrorCode.MISSING_TARGET_NODE: "Target node is required for this command",
            CLIErrorCode.INVALID_COMMAND_ARGS: "Invalid command arguments provided",
            CLIErrorCode.INVALID_JSON_ARGS: "Invalid JSON format in node arguments",
            CLIErrorCode.NODE_NOT_FOUND: "Specified node not found in registry",
            CLIErrorCode.NODE_IMPORT_FAILED: "Failed to import target node module",
            CLIErrorCode.NODE_REGISTRATION_FAILED: "Failed to register node with CLI",
            CLIErrorCode.DISCOVERY_SERVICE_UNAVAILABLE: "Node discovery service is unavailable",
            CLIErrorCode.NODE_EXECUTION_FAILED: "Target node execution failed",
            CLIErrorCode.NODE_MISSING_MAIN: "Target node does not have a main() function",
            CLIErrorCode.NODE_INTROSPECTION_FAILED: "Failed to get node introspection data",
            CLIErrorCode.NODE_TIMEOUT: "Node execution timed out",
            CLIErrorCode.EVENT_BUS_ERROR: "Event bus operation failed",
            CLIErrorCode.EVENT_PUBLISH_FAILED: "Failed to publish event to event bus",
            CLIErrorCode.EVENT_SUBSCRIPTION_FAILED: "Failed to subscribe to event bus",
            CLIErrorCode.SYSTEM_INFO_UNAVAILABLE: "System information is unavailable",
            CLIErrorCode.HANDLER_REGISTRY_ERROR: "File type handler registry error",
            CLIErrorCode.VERSION_RESOLVER_ERROR: "Version resolver operation failed",
        }
        return descriptions.get(self, "Unknown CLI error")

    def get_exit_code(self) -> int:
        """Get the exit code for this error."""
        # Map error categories to exit codes
        error_number = self.get_number()

        if 1 <= error_number <= 20:  # Command validation errors
            return 2
        elif 21 <= error_number <= 40:  # Node discovery errors
            return 3
        elif 41 <= error_number <= 60:  # Node execution errors
            return 4
        elif 61 <= error_number <= 80:  # Event bus errors
            return 5
        elif 81 <= error_number <= 100:  # System errors
            return 6
        else:
            return 1  # General error


def create_cli_error(
    error_code: CLIErrorCode,
    message: Optional[str] = None,
    context: Optional[Dict[str, str]] = None,
) -> OnexError:
    """
    Create a CLI-specific OnexError with proper error code mapping.

    Args:
        error_code: The CLI error code
        message: Optional custom message (defaults to error code description)
        context: Optional context information

    Returns:
        OnexError: Configured error with CLI error code
    """
    if message is None:
        message = error_code.get_description()

    # Add context information to message if provided
    if context:
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        message = f"{message} ({context_str})"

    # Map CLI error codes to core error codes for consistency
    core_error_mapping = {
        CLIErrorCode.UNKNOWN_COMMAND: CoreErrorCode.INVALID_PARAMETER,
        CLIErrorCode.MISSING_TARGET_NODE: CoreErrorCode.MISSING_REQUIRED_PARAMETER,
        CLIErrorCode.INVALID_COMMAND_ARGS: CoreErrorCode.INVALID_PARAMETER,
        CLIErrorCode.INVALID_JSON_ARGS: CoreErrorCode.INVALID_PARAMETER,
        CLIErrorCode.NODE_NOT_FOUND: CoreErrorCode.RESOURCE_NOT_FOUND,
        CLIErrorCode.NODE_IMPORT_FAILED: CoreErrorCode.MODULE_NOT_FOUND,
        CLIErrorCode.NODE_REGISTRATION_FAILED: CoreErrorCode.OPERATION_FAILED,
        CLIErrorCode.DISCOVERY_SERVICE_UNAVAILABLE: CoreErrorCode.RESOURCE_UNAVAILABLE,
        CLIErrorCode.NODE_EXECUTION_FAILED: CoreErrorCode.OPERATION_FAILED,
        CLIErrorCode.NODE_MISSING_MAIN: CoreErrorCode.INVALID_CONFIGURATION,
        CLIErrorCode.NODE_INTROSPECTION_FAILED: CoreErrorCode.OPERATION_FAILED,
        CLIErrorCode.NODE_TIMEOUT: CoreErrorCode.TIMEOUT_EXCEEDED,
        CLIErrorCode.EVENT_BUS_ERROR: CoreErrorCode.OPERATION_FAILED,
        CLIErrorCode.EVENT_PUBLISH_FAILED: CoreErrorCode.OPERATION_FAILED,
        CLIErrorCode.EVENT_SUBSCRIPTION_FAILED: CoreErrorCode.OPERATION_FAILED,
        CLIErrorCode.SYSTEM_INFO_UNAVAILABLE: CoreErrorCode.RESOURCE_UNAVAILABLE,
        CLIErrorCode.HANDLER_REGISTRY_ERROR: CoreErrorCode.OPERATION_FAILED,
        CLIErrorCode.VERSION_RESOLVER_ERROR: CoreErrorCode.OPERATION_FAILED,
    }

    core_error = core_error_mapping.get(error_code, CoreErrorCode.OPERATION_FAILED)

    return OnexError(
        message=message,
        error_code=core_error,
        details={
            "cli_error_code": error_code.value,
            "cli_exit_code": error_code.get_exit_code(),
            **(context or {}),
        },
    )


# Convenience functions for common CLI errors
def command_not_found_error(command: str) -> OnexError:
    """Create error for unknown command."""
    return create_cli_error(
        CLIErrorCode.UNKNOWN_COMMAND,
        f"Unknown command: {command}",
        {"command": command},
    )


def target_node_required_error(command: str) -> OnexError:
    """Create error for missing target node."""
    return create_cli_error(
        CLIErrorCode.MISSING_TARGET_NODE,
        f"target_node is required for '{command}' command",
        {"command": command},
    )


def node_not_found_error(node_name: str) -> OnexError:
    """Create error for node not found."""
    return create_cli_error(
        CLIErrorCode.NODE_NOT_FOUND,
        f"Node '{node_name}' not found in registry",
        {"node_name": node_name},
    )


def node_execution_error(node_name: str, error_message: str) -> OnexError:
    """Create error for node execution failure."""
    return create_cli_error(
        CLIErrorCode.NODE_EXECUTION_FAILED,
        f"Failed to execute node '{node_name}': {error_message}",
        {"node_name": node_name, "error": error_message},
    )


# Register CLI error codes with the global registry
register_error_codes("cli", CLIErrorCode)
