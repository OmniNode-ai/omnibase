# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: introspection.py
# version: 1.0.0
# uuid: 7de88b66-4b37-4fc8-aed4-ccb25f712809
# author: OmniNode Team
# created_at: 2025-05-25T17:28:59.327925
# last_modified_at: 2025-05-25T22:11:50.171483
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a55363691943dfb47b4c45b84b106d3bf713350f543eec4b942c184ba8f37d89
# entrypoint: python@introspection.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.introspection
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Introspection implementation for tree generator node.

This module provides the concrete introspection capabilities for the tree generator node,
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

from .error_codes import TreeGeneratorErrorCode
from .models.state import TreeGeneratorInputState, TreeGeneratorOutputState


class TreeGeneratorNodeIntrospection(NodeIntrospectionMixin):
    """Introspection implementation for tree generator node."""

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
        return TreeGeneratorInputState

    @classmethod
    def get_output_state_class(cls) -> Type[BaseModel]:
        """Return the output state model class."""
        return TreeGeneratorOutputState

    @classmethod
    def get_error_codes_class(cls) -> Type:
        """Return the error codes enum class."""
        return TreeGeneratorErrorCode

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
            NodeCapabilityEnum.SUPPORTS_DRY_RUN,
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
                name="--root-directory",
                type="str",
                required=True,
                description="Root directory to generate tree for",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--output-path",
                type="str",
                required=False,
                description="Output path for tree file",
                default=None,
                choices=None,
            ),
        ]

    @classmethod
    def get_cli_optional_args(cls) -> List[CLIArgumentModel]:
        """Return optional CLI arguments."""
        base_args = super().get_cli_optional_args()
        tree_args = [
            CLIArgumentModel(
                name="--format",
                type="str",
                required=False,
                description="Output format",
                default="json",
                choices=["json", "yaml", "text"],
            ),
            CLIArgumentModel(
                name="--validate",
                type="bool",
                required=False,
                description="Validate existing tree file",
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
        return base_args + tree_args

    @classmethod
    def get_cli_exit_codes(cls) -> List[int]:
        """Return possible CLI exit codes."""
        return [0, 1, 2, 3, 4, 5, 6]  # Full range of ONEX exit codes
