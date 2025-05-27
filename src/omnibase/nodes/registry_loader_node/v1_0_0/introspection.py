# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: introspection.py
# version: 1.0.0
# uuid: b883f044-d80a-4b66-aaf3-da7d9019ab61
# author: OmniNode Team
# created_at: 2025-05-25T17:30:45.815995
# last_modified_at: 2025-05-25T22:11:50.170737
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 2214285e553e504465963d6632f5bb3d7e0c5667cfe7585a23e5a1f4ca347172
# entrypoint: python@introspection.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.introspection
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Introspection implementation for registry loader node.

This module provides the concrete introspection capabilities for the registry loader node,
implementing the NodeIntrospectionMixin interface.
"""

from typing import List, Type

from pydantic import BaseModel

from omnibase.mixin.mixin_introspection import NodeIntrospectionMixin
from omnibase.model.model_node_introspection import CLIArgumentModel, NodeCapabilityEnum

from .error_codes import RegistryLoaderErrorCode
from .models.state import RegistryLoaderInputState, RegistryLoaderOutputState


class RegistryLoaderNodeIntrospection(NodeIntrospectionMixin):
    """Introspection implementation for registry loader node."""

    @classmethod
    def get_node_name(cls) -> str:
        """Return the canonical node name."""
        return "registry_loader_node"

    @classmethod
    def get_node_version(cls) -> str:
        """Return the node version."""
        return "1.0.0"

    @classmethod
    def get_node_description(cls) -> str:
        """Return the node description."""
        return "ONEX registry loader for loading and validating registry configurations"

    @classmethod
    def get_input_state_class(cls) -> Type[BaseModel]:
        """Return the input state model class."""
        return RegistryLoaderInputState

    @classmethod
    def get_output_state_class(cls) -> Type[BaseModel]:
        """Return the output state model class."""
        return RegistryLoaderOutputState

    @classmethod
    def get_error_codes_class(cls) -> Type:
        """Return the error codes enum class."""
        return RegistryLoaderErrorCode

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
            "omnibase.registry",
            "omnibase.utils",
        ]

    @classmethod
    def get_optional_dependencies(cls) -> List[str]:
        """Return optional dependencies."""
        return ["omnibase.runtimes.onex_runtime"]

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
                name="registry_path",
                type="str",
                required=True,
                description="Path to the registry configuration file",
                default=None,
                choices=None,
            )
        ]

    @classmethod
    def get_cli_optional_args(cls) -> List[CLIArgumentModel]:
        """Return optional CLI arguments."""
        base_args = super().get_cli_optional_args()
        registry_args = [
            CLIArgumentModel(
                name="--validate-only",
                type="bool",
                required=False,
                description="Only validate registry without loading",
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
            CLIArgumentModel(
                name="--registry-path",
                type="str",
                required=False,
                description="Path to registry directory",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--filter",
                type="str",
                required=False,
                description="Filter artifacts by type or pattern",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--output-format",
                type="str",
                required=False,
                description="Output format for registry data",
                default="json",
                choices=["json", "yaml", "summary"],
            ),
            CLIArgumentModel(
                name="--introspect",
                type="bool",
                required=False,
                description="Show node introspection information",
                default=False,
                choices=None,
            ),
        ]
        return base_args + registry_args

    @classmethod
    def get_cli_exit_codes(cls) -> List[int]:
        """Return possible CLI exit codes."""
        return [0, 1, 2, 3, 4, 5, 6]  # Full range of ONEX exit codes
