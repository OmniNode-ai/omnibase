# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: state.py
# version: 1.0.0
# uuid: 4a64594c-f633-463a-96e8-1a6fb46de27b
# author: OmniNode Team
# created_at: 2025-05-28T12:36:26.917567
# last_modified_at: 2025-05-28T17:20:04.949742
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 059eb14eb880ea5440e5ad4ad55c47245431cf1434b570a8930a9acf977e4fea
# entrypoint: python@state.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.state
# meta_type: tool
# === /OmniNode:Metadata ===


"""
TEMPLATE: State models for template_node.

Replace this docstring with a description of your node's state models.
Update the class names, fields, and validation logic as needed.

Schema Version: 1.0.0
See ../../CHANGELOG.md for version history and migration guidelines.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.core.core_error_codes import CoreErrorCode, OnexError

# Current schema version for template node state models
# This should be updated whenever the schema changes
# See ../../CHANGELOG.md for version history and migration guidelines
TEMPLATE_STATE_SCHEMA_VERSION = "1.0.0"


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


class TemplateInputState(BaseModel):
    """
    TEMPLATE: Input state model for template_node.

    Replace this with your node's input requirements.
    Update field names, types, and validation as needed.

    Schema Version: 1.0.0
    See ../../CHANGELOG.md for version history and migration guidelines.
    """

    version: str = Field(
        ...,
        description="Schema version for input state (must be compatible with current schema)",
    )
    # TEMPLATE: Replace with your required input fields
    template_required_field: str = Field(
        ..., description="TEMPLATE: Replace with your required input field description"
    )
    # TEMPLATE: Replace with your optional input fields
    template_optional_field: Optional[str] = Field(
        default="TEMPLATE_DEFAULT_VALUE",
        description="TEMPLATE: Replace with your optional input field description",
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate that the version field follows semantic versioning."""
        return validate_semantic_version(v)

    @field_validator("template_required_field")
    @classmethod
    def validate_template_required_field(cls, v: str) -> str:
        """TEMPLATE: Replace with validation for your required field."""
        if not v or not v.strip():
            raise OnexError(
                "template_required_field cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()


class TemplateOutputState(BaseModel):
    """
    TEMPLATE: Output state model for template_node.

    Replace this with your node's output structure.
    Update field names, types, and validation as needed.

    Schema Version: 1.0.0
    See ../../CHANGELOG.md for version history and migration guidelines.
    """

    version: str = Field(
        ..., description="Schema version for output state (must match input version)"
    )
    status: str = Field(..., description="Result status of the template operation")
    message: str = Field(..., description="Human-readable result or error message")
    # TEMPLATE: Replace with your output fields
    template_output_field: Optional[str] = Field(
        default=None, description="TEMPLATE: Replace with your output field description"
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


# TEMPLATE: Add any additional state models your node needs
class TemplateAdditionalState(BaseModel):
    """
    TEMPLATE: Additional state model if needed.

    Delete this if not needed, or replace with your additional state models.
    """

    template_field: str = Field(
        ..., description="TEMPLATE: Replace with your field description"
    )

    @field_validator("template_field")
    @classmethod
    def validate_template_field(cls, v: str) -> str:
        """TEMPLATE: Replace with validation for your field."""
        if not v or not v.strip():
            raise OnexError(
                "template_field cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()


def create_template_input_state(
    template_required_field: str,
    template_optional_field: Optional[str] = "TEMPLATE_DEFAULT_VALUE",
    version: Optional[str] = None,
) -> TemplateInputState:
    """
    TEMPLATE: Factory function to create a TemplateInputState with proper version handling.

    Replace this with your node's specific factory function.

    Args:
        template_required_field: TEMPLATE: Replace with your required field description
        template_optional_field: TEMPLATE: Replace with your optional field description
        version: Optional schema version (defaults to current schema version)

    Returns:
        A validated TemplateInputState instance
    """
    if version is None:
        version = TEMPLATE_STATE_SCHEMA_VERSION

    return TemplateInputState(
        version=version,
        template_required_field=template_required_field,
        template_optional_field=template_optional_field,
    )


def create_template_output_state(
    status: str,
    message: str,
    input_state: TemplateInputState,
    template_output_field: Optional[str] = None,
) -> TemplateOutputState:
    """
    TEMPLATE: Factory function to create a TemplateOutputState with proper version propagation.

    Replace this with your node's specific factory function.

    Args:
        status: Result status of the operation
        message: Human-readable result or error message
        input_state: The input state to propagate version from
        template_output_field: TEMPLATE: Replace with your output field description

    Returns:
        A validated TemplateOutputState instance with version matching input
    """
    return TemplateOutputState(
        version=input_state.version,  # Propagate version from input
        status=status,
        message=message,
        template_output_field=template_output_field,
    )
