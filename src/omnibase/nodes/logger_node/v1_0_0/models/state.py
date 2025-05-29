# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.084733'
# description: Stamped by PythonHandler
# entrypoint: python://state.py
# hash: 3e1450089bad3922f6efe66a363c3646dc8a4f44737e908f219f18c2f376e13c
# last_modified_at: '2025-05-29T11:50:11.313680+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: state.py
# namespace: omnibase.state
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 5a21a0bf-9304-40e8-a7dc-ddff0214372c
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
State models for logger_node.

Defines input and output state models for the ONEX logger node, which provides
structured logging capabilities with configurable output formats, log levels,
and integration with the ONEX observability system.

Schema Version: 1.0.0
See ../../CHANGELOG.md for version history and migration guidelines.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import LogLevelEnum, OnexStatus, OutputFormatEnum

# Current schema version for logger node state models
# This should be updated whenever the schema changes
# See ../../CHANGELOG.md for version history and migration guidelines
LOGGER_STATE_SCHEMA_VERSION = "1.0.0"


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
    import re

    semver_pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
    if not re.match(semver_pattern, version):
        raise OnexError(
            f"Version '{version}' does not follow semantic versioning format (e.g., '1.0.0')",
            CoreErrorCode.INVALID_PARAMETER,
        )
    return version


class LoggerInputState(BaseModel):
    """
    Input state model for logger_node.

    Defines the required and optional parameters for logging operations,
    including log level, message content, output format, and context data.

    Schema Version: 1.0.0
    See ../../CHANGELOG.md for version history and migration guidelines.
    """

    version: str = Field(
        ...,
        description="Schema version for input state (must be compatible with current schema)",
    )
    log_level: LogLevelEnum = Field(
        ...,
        description="Log level for the message (debug, info, warning, error, critical)",
    )
    message: str = Field(..., description="Primary log message content")
    output_format: OutputFormatEnum = Field(
        default=OutputFormatEnum.JSON,
        description="Output format for the log entry (json, yaml, markdown, text, csv)",
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context data to include with the log entry",
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Optional tags for categorizing and filtering log entries",
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="Optional correlation ID for tracing related log entries",
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate that message is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "message cannot be empty", CoreErrorCode.MISSING_REQUIRED_PARAMETER
            )
        return v.strip()


class LoggerOutputState(BaseModel):
    """
    Output state model for logger_node.

    Contains the formatted log entry, processing status, and metadata
    about the logging operation.

    Schema Version: 1.0.0
    See ../../CHANGELOG.md for version history and migration guidelines.
    """

    version: str = Field(
        ..., description="Schema version for output state (must match input version)"
    )
    status: OnexStatus = Field(
        ..., description="Result status of the logging operation"
    )
    message: str = Field(..., description="Human-readable result or error message")
    formatted_log: str = Field(
        ..., description="The formatted log entry in the requested output format"
    )
    output_format: OutputFormatEnum = Field(
        ..., description="The format used for the formatted log entry"
    )
    timestamp: str = Field(
        ..., description="ISO 8601 timestamp when the log entry was processed"
    )
    log_level: LogLevelEnum = Field(
        ..., description="The log level of the processed entry"
    )
    entry_size: int = Field(..., description="Size of the formatted log entry in bytes")

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: OnexStatus) -> OnexStatus:
        """Validate that status is a valid OnexStatus enum value."""
        # Pydantic automatically validates enum values, but we can add custom logic if needed
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

    @field_validator("entry_size")
    @classmethod
    def validate_entry_size(cls, v: int) -> int:
        """Validate that entry_size is non-negative."""
        if v < 0:
            raise OnexError(
                "entry_size cannot be negative", CoreErrorCode.PARAMETER_OUT_OF_RANGE
            )
        return v


def create_logger_input_state(
    log_level: LogLevelEnum,
    message: str,
    output_format: OutputFormatEnum = OutputFormatEnum.JSON,
    context: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
    correlation_id: Optional[str] = None,
    version: Optional[str] = None,
) -> LoggerInputState:
    """
    Factory function to create a LoggerInputState with proper version handling.

    Args:
        log_level: Log level for the message
        message: Primary log message content
        output_format: Output format for the log entry (defaults to JSON)
        context: Additional context data to include with the log entry
        tags: Optional tags for categorizing and filtering log entries
        correlation_id: Optional correlation ID for tracing related log entries
        version: Optional schema version (defaults to current schema version)

    Returns:
        A validated LoggerInputState instance
    """
    if version is None:
        version = LOGGER_STATE_SCHEMA_VERSION

    return LoggerInputState(
        version=version,
        log_level=log_level,
        message=message,
        output_format=output_format,
        context=context,
        tags=tags,
        correlation_id=correlation_id,
    )


def create_logger_output_state(
    status: OnexStatus,
    message: str,
    input_state: LoggerInputState,
    formatted_log: str,
    timestamp: str,
    entry_size: int,
) -> LoggerOutputState:
    """
    Factory function to create a LoggerOutputState with proper version propagation.

    Args:
        status: Result status of the logging operation
        message: Human-readable result or error message
        input_state: The input state to propagate version and format from
        formatted_log: The formatted log entry in the requested output format
        timestamp: ISO 8601 timestamp when the log entry was processed
        entry_size: Size of the formatted log entry in bytes

    Returns:
        A validated LoggerOutputState instance with version matching input
    """
    return LoggerOutputState(
        version=input_state.version,  # Propagate version from input
        status=status,
        message=message,
        formatted_log=formatted_log,
        output_format=input_state.output_format,
        timestamp=timestamp,
        log_level=input_state.log_level,
        entry_size=entry_size,
    )
