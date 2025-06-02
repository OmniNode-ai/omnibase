# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.685575'
# description: Stamped by PythonHandler
# entrypoint: python://state
# hash: efc20697bf47e2f3eda74c77635d7ee2e4a3319b72fdfdee5c0cd622ca4884bb
# last_modified_at: '2025-05-29T14:13:59.857073+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: state.py
# namespace: python://omnibase.nodes.stamper_node.v1_0_0.models.state
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 11b325bb-d097-4604-a071-048be348792e
# version: 1.0.0
# === /OmniNode:Metadata ===


import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.mixin.mixin_redaction import SensitiveFieldRedactionMixin
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import (
    OnexVersionLoader,
)
from omnibase.enums.onex_status import OnexStatus

# Use the canonical schema version from the system
STAMPER_STATE_SCHEMA_VERSION = OnexVersionLoader().get_onex_versions().schema_version

# Dynamic example version for schema documentation
_EXAMPLE_VERSION = STAMPER_STATE_SCHEMA_VERSION


def validate_semantic_version(version: str) -> str:
    """
    Validate that a version string follows semantic versioning format.

    Args:
        version: Version string to validate

    Returns:
        The validated version string

    Raises:
        OnexError: If version doesn't match semantic versioning format
    """
    semver_pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
    if not re.match(semver_pattern, version):
        raise OnexError(
            f"Version '{version}' does not follow semantic versioning format (e.g., '1.0.0')",
            CoreErrorCode.INVALID_PARAMETER,
        )
    return version


def validate_schema_version_compatibility(version: str) -> str:
    """
    Validate that a schema version is compatible with the current implementation.

    Args:
        version: Schema version to validate

    Returns:
        The validated version string

    Raises:
        OnexError: If version is not compatible with current schema
    """
    validate_semantic_version(version)

    # Parse version components
    major, minor, patch = version.split(".")[:3]
    current_major, current_minor, current_patch = STAMPER_STATE_SCHEMA_VERSION.split(
        "."
    )[:3]

    # Major version must match for compatibility
    if major != current_major:
        raise OnexError(
            f"Schema version '{version}' is not compatible with current schema version '{STAMPER_STATE_SCHEMA_VERSION}'. "
            f"Major version mismatch requires migration.",
            CoreErrorCode.INVALID_PARAMETER,
        )

    # Minor version can be lower or equal (backward compatibility)
    if int(minor) > int(current_minor):
        raise OnexError(
            f"Schema version '{version}' is newer than current schema version '{STAMPER_STATE_SCHEMA_VERSION}'. "
            f"Please upgrade the implementation.",
            CoreErrorCode.INVALID_PARAMETER,
        )

    return version


