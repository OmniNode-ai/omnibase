# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.663133'
# description: Stamped by PythonHandler
# entrypoint: python://introspection
# hash: 470b811736b1d7fe2c769ad1cfc46e45932c75136e7346101a99338c3df6de33
# last_modified_at: '2025-05-29T14:13:59.841380+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: introspection.py
# namespace: python://omnibase.nodes.stamper_node.v1_0_0.introspection
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 151efe6b-39e1-44fb-8056-865880d14755
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Introspection implementation for stamper node.

This module provides the concrete introspection capabilities for the stamper node,
implementing the NodeIntrospectionMixin interface.
"""

from pathlib import Path
from typing import List, Optional, Type

from pydantic import BaseModel

from omnibase.mixin.mixin_introspection import NodeIntrospectionMixin
from omnibase.model.model_node_introspection import CLIArgumentModel, NodeCapabilityEnum
    NodeMetadataLoader,
)

from .error_codes import StamperErrorCode
from .models.state import StamperInputState, StamperOutputState


class StamperNodeIntrospection(NodeIntrospectionMixin):
    """Introspection implementation for stamper node."""

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
        return StamperInputState

    @classmethod
    def get_output_state_class(cls) -> Type[BaseModel]:
        """Return the output state model class."""
        return StamperOutputState

    @classmethod
    def get_error_codes_class(cls) -> Type:
        """Return the error codes enum class."""
        return StamperErrorCode

    @classmethod
    def get_schema_version(cls) -> str:
        """Return the schema version."""
        return "1.1.1"  # Stamper is at 1.1.1 due to Pydantic V2 migration

    @classmethod
    def get_runtime_dependencies(cls) -> List[str]:
        """Return runtime dependencies."""
        return [
            "omnibase.core",
            "omnibase.model",
            "omnibase.handlers",
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
            NodeCapabilityEnum.SUPPORTS_DRY_RUN,
            NodeCapabilityEnum.SUPPORTS_BATCH_PROCESSING,
            NodeCapabilityEnum.SUPPORTS_CUSTOM_HANDLERS,
            NodeCapabilityEnum.TELEMETRY_ENABLED,
            NodeCapabilityEnum.SUPPORTS_CORRELATION_ID,
            NodeCapabilityEnum.SUPPORTS_EVENT_BUS,
        ]

    @classmethod
    def get_cli_required_args(cls) -> List[CLIArgumentModel]:
        """Return required CLI arguments."""
        return [
            CLIArgumentModel(
                name="files",
                type="List[str]",
                required=True,
                description="Files to stamp with metadata",
                default=None,
                choices=None,
            )
        ]

    @classmethod
    def get_cli_optional_args(cls) -> List[CLIArgumentModel]:
        """Return optional CLI arguments."""
        base_args = super().get_cli_optional_args()
        stamper_args = [
            CLIArgumentModel(
                name="--author",
                type="str",
                required=False,
                description="Author name for metadata",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--dry-run",
                type="bool",
                required=False,
                description="Show what would be stamped without modifying files",
                default=False,
                choices=None,
            ),
            CLIArgumentModel(
                name="--force",
                type="bool",
                required=False,
                description="Force re-stamping of already stamped files",
                default=False,
                choices=None,
            ),
            CLIArgumentModel(
                name="--batch",
                type="bool",
                required=False,
                description="Process files in batch mode",
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
                name="--write",
                type="bool",
                required=False,
                description="Actually write stamped files (overrides dry-run)",
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
        return base_args + stamper_args

    @classmethod
    def get_cli_exit_codes(cls) -> List[int]:
        """Return possible CLI exit codes."""
        return [0, 1, 2, 3, 4, 5, 6]  # Full range of ONEX exit codes
