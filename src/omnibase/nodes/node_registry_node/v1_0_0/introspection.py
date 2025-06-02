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
# namespace: python://omnibase.nodes.node_registry_node.v1_0_0.introspection
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
Introspection implementation for node_registry node.

This module provides the concrete introspection capabilities for the node_registry node,
implementing the NodeIntrospectionMixin interface.
"""

import logging
from pathlib import Path
from typing import List, Optional, Type

import yaml
from pydantic import BaseModel

from omnibase.mixin.mixin_introspection import NodeIntrospectionMixin
from omnibase.model.model_node_introspection import CLIArgumentModel, NodeCapabilityEnum
from omnibase.model.model_state_contract import (
    StateContractModel,
    load_state_contract_from_file,
)
from omnibase.nodes.parity_validator_node.v1_0_0.helpers.parity_node_metadata_loader import (
    NodeMetadataLoader,
)

from .error_codes import NodeRegistryErrorCode
from .models.state import (
    NodeRegistryEntry,
    NodeRegistryInputState,
    NodeRegistryOutputState,
    NodeRegistryState,
)
from .port_manager import PortManager


class NodeRegistryNodeIntrospection(NodeIntrospectionMixin):
    """Introspection implementation for node_registry node."""

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
        return NodeRegistryInputState

    @classmethod
    def get_output_state_class(cls) -> Type[BaseModel]:
        """Return the output state model class."""
        return NodeRegistryOutputState

    @classmethod
    def get_error_codes_class(cls) -> Type:
        """Return the error codes enum class."""
        return NodeRegistryErrorCode

    @classmethod
    def get_schema_version(cls) -> str:
        """Return the schema version from the node contract (node.onex.yaml)."""
        # ONEX: Always load schema_version dynamically from contract
        return cls._get_metadata_loader().metadata.schema_version

    @classmethod
    def get_runtime_dependencies(cls) -> List[str]:
        """Return runtime dependencies."""
        return [
            "omnibase.core",
            "omnibase.model",
            "omnibase.node_registrys",
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
                name="--node_registry-path",
                type="str",
                required=True,
                description="Path to node_registry file or directory",
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
        node_registry_args = [
            CLIArgumentModel(
                name="--variables",
                type="str",
                required=False,
                description="JSON string or file path containing node_registry variables",
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
        return base_args + node_registry_args

    @classmethod
    def get_cli_exit_codes(cls) -> List[int]:
        """Return possible CLI exit codes."""
        return [0, 1, 2, 3, 4, 5, 6]  # Full range of ONEX exit codes

    @classmethod
    def get_introspection_response(cls, node_instance) -> dict:
        """
        Aggregate static metadata, contract, and dynamic state for canonical introspection.
        Args:
            node_instance: The live NodeRegistryNode instance.
        Returns:
            dict: Canonical introspection response.
        """
        node_dir = Path(__file__).parent
        # --- Static metadata from node.onex.yaml ---
        with open(node_dir / "node.onex.yaml", "r") as f:
            node_metadata = yaml.safe_load(f)
        # --- Contract/schema from contract.yaml (protocol-pure) ---
        try:
            contract_model: StateContractModel = load_state_contract_from_file(
                str(node_dir / "contract.yaml")
            )
            contract = contract_model.model_dump()
        except Exception as exc:
            # Protocol-pure error info for introspection consumers
            contract = {
                "error": f"Failed to load or validate contract.yaml: {exc}",
                "file": str(node_dir / "contract.yaml"),
            }
            logging.error(f"[NodeRegistryNodeIntrospection] Contract load error: {exc}")
        # --- Dynamic state from node instance ---
        port_manager = getattr(node_instance, "port_manager", None)
        registry_state = getattr(node_instance, "registry_state", None)
        # --- Aggregate response ---
        response = {
            "node_metadata": node_metadata,
            "contract": contract,
            "ports": port_manager.port_state.model_dump() if port_manager else None,
            "event_buses": (
                port_manager.event_bus_state.model_dump() if port_manager else None
            ),
            "port_usage": (
                port_manager.port_usage_map.model_dump() if port_manager else None
            ),
            "registry": registry_state.model_dump() if registry_state else None,
            "tools": (
                registry_state.tools.model_dump()
                if registry_state and hasattr(registry_state, "tools")
                else None
            ),
            # Trust/validation status: collect from registry entries if present
            "trust_status": (
                [
                    {
                        "node_id": entry.node_id,
                        "trust_state": entry.trust_state,
                        "status": entry.status,
                        "last_announce": entry.last_announce,
                    }
                    for entry in getattr(registry_state, "registry", {}).values()
                ]
                if registry_state and getattr(registry_state, "registry", None)
                else None
            ),
        }
        return response