class StamperInputState(SensitiveFieldRedactionMixin, BaseModel):
    """Input state contract for the stamper node (node-local).

    This model defines the input parameters required for stamper node execution.
    All fields are validated according to the current schema version.

    Fields:
        version: Schema version for input state (must match current schema version)
        file_path: Path to the file to be stamped (required)
        author: Name or identifier of the user or process requesting the stamp
        correlation_id: Optional correlation ID for request tracking and telemetry
        discover_functions: Whether to discover and include function tools in metadata
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "version": _EXAMPLE_VERSION,
                "file_path": "/path/to/file.py",
                "author": "OmniNode Team",
                "correlation_id": "req-123e4567-e89b-12d3-a456-426614174000",
                "discover_functions": False,
                "api_key": "sk-1234567890abcdef",
                "access_token": "token_abcdef123456",
            }
        }
    )

    version: str = Field(
        ...,
        description="Schema version for input state (must be compatible with current schema)",
        json_schema_extra={"example": _EXAMPLE_VERSION},
    )
    file_path: str = Field(
        ...,
        description="Path to the file to be stamped",
        json_schema_extra={"example": "/path/to/file.py"},
    )
    author: str = Field(
        default="OmniNode Team",
        description="Name or identifier of the user or process requesting the stamp",
        json_schema_extra={"example": "OmniNode Team"},
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="Optional correlation ID for request tracking and telemetry",
        json_schema_extra={"example": "req-123e4567-e89b-12d3-a456-426614174000"},
    )
    discover_functions: bool = Field(
        default=False,
        description="Whether to discover and include function tools in metadata (unified tools approach)",
        json_schema_extra={"example": False},
    )
    api_key: Optional[str] = Field(
        default=None,
        description="Optional API key for authenticated operations (sensitive field)",
        json_schema_extra={"example": "sk-1234567890abcdef"},
    )
    access_token: Optional[str] = Field(
        default=None,
        description="Optional access token for authentication (sensitive field)",
        json_schema_extra={"example": "token_abcdef123456"},
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field is compatible with current schema."""
        return validate_schema_version_compatibility(v)

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Validate that file_path is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "file_path cannot be empty", CoreErrorCode.MISSING_REQUIRED_PARAMETER
            )
        return v.strip()

    @field_validator("author")
    @classmethod
    def validate_author(cls, v: str) -> str:
        """Validate that author is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "author cannot be empty", CoreErrorCode.MISSING_REQUIRED_PARAMETER
            )
        return v.strip()


class StamperOutputState(SensitiveFieldRedactionMixin, BaseModel):
    """Output state contract for the stamper node (node-local).

    This model defines the output structure returned by stamper node execution.
    All fields are validated according to the current schema version.

    Fields:
        version: Schema version for output state (must match input version)
        status: Result status of the stamping operation (must be OnexStatus)
        message: Human-readable result or error message
        correlation_id: Optional correlation ID propagated from input for telemetry
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "version": _EXAMPLE_VERSION,
                "status": "success",
                "message": "File stamped successfully",
                "correlation_id": "req-123e4567-e89b-12d3-a456-426614174000",
                "operation_signature": "sha256:abcdef1234567890",
            }
        }
    )

    version: str = Field(
        ...,
        description="Schema version for output state (must match input version)",
        json_schema_extra={"example": _EXAMPLE_VERSION},
    )
    status: OnexStatus = Field(
        ...,
        description="Result status of the stamping operation (must be OnexStatus)",
        json_schema_extra={"example": OnexStatus.SUCCESS},
    )
    message: str = Field(
        ...,
        description="Human-readable result or error message",
        json_schema_extra={"example": "File stamped successfully"},
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="Optional correlation ID propagated from input for telemetry",
        json_schema_extra={"example": "req-123e4567-e89b-12d3-a456-426614174000"},
    )
    operation_signature: Optional[str] = Field(
        default=None,
        description="Optional cryptographic signature of the operation (sensitive field)",
        json_schema_extra={"example": "sha256:abcdef1234567890"},
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field is compatible with current schema."""
        return validate_schema_version_compatibility(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: OnexStatus) -> OnexStatus:
        """Validate that status is one of the allowed values."""
        if v not in OnexStatus:
            raise OnexError(
                f"status must be a valid OnexStatus, got '{v}'",
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


def create_stamper_input_state(
    file_path: str,
    author: str = "OmniNode Team",
    correlation_id: Optional[str] = None,
    version: Optional[str] = None,
    discover_functions: bool = False,
    api_key: Optional[str] = None,
    access_token: Optional[str] = None,
) -> StamperInputState:
    """
    Factory function to create a StamperInputState with proper version handling.

    Args:
        file_path: Path to the file to be stamped
        author: Name or identifier of the user or process
        correlation_id: Optional correlation ID for tracking
        version: Optional schema version (defaults to current schema version)
        discover_functions: Whether to discover and include function tools in metadata

    Returns:
        A validated StamperInputState instance

    Example:
        >>> state = create_stamper_input_state("/path/to/file.py", "OmniNode Team")
        >>> print(state.version)
        0.1.0
    """
    if version is None:
        version = STAMPER_STATE_SCHEMA_VERSION

    return StamperInputState(
        version=version,
        file_path=file_path,
        author=author,
        correlation_id=correlation_id,
        discover_functions=discover_functions,
        api_key=api_key,
        access_token=access_token,
    )


def create_stamper_output_state(
    status: OnexStatus,
    message: str,
    input_state: StamperInputState,
    correlation_id: Optional[str] = None,
    operation_signature: Optional[str] = None,
) -> StamperOutputState:
    """
    Factory function to create a StamperOutputState with proper version propagation.

    Args:
        status: Result status of the operation
        message: Human-readable result or error message
        input_state: The input state to propagate version and correlation_id from
        correlation_id: Optional override for correlation_id
        operation_signature: Optional cryptographic signature of the operation

    Returns:
        A validated StamperOutputState instance with version matching input

    Example:
        >>> input_state = create_stamper_input_state("/path/to/file.py")
        >>> output_state = create_stamper_output_state("success", "Done", input_state)
        >>> print(output_state.version == input_state.version)
        True
    """
    return StamperOutputState(
        version=input_state.version,  # Propagate version from input
        status=status,
        message=message,
        correlation_id=correlation_id or input_state.correlation_id,
        operation_signature=operation_signature,
    )
