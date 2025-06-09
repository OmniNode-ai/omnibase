# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.896650'
# description: Stamped by PythonHandler
# entrypoint: python://introspection
# hash: a49126930edbf3447ce46f91d5ab67c99e796f5168ced3b8e6f286e8d0f1d063
# last_modified_at: '2025-05-29T14:14:00.024204+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: introspection.py
# namespace: python://omnibase.nodes.node_scenario_runner_node.v1_0_0.introspection
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: fc7dbe64-4fbe-45b5-837e-c1f1587f5f3d
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Introspection implementation for node_scenario_runner node.

This module provides the concrete introspection capabilities for the node_scenario_runner node,
implementing the NodeIntrospectionMixin interface.
"""

from pathlib import Path
from typing import List, Optional, Type

from pydantic import BaseModel

from omnibase.mixin.mixin_introspection import NodeIntrospectionMixin
from omnibase.model.model_node_introspection import CLIArgumentModel, NodeCapabilityEnum
    NodeMetadataLoader,
)

from .error_codes import NodeScenarioRunnerErrorCode
from .models.state import NodeScenarioRunnerInputState, NodeScenarioRunnerOutputState


class NodeScenarioRunnerNodeIntrospection(NodeIntrospectionMixin):
    """Introspection implementation for node_scenario_runner node."""

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
        return NodeScenarioRunnerInputState

    @classmethod
    def get_output_state_class(cls) -> Type[BaseModel]:
        """Return the output state model class."""
        return NodeScenarioRunnerOutputState

    @classmethod
    def get_error_codes_class(cls) -> Type:
        """Return the error codes enum class."""
        return NodeScenarioRunnerErrorCode

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
            "omnibase.node_scenario_runners",
            "omnibase.utils",
        ]

    @classmethod
    def get_optional_dependencies(cls) -> List[str]:
        """Return optional dependencies."""
        return ["omnibase.runtimes.onex_runtime", "jinja2"]

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
                name="--node_scenario_runner-path",
                type="str",
                required=True,
                description="Path to node_scenario_runner file or directory",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--output-path",
                type="str",
                required=True,
                description="Output path for generated files",
                default=None,
                choices=None,
            ),
        ]

    @classmethod
    def get_cli_optional_args(cls) -> List[CLIArgumentModel]:
        """Return optional CLI arguments."""
        base_args = super().get_cli_optional_args()
        node_scenario_runner_args = [
            CLIArgumentModel(
                name="--variables",
                type="str",
                required=False,
                description="JSON string or file path containing node_scenario_runner variables",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--dry-run",
                type="bool",
                required=False,
                description="Show what would be generated without creating files",
                default=False,
                choices=None,
            ),
            CLIArgumentModel(
                name="--force",
                type="bool",
                required=False,
                description="Overwrite existing files",
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
        return base_args + node_scenario_runner_args

    @classmethod
    def get_cli_exit_codes(cls) -> List[int]:
        """Return possible CLI exit codes."""
        return [0, 1, 2, 3, 4, 5, 6]  # Full range of ONEX exit codes
