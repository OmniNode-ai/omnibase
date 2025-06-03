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
# namespace: python://omnibase.nodes.node_scenario_runner_node.v1_0_0.models.state
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
NODE_SCENARIO_RUNNER: State models for node_scenario_runner_node.

Replace this docstring with a description of your node's state models.
Update the class names, fields, and validation logic as needed.

Schema Version: 1.0.0
See ../../CHANGELOG.md for version history and migration guidelines.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.core.core_error_codes import CoreErrorCode, OnexError

# Current schema version for node_scenario_runner node state models
# This should be updated whenever the schema changes
# See ../../CHANGELOG.md for version history and migration guidelines
NODE_SCENARIO_RUNNER_STATE_SCHEMA_VERSION = "1.0.0"


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


class NodeScenarioRunnerInputState(BaseModel):
    """
    NODE_SCENARIO_RUNNER: Input state model for node_scenario_runner_node.

    Replace this with your node's input requirements.
    Update field names, types, and validation as needed.

    Schema Version: 1.0.0
    See ../../CHANGELOG.md for version history and migration guidelines.
    """

    version: str = Field(
        ...,
        description="Schema version for input state (must be compatible with current schema)",
    )
    # NODE_SCENARIO_RUNNER: Replace with your required input fields
    node_scenario_runner_required_field: str = Field(
        ..., description="NODE_SCENARIO_RUNNER: Replace with your required input field description"
    )
    # NODE_SCENARIO_RUNNER: Replace with your optional input fields
    node_scenario_runner_optional_field: Optional[str] = Field(
        default="NODE_SCENARIO_RUNNER_DEFAULT_VALUE",
        description="NODE_SCENARIO_RUNNER: Replace with your optional input field description",
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("node_scenario_runner_required_field")
    @classmethod
    def validate_node_scenario_runner_required_field(cls, v: str) -> str:
        """NODE_SCENARIO_RUNNER: Replace with validation for your required field."""
        if not v or not v.strip():
            raise OnexError(
                "node_scenario_runner_required_field cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()


class NodeScenarioRunnerOutputState(BaseModel):
    """
    NODE_SCENARIO_RUNNER: Output state model for node_scenario_runner_node.

    Replace this with your node's output structure.
    Update field names, types, and validation as needed.

    Schema Version: 1.0.0
    See ../../CHANGELOG.md for version history and migration guidelines.
    """

    version: str = Field(
        ..., description="Schema version for output state (must match input version)"
    )
    status: str = Field(..., description="Result status of the node_scenario_runner operation")
    message: str = Field(..., description="Human-readable result or error message")
    # NODE_SCENARIO_RUNNER: Replace with your output fields
    node_scenario_runner_output_field: Optional[str] = Field(
        default=None, description="NODE_SCENARIO_RUNNER: Replace with your output field description"
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate that status is one of the allowed values."""
        allowed_statuses = {"success", "failure", "warning"}
        if v not in allowed_statuses:
            raise OnexError(
                f"status must be one of {allowed_statuses}, got '{v}'",
                CoreErrorCode.INVALID_PARAMETER,
            )
        return v

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate that message is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "message cannot be empty", CoreErrorCode.MISSING_REQUIRED_PARAMETER
            )
        return v.strip()


# NODE_SCENARIO_RUNNER: Add any additional state models your node needs
class NodeScenarioRunnerAdditionalState(BaseModel):
    """
    NODE_SCENARIO_RUNNER: Additional state model if needed.

    Delete this if not needed, or replace with your additional state models.
    """

    node_scenario_runner_field: str = Field(
        ..., description="NODE_SCENARIO_RUNNER: Replace with your field description"
    )

    @field_validator("node_scenario_runner_field")
    @classmethod
    def validate_node_scenario_runner_field(cls, v: str) -> str:
        """NODE_SCENARIO_RUNNER: Replace with validation for your field."""
        if not v or not v.strip():
            raise OnexError(
                "node_scenario_runner_field cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()


def create_node_scenario_runner_input_state(
    node_scenario_runner_required_field: str,
    node_scenario_runner_optional_field: Optional[str] = "NODE_SCENARIO_RUNNER_DEFAULT_VALUE",
    version: Optional[str] = None,
) -> NodeScenarioRunnerInputState:
    """
    NODE_SCENARIO_RUNNER: Factory function to create a NodeScenarioRunnerInputState with proper version handling.

    Replace this with your node's specific factory function.

    Args:
        node_scenario_runner_required_field: NODE_SCENARIO_RUNNER: Replace with your required field description
        node_scenario_runner_optional_field: NODE_SCENARIO_RUNNER: Replace with your optional field description
        version: Optional schema version (defaults to current schema version)

    Returns:
        A validated NodeScenarioRunnerInputState instance
    """
    if version is None:
        version = NODE_SCENARIO_RUNNER_STATE_SCHEMA_VERSION

    return NodeScenarioRunnerInputState(
        version=version,
        node_scenario_runner_required_field=node_scenario_runner_required_field,
        node_scenario_runner_optional_field=node_scenario_runner_optional_field,
    )


def create_node_scenario_runner_output_state(
    status: str,
    message: str,
    input_state: NodeScenarioRunnerInputState,
    node_scenario_runner_output_field: Optional[str] = None,
) -> NodeScenarioRunnerOutputState:
    """
    NODE_SCENARIO_RUNNER: Factory function to create a NodeScenarioRunnerOutputState with proper version propagation.

    Replace this with your node's specific factory function.

    Args:
        status: Result status of the operation
        message: Human-readable result or error message
        input_state: The input state to propagate version from
        node_scenario_runner_output_field: NODE_SCENARIO_RUNNER: Replace with your output field description

    Returns:
        A validated NodeScenarioRunnerOutputState instance with version matching input
    """
    return NodeScenarioRunnerOutputState(
        version=input_state.version,  # Propagate version from input
        status=status,
        message=message,
        node_scenario_runner_output_field=node_scenario_runner_output_field,
    )
