# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: state.py
# version: 1.0.0
# uuid: 1974b360-4dd3-4412-a205-ff57e3d3be6b
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.794886
# last_modified_at: 2025-05-28T17:20:04.518116
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 5843f5022bfe9074d3d832049cb6fba06fe2d00a83300990e52fff8325591ef2
# entrypoint: python@state.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.state
# meta_type: tool
# === /OmniNode:Metadata ===


"""
CLI Node State Models.

State models for the CLI node that handles command routing and node registration
via event-driven architecture.

Schema Version: 1.0.0
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.core.core_error_codes import CoreErrorCode, OnexError

# Current schema version for CLI node state models
CLI_STATE_SCHEMA_VERSION = "1.0.0"


def validate_semantic_version(version: str) -> str:
    """
    Validate that a version string follows semantic versioning format.

    Accepts both standard semantic versioning (1.0.0) and ONEX format (v1_0_0).

    Args:
        version: Version string to validate

    Returns:
        The validated version string

    Raises:
        OnexError: If version doesn't match either format
    """
    import re

    # Standard semantic versioning pattern (1.0.0)
    semver_pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"

    # ONEX versioning pattern (v1_0_0)
    onex_pattern = r"^v(\d+)_(\d+)_(\d+)$"

    if re.match(semver_pattern, version) or re.match(onex_pattern, version):
        return version

    raise OnexError(
        f"Version '{version}' does not follow semantic versioning format (e.g., '1.0.0') or ONEX format (e.g., 'v1_0_0')",
        CoreErrorCode.INVALID_PARAMETER,
    )
    return version


class CLIInputState(BaseModel):
    """
    Input state model for CLI node command execution.

    Handles routing commands to registered nodes via event bus.

    Schema Version: 1.0.0
    """

    version: str = Field(
        ...,
        description="Schema version for input state (must be compatible with current schema)",
    )
    command: str = Field(
        ..., description="Command to execute (e.g., 'run', 'list-nodes', 'node-info')"
    )
    target_node: Optional[str] = Field(
        default=None, description="Target node name for 'run' command"
    )
    node_version: Optional[str] = Field(
        default=None, description="Specific version of target node to run"
    )
    args: List[str] = Field(
        default_factory=list, description="Arguments to pass to the target node"
    )
    introspect: bool = Field(
        default=False, description="Whether to show introspection information"
    )
    list_versions: bool = Field(
        default=False, description="Whether to list available versions"
    )
    correlation_id: Optional[str] = Field(
        default=None, description="Correlation ID for request tracking"
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: str) -> str:
        """Validate that command is one of the supported commands."""
        allowed_commands = {
            "run",
            "list-nodes",
            "node-info",
            "version",
            "info",
            "handlers",
        }
        if v not in allowed_commands:
            raise OnexError(
                f"command must be one of {allowed_commands}, got '{v}'",
                CoreErrorCode.INVALID_PARAMETER,
            )
        return v

    @field_validator("target_node")
    @classmethod
    def validate_target_node(cls, v: Optional[str], info: Any) -> Optional[str]:
        """Validate that target_node is provided when command is 'run'."""
        if info.data.get("command") == "run" and not v:
            raise OnexError(
                "target_node is required when command is 'run'",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v


class CLIOutputState(BaseModel):
    """
    Output state model for CLI node command execution.

    Contains the result of command execution and any relevant metadata.

    Schema Version: 1.0.0
    """

    version: str = Field(
        ..., description="Schema version for output state (must match input version)"
    )
    status: str = Field(..., description="Result status of the CLI operation")
    message: str = Field(..., description="Human-readable result or error message")
    command: str = Field(..., description="The command that was executed")
    target_node: Optional[str] = Field(
        default=None, description="Target node that was executed (if applicable)"
    )
    result_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Structured result data from command execution"
    )
    execution_time_ms: Optional[float] = Field(
        default=None, description="Execution time in milliseconds"
    )
    correlation_id: Optional[str] = Field(
        default=None, description="Correlation ID for request tracking"
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate that status is one of the allowed values."""
        allowed_statuses = {"success", "failure", "warning", "error"}
        if v not in allowed_statuses:
            raise OnexError(
                f"status must be one of {allowed_statuses}, got '{v}'",
                CoreErrorCode.INVALID_PARAMETER,
            )
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate that message is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "message cannot be empty", CoreErrorCode.MISSING_REQUIRED_PARAMETER
            )
        return v.strip()


class NodeRegistrationState(BaseModel):
    """
    State model for node registration with the CLI node.

    Used for event-driven node discovery and registration.
    """

    node_name: str = Field(..., description="Name of the node being registered")
    node_version: str = Field(..., description="Version of the node being registered")
    module_path: str = Field(..., description="Python module path for the node")
    capabilities: List[str] = Field(
        default_factory=list, description="List of capabilities the node provides"
    )
    cli_entrypoint: Optional[str] = Field(
        default=None, description="CLI entrypoint command for the node"
    )
    introspection_available: bool = Field(
        default=False, description="Whether the node supports introspection"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata about the node"
    )

    @field_validator("node_name")
    @classmethod
    def validate_node_name(cls, v: str) -> str:
        """Validate that node_name is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "node_name cannot be empty", CoreErrorCode.MISSING_REQUIRED_PARAMETER
            )
        return v.strip()

    @field_validator("node_version")
    @classmethod
    def validate_node_version(cls, v: str) -> str:
        """Validate that node_version follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("module_path")
    @classmethod
    def validate_module_path(cls, v: str) -> str:
        """Validate that module_path is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "module_path cannot be empty", CoreErrorCode.MISSING_REQUIRED_PARAMETER
            )
        return v.strip()


def create_cli_input_state(
    command: str,
    target_node: Optional[str] = None,
    node_version: Optional[str] = None,
    args: Optional[List[str]] = None,
    introspect: bool = False,
    list_versions: bool = False,
    correlation_id: Optional[str] = None,
    version: Optional[str] = None,
) -> CLIInputState:
    """
    Factory function to create a CLIInputState with proper version handling.

    Args:
        command: Command to execute
        target_node: Target node name for 'run' command
        node_version: Specific version of target node to run
        args: Arguments to pass to the target node
        introspect: Whether to show introspection information
        list_versions: Whether to list available versions
        correlation_id: Correlation ID for request tracking
        version: Optional schema version (defaults to current schema version)

    Returns:
        CLIInputState: Configured input state with proper version
    """
    if version is None:
        version = CLI_STATE_SCHEMA_VERSION

    return CLIInputState(
        version=version,
        command=command,
        target_node=target_node,
        node_version=node_version,
        args=args or [],
        introspect=introspect,
        list_versions=list_versions,
        correlation_id=correlation_id,
    )


def create_cli_output_state(
    status: str,
    message: str,
    command: str,
    input_state: CLIInputState,
    target_node: Optional[str] = None,
    result_data: Optional[Dict[str, Any]] = None,
    execution_time_ms: Optional[float] = None,
) -> CLIOutputState:
    """
    Factory function to create a CLIOutputState with proper version handling.

    Args:
        status: Result status of the CLI operation
        message: Human-readable result or error message
        command: The command that was executed
        input_state: The input state that was processed
        target_node: Target node that was executed (if applicable)
        result_data: Structured result data from command execution
        execution_time_ms: Execution time in milliseconds

    Returns:
        CLIOutputState: Configured output state with matching version
    """
    return CLIOutputState(
        version=input_state.version,
        status=status,
        message=message,
        command=command,
        target_node=target_node,
        result_data=result_data,
        execution_time_ms=execution_time_ms,
        correlation_id=input_state.correlation_id,
    )
