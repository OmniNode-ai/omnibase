# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: logger_output_config.py
# version: 1.0.0
# uuid: 78ed3ce3-1bae-4834-87f2-03d0c621e2aa
# author: OmniNode Team
# created_at: 2025-05-26T16:24:53.818116
# last_modified_at: 2025-05-27T09:37:08.977251
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 47bfd09f1f3c790318c8f88cdc716961c895ef5099462115b46455748df7ca48
# entrypoint: python@logger_output_config.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.logger_output_config
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Logger Node output configuration models.

Defines configuration models for controlling Logger Node output formatting,
target destinations, and context-aware behavior based on environment
(CLI, production, development).

This supports Phase 2 of the structured logging infrastructure implementation.
"""

import os
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.core.error_codes import CoreErrorCode, OnexError
from omnibase.enums import OutputFormatEnum


class LoggerEnvironmentEnum(str, Enum):
    """Environment types for context-aware formatting."""

    CLI = "cli"
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TESTING = "testing"


class LoggerOutputTargetEnum(str, Enum):
    """Output target destinations for log entries."""

    STDOUT = "stdout"
    STDERR = "stderr"
    FILE = "file"
    BOTH = "both"  # stdout + file
    NULL = "null"  # discard output


class LoggerVerbosityEnum(str, Enum):
    """Verbosity levels for output formatting."""

    MINIMAL = "minimal"  # Just message
    STANDARD = "standard"  # Message + level + timestamp
    VERBOSE = "verbose"  # All fields including context
    DEBUG = "debug"  # Everything + internal metadata


class LoggerOutputConfig(BaseModel):
    """
    Configuration model for Logger Node output formatting and targeting.

    Controls how log entries are formatted and where they are sent,
    with support for environment-specific behavior and multiple targets.
    """

    # Core formatting configuration
    output_format: OutputFormatEnum = Field(
        default=OutputFormatEnum.JSON,
        description="Primary output format for log entries",
    )

    verbosity: LoggerVerbosityEnum = Field(
        default=LoggerVerbosityEnum.STANDARD,
        description="Verbosity level for output formatting",
    )

    environment: LoggerEnvironmentEnum = Field(
        default=LoggerEnvironmentEnum.DEVELOPMENT,
        description="Environment context for formatting decisions",
    )

    # Output targeting
    primary_target: LoggerOutputTargetEnum = Field(
        default=LoggerOutputTargetEnum.STDOUT, description="Primary output destination"
    )

    file_path: Optional[str] = Field(
        default=None,
        description="File path for file-based output (required if target includes file)",
    )

    # Context-aware formatting options
    include_timestamp: bool = Field(
        default=True, description="Include timestamp in formatted output"
    )

    include_correlation_id: bool = Field(
        default=True, description="Include correlation ID when available"
    )

    include_context: bool = Field(
        default=True, description="Include context data in output"
    )

    include_tags: bool = Field(default=True, description="Include tags in output")

    # Human-readable formatting options
    use_colors: bool = Field(
        default=False,
        description="Use ANSI color codes for CLI output (auto-detected if not set)",
    )

    compact_format: bool = Field(
        default=False, description="Use compact single-line format when possible"
    )

    # Advanced options
    max_context_depth: int = Field(
        default=3, description="Maximum nesting depth for context objects"
    )

    truncate_long_messages: bool = Field(
        default=False, description="Truncate messages longer than max_message_length"
    )

    max_message_length: int = Field(
        default=1000, description="Maximum message length before truncation"
    )

    # Environment variable overrides
    respect_env_vars: bool = Field(
        default=True,
        description="Allow environment variables to override configuration",
    )

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v: Optional[str], info: Any) -> Optional[str]:
        """Validate file path when file output is requested."""
        if v is None:
            return v

        # Check if primary_target requires a file path
        primary_target = info.data.get("primary_target")
        if primary_target in [LoggerOutputTargetEnum.FILE, LoggerOutputTargetEnum.BOTH]:
            if not v or not v.strip():
                raise OnexError(
                    "file_path is required when primary_target is 'file' or 'both'",
                    CoreErrorCode.MISSING_REQUIRED_PARAMETER,
                )

        return v.strip() if v else None

    @field_validator("max_context_depth")
    @classmethod
    def validate_max_context_depth(cls, v: int) -> int:
        """Validate context depth is reasonable."""
        if v < 1 or v > 10:
            raise OnexError(
                "max_context_depth must be between 1 and 10",
                CoreErrorCode.PARAMETER_OUT_OF_RANGE,
            )
        return v

    @field_validator("max_message_length")
    @classmethod
    def validate_max_message_length(cls, v: int) -> int:
        """Validate message length limit is reasonable."""
        if v < 50 or v > 10000:
            raise OnexError(
                "max_message_length must be between 50 and 10000",
                CoreErrorCode.PARAMETER_OUT_OF_RANGE,
            )
        return v

    def apply_environment_overrides(self) -> "LoggerOutputConfig":
        """
        Apply environment variable overrides to configuration.

        Returns:
            New LoggerOutputConfig instance with environment overrides applied
        """
        if not self.respect_env_vars:
            return self

        # Create a copy of current config
        config_dict = self.model_dump()

        # Apply environment variable overrides
        env_mappings = {
            "ONEX_LOG_FORMAT": ("output_format", OutputFormatEnum),
            "ONEX_LOG_VERBOSITY": ("verbosity", LoggerVerbosityEnum),
            "ONEX_LOG_ENVIRONMENT": ("environment", LoggerEnvironmentEnum),
            "ONEX_LOG_TARGET": ("primary_target", LoggerOutputTargetEnum),
            "ONEX_LOG_FILE_PATH": ("file_path", str),
            "ONEX_LOG_INCLUDE_TIMESTAMP": ("include_timestamp", bool),
            "ONEX_LOG_INCLUDE_CORRELATION_ID": ("include_correlation_id", bool),
            "ONEX_LOG_INCLUDE_CONTEXT": ("include_context", bool),
            "ONEX_LOG_USE_COLORS": ("use_colors", bool),
            "ONEX_LOG_COMPACT": ("compact_format", bool),
        }

        for env_var, (field_name, field_type) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    if field_type == bool:
                        config_dict[field_name] = env_value.lower() in (
                            "true",
                            "1",
                            "yes",
                            "on",
                        )
                    elif field_type == str:
                        config_dict[field_name] = env_value
                    elif isinstance(field_type, type) and issubclass(field_type, Enum):
                        config_dict[field_name] = field_type(env_value.lower())
                except (ValueError, TypeError):
                    # Log warning but don't fail - use default value
                    pass

        return LoggerOutputConfig(**config_dict)

    def get_effective_format_settings(self) -> Dict[str, Any]:
        """
        Get effective format settings based on environment and verbosity.

        Returns:
            Dictionary of format settings for use by format handlers
        """
        settings = {
            "include_timestamp": self.include_timestamp,
            "include_correlation_id": self.include_correlation_id,
            "include_context": self.include_context,
            "include_tags": self.include_tags,
            "use_colors": self.use_colors,
            "compact_format": self.compact_format,
            "max_context_depth": self.max_context_depth,
            "truncate_long_messages": self.truncate_long_messages,
            "max_message_length": self.max_message_length,
        }

        # Apply environment-specific adjustments
        if self.environment == LoggerEnvironmentEnum.CLI:
            # CLI prefers human-readable output
            settings["use_colors"] = True  # Auto-detect TTY
            settings["compact_format"] = False

        elif self.environment == LoggerEnvironmentEnum.PRODUCTION:
            # Production prefers structured, compact output
            settings["use_colors"] = False
            settings["compact_format"] = True

        elif self.environment == LoggerEnvironmentEnum.DEVELOPMENT:
            # Development prefers verbose, readable output
            settings["use_colors"] = True
            settings["compact_format"] = False

        elif self.environment == LoggerEnvironmentEnum.TESTING:
            # Testing prefers consistent, minimal output
            settings["use_colors"] = False
            settings["compact_format"] = True
            settings["include_timestamp"] = False  # For deterministic tests

        # Apply verbosity-specific adjustments
        if self.verbosity == LoggerVerbosityEnum.MINIMAL:
            settings.update(
                {
                    "include_timestamp": False,
                    "include_correlation_id": False,
                    "include_context": False,
                    "include_tags": False,
                    "compact_format": True,
                }
            )

        elif self.verbosity == LoggerVerbosityEnum.STANDARD:
            settings.update(
                {
                    "include_timestamp": True,
                    "include_correlation_id": False,
                    "include_context": False,
                    "include_tags": False,
                }
            )

        elif self.verbosity == LoggerVerbosityEnum.VERBOSE:
            settings.update(
                {
                    "include_timestamp": True,
                    "include_correlation_id": True,
                    "include_context": True,
                    "include_tags": True,
                }
            )

        elif self.verbosity == LoggerVerbosityEnum.DEBUG:
            settings.update(
                {
                    "include_timestamp": True,
                    "include_correlation_id": True,
                    "include_context": True,
                    "include_tags": True,
                    "compact_format": False,
                }
            )

        return settings

    def should_output_to_stdout(self) -> bool:
        """Check if output should go to stdout."""
        return self.primary_target in [
            LoggerOutputTargetEnum.STDOUT,
            LoggerOutputTargetEnum.BOTH,
        ]

    def should_output_to_stderr(self) -> bool:
        """Check if output should go to stderr."""
        return self.primary_target == LoggerOutputTargetEnum.STDERR

    def should_output_to_file(self) -> bool:
        """Check if output should go to file."""
        return self.primary_target in [
            LoggerOutputTargetEnum.FILE,
            LoggerOutputTargetEnum.BOTH,
        ]

    def should_discard_output(self) -> bool:
        """Check if output should be discarded."""
        return self.primary_target == LoggerOutputTargetEnum.NULL


def create_default_config(
    environment: Optional[LoggerEnvironmentEnum] = None,
    verbosity: Optional[LoggerVerbosityEnum] = None,
    output_format: Optional[OutputFormatEnum] = None,
) -> LoggerOutputConfig:
    """
    Create a default Logger output configuration.

    Args:
        environment: Environment context (auto-detected if None)
        verbosity: Verbosity level (standard if None)
        output_format: Output format (JSON if None)

    Returns:
        LoggerOutputConfig with appropriate defaults
    """
    # Auto-detect environment if not specified
    if environment is None:
        if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
            environment = LoggerEnvironmentEnum.TESTING
        elif os.getenv("ONEX_ENV") == "production":
            environment = LoggerEnvironmentEnum.PRODUCTION
        elif os.getenv("ONEX_ENV") == "development":
            environment = LoggerEnvironmentEnum.DEVELOPMENT
        else:
            # Default to CLI if running interactively
            import sys

            environment = (
                LoggerEnvironmentEnum.CLI
                if sys.stdout.isatty()
                else LoggerEnvironmentEnum.DEVELOPMENT
            )

    config = LoggerOutputConfig(
        environment=environment,
        verbosity=verbosity or LoggerVerbosityEnum.STANDARD,
        output_format=output_format or OutputFormatEnum.JSON,
    )

    # Apply environment variable overrides
    return config.apply_environment_overrides()


def create_cli_config() -> LoggerOutputConfig:
    """Create configuration optimized for CLI usage."""
    return create_default_config(
        environment=LoggerEnvironmentEnum.CLI,
        verbosity=LoggerVerbosityEnum.STANDARD,
        output_format=OutputFormatEnum.TEXT,
    )


def create_production_config() -> LoggerOutputConfig:
    """Create configuration optimized for production usage."""
    return create_default_config(
        environment=LoggerEnvironmentEnum.PRODUCTION,
        verbosity=LoggerVerbosityEnum.VERBOSE,
        output_format=OutputFormatEnum.JSON,
    )


def create_development_config() -> LoggerOutputConfig:
    """Create configuration optimized for development usage."""
    return create_default_config(
        environment=LoggerEnvironmentEnum.DEVELOPMENT,
        verbosity=LoggerVerbosityEnum.VERBOSE,
        output_format=OutputFormatEnum.YAML,
    )


def create_testing_config() -> LoggerOutputConfig:
    """Create configuration optimized for testing usage."""
    return create_default_config(
        environment=LoggerEnvironmentEnum.TESTING,
        verbosity=LoggerVerbosityEnum.MINIMAL,
        output_format=OutputFormatEnum.JSON,
    )
