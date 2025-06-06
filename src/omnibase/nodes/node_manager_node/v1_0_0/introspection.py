# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T09:34:52.824810'
# description: Stamped by PythonHandler
# entrypoint: python://introspection
# hash: 51d41f8ea4ea025749a01565accdca7150d3549158dd85406a9ae5e91581d540
# last_modified_at: '2025-05-29T14:13:59.382713+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: introspection.py
# namespace: python://omnibase.nodes.node_manager_node.v1_0_0.introspection
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 74bac8d0-777b-4dba-84c8-429a516d9b72
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Introspection implementation for node_manager_node.

This module provides the concrete introspection capabilities for the node manager node,
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

from .error_codes import NodeManagerErrorCode
from .models.state import NodeManagerInputState, NodeManagerOutputState


class NodeManagerIntrospection(NodeIntrospectionMixin):
    """Introspection implementation for node manager node."""

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
        return NodeManagerInputState

    @classmethod
    def get_output_state_class(cls) -> Type[BaseModel]:
        """Return the output state model class."""
        return NodeManagerOutputState

    @classmethod
    def get_error_codes_class(cls) -> Type:
        """Return the error codes enum class."""
        return NodeManagerErrorCode

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
            "omnibase.runtimes.onex_runtime",
        ]

    @classmethod
    def get_optional_dependencies(cls) -> List[str]:
        """Return optional dependencies."""
        return ["jinja2", "pyyaml"]

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
                name="operation",
                type="str",
                required=True,
                description="Node management operation to perform",
                default=None,
                choices=[
                    "generate",
                    "regenerate-contract",
                    "regenerate-manifest",
                    "fix-health",
                    "sync-configs",
                ],
            ),
        ]

    @classmethod
    def get_cli_optional_args(cls) -> List[CLIArgumentModel]:
        """Return optional CLI arguments."""
        base_args = super().get_cli_optional_args()
        node_manager_args = [
            # Generate operation arguments
            CLIArgumentModel(
                name="node_name",
                type="str",
                required=False,
                description="Name of the new node to generate (required for generate operation)",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--template",
                type="str",
                required=False,
                description="Template source to use for generation",
                default="node_template",
                choices=None,
            ),
            CLIArgumentModel(
                name="--author",
                type="str",
                required=False,
                description="Author name for generated/updated node metadata",
                default="OmniNode Team",
                choices=None,
            ),
            # Maintenance operation arguments
            CLIArgumentModel(
                name="--nodes",
                type="List[str]",
                required=False,
                description="Specific node names to process (default: all nodes)",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--target-directory",
                type="str",
                required=False,
                description="Target directory for operations",
                default="src/omnibase/nodes",
                choices=None,
            ),
            CLIArgumentModel(
                name="--apply",
                type="bool",
                required=False,
                description="Apply changes (default: dry-run mode)",
                default=False,
                choices=None,
            ),
            CLIArgumentModel(
                name="--no-backup",
                type="bool",
                required=False,
                description="Disable backup creation before making changes",
                default=False,
                choices=None,
            ),
            CLIArgumentModel(
                name="--schema-version",
                type="str",
                required=False,
                description="Schema version to use",
                default="1.0.0",
                choices=None,
            ),
            CLIArgumentModel(
                name="--introspect",
                type="bool",
                required=False,
                description="Display node contract and capabilities",
                default=False,
                choices=None,
            ),
        ]
        return base_args + node_manager_args

    @classmethod
    def get_cli_exit_codes(cls) -> List[int]:
        """Return possible CLI exit codes."""
        return [0, 1, 2, 3, 4, 5, 6]  # Full range of ONEX exit codes
