# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.764031'
# description: Stamped by PythonHandler
# entrypoint: python://introspection
# hash: 2260fa2cb4b0bcdccc3aa2969cf71d58527290327768fd4a979e6958db5e1491
# last_modified_at: '2025-05-29T14:13:59.001113+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: introspection.py
# namespace: python://omnibase.nodes.cli_node.v1_0_0.introspection
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: dac949aa-fa58-4108-ac1a-1ee62575eb63
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
CLI Node Introspection.

Introspection capabilities for the CLI node that handles command routing
and node management via event-driven architecture.
"""

from pathlib import Path
from typing import List, Optional, Type

from pydantic import BaseModel

from omnibase.mixin.mixin_introspection import NodeIntrospectionMixin
from omnibase.model.model_node_introspection import CLIArgumentModel, NodeCapabilityEnum

from .error_codes import CLIErrorCode
from .models.state import CLIInputState, CLIOutputState
from omnibase.nodes.node_manager.v1_0_0.tools.tool_metadata_loader import ToolNodeMetadataLoader


class CLINodeIntrospection(NodeIntrospectionMixin):
    """
    Introspection capabilities for CLI node.

    Provides comprehensive metadata about the CLI node's capabilities,
    supported commands, and interface contract.
    """

    _metadata_loader: Optional[ToolNodeMetadataLoader] = None

    @classmethod
    def _get_metadata_loader(cls) -> ToolNodeMetadataLoader:
        """Get or create the metadata loader for this node."""
        if cls._metadata_loader is None:
            # Get the directory containing this file
            current_file = Path(__file__)
            node_directory = current_file.parent
            cls._metadata_loader = ToolNodeMetadataLoader(node_directory)
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
        return CLIInputState

    @classmethod
    def get_output_state_class(cls) -> Type[BaseModel]:
        """Return the output state model class."""
        return CLIOutputState

    @classmethod
    def get_error_codes_class(cls) -> Type:
        """Return the error codes enum class."""
        return CLIErrorCode

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
    def get_runtime_dependencies(cls) -> List[str]:
        """Return runtime dependencies."""
        return [
            "omnibase.core",
            "omnibase.model",
            "omnibase.protocol.protocol_event_bus",
            "omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory",
        ]

    @classmethod
    def get_optional_dependencies(cls) -> List[str]:
        """Return optional dependencies."""
        return ["omnibase.cli_tools.onex.v1_0_0.cli_version_resolver"]

    @classmethod
    def get_cli_required_args(cls) -> List[CLIArgumentModel]:
        """Return required CLI arguments."""
        return [
            CLIArgumentModel(
                name="command",
                type="str",
                required=True,
                description="Command to execute (run, list-nodes, node-info, version, info, handlers)",
                default=None,
                choices=[
                    "run",
                    "list-nodes",
                    "node-info",
                    "version",
                    "info",
                    "handlers",
                ],
            ),
        ]

    @classmethod
    def get_cli_optional_args(cls) -> List[CLIArgumentModel]:
        """Return optional CLI arguments."""
        base_args = super().get_cli_optional_args()
        cli_args = [
            CLIArgumentModel(
                name="target_node",
                type="str",
                required=False,
                description="Target node name (for 'run' and 'node-info' commands)",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--version",
                type="str",
                required=False,
                description="Specific version of target node to run",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--args",
                type="str",
                required=False,
                description="Additional arguments to pass to the node (as JSON string)",
                default=None,
                choices=None,
            ),
            CLIArgumentModel(
                name="--list-versions",
                type="bool",
                required=False,
                description="List available versions for the specified node",
                default=False,
                choices=None,
            ),
        ]
        return base_args + cli_args

    @classmethod
    def get_cli_exit_codes(cls) -> List[int]:
        """Return possible CLI exit codes."""
        return [0, 1]  # Success or error

    # Note: Removed custom handle_introspect_command() method to use the standardized
    # base mixin implementation that outputs proper NodeIntrospectionResponse format
    # for parity validator compatibility
