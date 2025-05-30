# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.917567'
# description: Stamped by PythonHandler
# entrypoint: python://state
# hash: 45e063fcbb5fdf3884b6b30de813649d187e5f7412bd27c59289322c2fc6c0c2
# last_modified_at: '2025-05-29T14:14:00.041025+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: state.py
# namespace: python://omnibase.nodes.node_registry_node.v1_0_0.models.state
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 4a64594c-f633-463a-96e8-1a6fb46de27b
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
NODE_REGISTRY: State models for node_registry_node.

Replace this docstring with a description of your node's state models.
Update the class names, fields, and validation logic as needed.

Schema Version: 1.0.0
See ../../CHANGELOG.md for version history and migration guidelines.
"""

from typing import Optional, Dict, List, Union
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.model.model_onex_event import OnexEventTypeEnum
from omnibase.model.model_node_metadata import NodeMetadataBlock, IOBlock

# Current schema version for node_registry node state models
# This should be updated whenever the schema changes
# See ../../CHANGELOG.md for version history and migration guidelines
NODE_REGISTRY_STATE_SCHEMA_VERSION = "1.0.0"


def validate_semantic_version(version: str) -> str:
    """
    Validate that a version string follows semantic versioning format.

    Args:
        version: Version string to validate

    Returns:
        The validated version string

    Raises:
        OnexError: If version doesn't match semantic versioning format
    """
    import re

    semver_pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
    if not re.match(semver_pattern, version):
        raise OnexError(
            f"Version '{version}' does not follow semantic versioning format (e.g., '1.0.0')",
            CoreErrorCode.INVALID_PARAMETER,
        )
    return version


class NodeRegistryInputState(BaseModel):
    """
    Input state for node_registry_node.
    - action: str (required) -- e.g., 'get_active_nodes', 'get_node'
    - node_id: Optional[str] -- for node-specific queries
    """
    version: str = Field(..., description="Schema version for input state (must be compatible with current schema)")
    action: str = Field(..., description="Action to perform: 'get_active_nodes', 'get_node', etc.")
    node_id: Optional[str] = Field(default=None, description="Node ID for node-specific queries")

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        return validate_semantic_version(v)

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        allowed = {"get_active_nodes", "get_node"}
        if v not in allowed:
            raise OnexError(f"action must be one of {allowed}", CoreErrorCode.INVALID_PARAMETER)
        return v

    @field_validator("node_id")
    @classmethod
    def validate_node_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise OnexError("node_id cannot be empty if provided", CoreErrorCode.MISSING_REQUIRED_PARAMETER)
        return v.strip() if v else v


class NodeRegistryOutputState(BaseModel):
    """
    Output state for node_registry_node.
    - registry_json: str (JSON-serialized registry state)
    - status: str
    - message: str
    """
    version: str = Field(..., description="Schema version for output state (must match input version)")
    status: str = Field(..., description="Result status of the node_registry operation")
    message: str = Field(..., description="Human-readable result or error message")
    registry_json: Optional[str] = Field(default=None, description="JSON-serialized registry state or node info")

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        return validate_semantic_version(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed_statuses = {"success", "failure", "warning"}
        if v not in allowed_statuses:
            raise OnexError(f"status must be one of {allowed_statuses}, got '{v}'", CoreErrorCode.INVALID_PARAMETER)
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v or not v.strip():
            raise OnexError("message cannot be empty", CoreErrorCode.MISSING_REQUIRED_PARAMETER)
        return v.strip()


# NODE_REGISTRY: Add any additional state models your node needs
class NodeRegistryAdditionalState(BaseModel):
    """
    NODE_REGISTRY: Additional state model if needed.

    Delete this if not needed, or replace with your additional state models.
    """

    node_registry_field: str = Field(
        ..., description="NODE_REGISTRY: Replace with your field description"
    )

    @field_validator("node_registry_field")
    @classmethod
    def validate_node_registry_field(cls, v: str) -> str:
        """NODE_REGISTRY: Replace with validation for your field."""
        if not v or not v.strip():
            raise OnexError(
                "node_registry_field cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()


def create_node_registry_input_state(
    node_registry_required_field: str,
    node_registry_optional_field: Optional[str] = "NODE_REGISTRY_DEFAULT_VALUE",
    version: Optional[str] = None,
) -> NodeRegistryInputState:
    """
    NODE_REGISTRY: Factory function to create a NodeRegistryInputState with proper version handling.

    Replace this with your node's specific factory function.

    Args:
        node_registry_required_field: NODE_REGISTRY: Replace with your required field description
        node_registry_optional_field: NODE_REGISTRY: Replace with your optional field description
        version: Optional schema version (defaults to current schema version)

    Returns:
        A validated NodeRegistryInputState instance
    """
    if version is None:
        version = NODE_REGISTRY_STATE_SCHEMA_VERSION

    return NodeRegistryInputState(
        version=version,
        node_registry_required_field=node_registry_required_field,
        node_registry_optional_field=node_registry_optional_field,
    )


def create_node_registry_output_state(
    status: str,
    message: str,
    input_state: NodeRegistryInputState,
    node_registry_output_field: Optional[str] = None,
) -> NodeRegistryOutputState:
    """
    NODE_REGISTRY: Factory function to create a NodeRegistryOutputState with proper version propagation.

    Replace this with your node's specific factory function.

    Args:
        status: Result status of the operation
        message: Human-readable result or error message
        input_state: The input state to propagate version from
        node_registry_output_field: NODE_REGISTRY: Replace with your output field description

    Returns:
        A validated NodeRegistryOutputState instance with version matching input
    """
    return NodeRegistryOutputState(
        version=input_state.version,  # Propagate version from input
        status=status,
        message=message,
        node_registry_output_field=node_registry_output_field,
    )


class NodeRegistryEntry(BaseModel):
    node_id: Union[str, UUID] = Field(..., description="Unique node identifier")
    metadata_block: NodeMetadataBlock = Field(..., description="Canonical node metadata block")
    status: str = Field(..., description='"ephemeral" | "online" | "validated"')
    execution_mode: str = Field(..., description='"memory" | "container" | "external"')
    inputs: List[IOBlock] = Field(default_factory=list, description="Input schema summary (typed)")
    outputs: List[IOBlock] = Field(default_factory=list, description="Output schema summary (typed)")
    graph_binding: str | None = Field(default=None, description="Optional subgraph ID")
    trust_state: str | None = Field(default=None, description="Trust state")
    ttl: int | None = Field(default=None, description="Ephemeral expiration (seconds)")
    last_announce: str | None = Field(default=None, description="Timestamp of last announce event")


class NodeRegistryState(BaseModel):
    registry: Dict[str, NodeRegistryEntry] = Field(default_factory=dict, description="Active node registry keyed by node_id")
    last_updated: str | None = Field(default=None, description="Timestamp of last registry update")
