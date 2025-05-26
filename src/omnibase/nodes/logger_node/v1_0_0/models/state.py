# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: state.py
# version: 1.0.0
# uuid: 2403f1fb-9605-4bc3-8a53-dd240220a1e8
# author: OmniNode Team
# created_at: 2025-05-24T09:29:37.968817
# last_modified_at: 2025-05-24T13:39:57.891980
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 9cdf081abf61fa062af9e2bdc49212b08cf963b08d82708e179d399494f6e5d1
# entrypoint: python@state.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.state
# meta_type: tool
# === /OmniNode:Metadata ===


"""
State models for logger_node.

Defines input and output state models for the ONEX logger node, which provides
structured logging capabilities with configurable output formats, log levels,
and integration with the ONEX observability system.

Schema Version: 1.0.0
See ../../CHANGELOG.md for version history and migration guidelines.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.core.error_codes import CoreErrorCode, OnexError

# Current schema version for logger node state models
# This should be updated whenever the schema changes
# See ../../CHANGELOG.md for version history and migration guidelines
LOGGER_STATE_SCHEMA_VERSION = "1.0.0"


class LogLevel(str, Enum):
    """Supported log levels for the logger node."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class OutputFormat(str, Enum):
    """Supported output formats for log entries."""

    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    TEXT = "text"
    CSV = "csv"


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
    log_level: LogLevel = Field(
        ...,
        description="Log level for the message (debug, info, warning, error, critical)",
    )
    message: str = Field(..., description="Primary log message content")
    output_format: OutputFormat = Field(
        default=OutputFormat.JSON,
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
    status: str = Field(..., description="Result status of the logging operation")
    message: str = Field(..., description="Human-readable result or error message")
    formatted_log: str = Field(
        ..., description="The formatted log entry in the requested output format"
    )
    output_format: OutputFormat = Field(
        ..., description="The format used for the formatted log entry"
    )
    timestamp: str = Field(
        ..., description="ISO 8601 timestamp when the log entry was processed"
    )
    log_level: LogLevel = Field(..., description="The log level of the processed entry")
    entry_size: int = Field(..., description="Size of the formatted log entry in bytes")

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate that status is one of the allowed values."""
        allowed_statuses = {"success", "failure", "warning"}
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
    log_level: LogLevel,
    message: str,
    output_format: OutputFormat = OutputFormat.JSON,
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
    status: str,
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
