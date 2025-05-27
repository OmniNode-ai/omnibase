# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: introspection.py
# version: 1.0.0
# uuid: b6330b0b-6cf3-46e1-ae4b-fc2d93e587f3
# author: OmniNode Team
# created_at: 2025-05-25T17:33:13.723342
# last_modified_at: 2025-05-25T22:11:50.177189
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 889d93232741cd2f437fa14f2177a5f32af1391efb1d7eb90e21c22dd75fc0e1
# entrypoint: python@introspection.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.introspection
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Introspection implementation for schema generator node.

This module provides the concrete introspection capabilities for the schema generator node,
implementing the NodeIntrospectionMixin interface.
"""

from typing import List, Type

from pydantic import BaseModel

from omnibase.mixin.mixin_introspection import NodeIntrospectionMixin
from omnibase.model.model_node_introspection import CLIArgumentModel, NodeCapabilityEnum

from .error_codes import SchemaGeneratorErrorCode
from .models.state import SchemaGeneratorInputState, SchemaGeneratorOutputState


class SchemaGeneratorNodeIntrospection(NodeIntrospectionMixin):
    """Introspection implementation for schema generator node."""

    @classmethod
    def get_node_name(cls) -> str:
        """Return the canonical node name."""
        return "schema_generator_node"

    @classmethod
    def get_node_version(cls) -> str:
        """Return the node version."""
        return "1.0.0"

    @classmethod
    def get_node_description(cls) -> str:
        """Return the node description."""
        return "ONEX schema generator for creating JSON schemas from Pydantic models"

    @classmethod
    def get_input_state_class(cls) -> Type[BaseModel]:
        """Return the input state model class."""
        return SchemaGeneratorInputState

    @classmethod
    def get_output_state_class(cls) -> Type[BaseModel]:
        """Return the output state model class."""
        return SchemaGeneratorOutputState

    @classmethod
    def get_error_codes_class(cls) -> Type:
        """Return the error codes enum class."""
        return SchemaGeneratorErrorCode

    @classmethod
    def get_schema_version(cls) -> str:
        """Return the schema version."""
        return "1.0.0"

    @classmethod
    def get_runtime_dependencies(cls) -> List[str]:
        """Return runtime dependencies."""
        return ["omnibase.core", "omnibase.model", "omnibase.utils"]

    @classmethod
    def get_optional_dependencies(cls) -> List[str]:
        """Return optional dependencies."""
        return ["omnibase.runtimes.onex_runtime"]

    @classmethod
    def get_node_capabilities(cls) -> List[NodeCapabilityEnum]:
        """Return node capabilities."""
        return [
            NodeCapabilityEnum.SUPPORTS_BATCH_PROCESSING,
            NodeCapabilityEnum.TELEMETRY_ENABLED,
            NodeCapabilityEnum.SUPPORTS_CORRELATION_ID,
            NodeCapabilityEnum.SUPPORTS_EVENT_BUS,
            NodeCapabilityEnum.SUPPORTS_SCHEMA_VALIDATION,
        ]

    @classmethod
    def get_cli_required_args(cls) -> List[CLIArgumentModel]:
        """Return required CLI arguments."""
        return []  # Schema generator has no required args

    @classmethod
    def get_cli_optional_args(cls) -> List[CLIArgumentModel]:
        """Return optional CLI arguments."""
        base_args = super().get_cli_optional_args()
        schema_args = [
            CLIArgumentModel(
                name="--input-path",
                type="str",
                required=True,
                description="Path to input file or directory containing Pydantic models",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--output-dir",
                type="str",
                required=False,
                description="Output directory for generated schemas",
                default="src/omnibase/schemas/",
                choices=None,
            ),
            CLIArgumentModel(
                name="--include-metadata",
                type="bool",
                required=False,
                description="Include metadata in generated schemas",
                default=True,
                choices=None,
            ),
            CLIArgumentModel(
                name="--models",
                type="List[str]",
                required=False,
                description="Specific models to generate schemas for",
                default=None,
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
                name="--output-path",
                type="str",
                required=False,
                description="Output path for generated schema files",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--format",
                type="str",
                required=False,
                description="Output format for schemas",
                default="json",
                choices=["json", "yaml"],
            ),
            CLIArgumentModel(
                name="--batch",
                type="bool",
                required=False,
                description="Process multiple files in batch mode",
                default=False,
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
        ]
        return base_args + schema_args

    @classmethod
    def get_cli_exit_codes(cls) -> List[int]:
        """Return possible CLI exit codes."""
        return [0, 1, 2, 3, 4, 5, 6]  # Full range of ONEX exit codes
