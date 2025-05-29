# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.524700'
# description: Stamped by PythonHandler
# entrypoint: python://introspection.py
# hash: 7b10f9ffe019be349dfcc395b461543c81bd1558a20030b1291df419a373d747
# last_modified_at: '2025-05-29T11:50:11.652441+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: introspection.py
# namespace: omnibase.introspection
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 579fbb6a-3eb5-4d87-ace9-25d629a31a03
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Introspection implementation for schema generator node.

This module provides the concrete introspection capabilities for the schema generator node,
implementing the NodeIntrospectionMixin interface.
"""

from pathlib import Path
from typing import List, Optional, Type

from pydantic import BaseModel

from omnibase.mixin.mixin_introspection import NodeIntrospectionMixin
from omnibase.model.model_node_introspection import CLIArgumentModel, NodeCapabilityEnum
from omnibase.nodes.parity_validator_node.v1_0_0.helpers.parity_node_metadata_loader import (
    NodeMetadataLoader,
)

from .error_codes import SchemaGeneratorErrorCode
from .models.state import SchemaGeneratorInputState, SchemaGeneratorOutputState


class SchemaGeneratorNodeIntrospection(NodeIntrospectionMixin):
    """Introspection implementation for schema generator node."""

    _metadata_loader: Optional[NodeMetadataLoader] = None

    @classmethod
    def _get_metadata_loader(cls) -> NodeMetadataLoader:
        """Get or create the metadata loader for this node."""
        if cls._metadata_loader is None:
            # Get the directory containing this file
            current_file = Path(__file__)
            node_directory = current_file.parent
            cls._metadata_loader = NodeMetadataLoader(node_directory)
        return cls._metadata_loader

    @classmethod
    def get_node_name(cls) -> str:
        """Return the canonical node name from metadata."""
        return cls._get_metadata_loader().node_name

    @classmethod
    def get_node_version(cls) -> str:
        """Return the node version from metadata."""
        return cls._get_metadata_loader().node_version

    @classmethod
    def get_node_description(cls) -> str:
        """Return the node description from metadata."""
        return cls._get_metadata_loader().node_description

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
