# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: introspection.py
# version: 1.0.0
# uuid: 3871e68b-85df-4d82-9740-245dd51dd69d
# author: OmniNode Team
# created_at: 2025-05-25T17:35:42.194400
# last_modified_at: 2025-05-25T22:11:50.169692
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 602e09871fc89252ce1df574c394de4688f427170bae0358bf631bd08dc3f409
# entrypoint: python@introspection.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.introspection
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Introspection implementation for logger node.

This module provides the concrete introspection capabilities for the logger node,
implementing the NodeIntrospectionMixin interface.
"""

from typing import List, Type

from pydantic import BaseModel

from omnibase.core.error_codes import CoreErrorCode
from omnibase.mixin.introspection_mixin import NodeIntrospectionMixin
from omnibase.model.model_node_introspection import CLIArgumentModel, NodeCapabilityEnum

from .models.state import LoggerInputState, LoggerOutputState


class LoggerNodeIntrospection(NodeIntrospectionMixin):
    """Introspection implementation for logger node."""

    @classmethod
    def get_node_name(cls) -> str:
        """Return the canonical node name."""
        return "logger_node"

    @classmethod
    def get_node_version(cls) -> str:
        """Return the node version."""
        return "1.0.0"

    @classmethod
    def get_node_description(cls) -> str:
        """Return the node description."""
        return "ONEX logger node for structured logging with configurable output formats and centralized configuration"

    @classmethod
    def get_input_state_class(cls) -> Type[BaseModel]:
        """Return the input state model class."""
        return LoggerInputState

    @classmethod
    def get_output_state_class(cls) -> Type[BaseModel]:
        """Return the output state model class."""
        return LoggerOutputState

    @classmethod
    def get_error_codes_class(cls) -> Type:
        """Return the error codes enum class."""
        return CoreErrorCode

    @classmethod
    def get_schema_version(cls) -> str:
        """Return the schema version."""
        return "1.0.0"

    @classmethod
    def get_runtime_dependencies(cls) -> List[str]:
        """Return runtime dependencies."""
        return [
            "omnibase.core",
            "omnibase.model",
            "omnibase.utils",
            "pydantic",
            "datetime",
        ]

    @classmethod
    def get_optional_dependencies(cls) -> List[str]:
        """Return optional dependencies."""
        return ["omnibase.runtimes.onex_runtime", "yaml", "csv"]

    @classmethod
    def get_node_capabilities(cls) -> List[NodeCapabilityEnum]:
        """Return node capabilities."""
        return [
            NodeCapabilityEnum.TELEMETRY_ENABLED,
            NodeCapabilityEnum.SUPPORTS_CORRELATION_ID,
            NodeCapabilityEnum.SUPPORTS_EVENT_BUS,
            NodeCapabilityEnum.SUPPORTS_SCHEMA_VALIDATION,
        ]

    @classmethod
    def get_cli_required_args(cls) -> List[CLIArgumentModel]:
        """Return required CLI arguments."""
        return [
            CLIArgumentModel(
                name="--log-level",
                type="str",
                required=True,
                description="Log level for the message",
                default=None,
                choices=["debug", "info", "warning", "error", "critical"],
            ),
            CLIArgumentModel(
                name="--message",
                type="str",
                required=True,
                description="Primary log message content",
                default=None,
                choices=None,
            ),
        ]

    @classmethod
    def get_cli_optional_args(cls) -> List[CLIArgumentModel]:
        """Return optional CLI arguments."""
        base_args = super().get_cli_optional_args()
        logger_args = [
            CLIArgumentModel(
                name="--output-format",
                type="str",
                required=False,
                description="Output format for the log entry",
                default="json",
                choices=["json", "yaml", "markdown", "text", "csv"],
            ),
            CLIArgumentModel(
                name="--context",
                type="str",
                required=False,
                description="JSON string containing additional context data",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--tags",
                type="str",
                required=False,
                description="Comma-separated list of tags for categorizing log entries",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--introspect",
                type="bool",
                required=False,
                description="Show node introspection information",
                default=False,
                choices=None,
            ),
            CLIArgumentModel(
                name="--correlation-id",
                type="str",
                required=False,
                description="Correlation ID for request tracking",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--verbose",
                type="bool",
                required=False,
                description="Enable verbose output",
                default=False,
                choices=None,
            ),
        ]
        return base_args + logger_args

    @classmethod
    def get_cli_exit_codes(cls) -> List[int]:
        """Return possible CLI exit codes."""
        return [0, 1, 2, 3, 4, 5, 6]  # Full range of ONEX exit codes
