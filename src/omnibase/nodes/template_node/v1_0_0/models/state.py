# === Canonical Template Node State Models ===

from typing import Optional
from pydantic import BaseModel, Field, field_validator
# Import OnexError and CoreErrorCode from the canonical location
from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.utils.validators import validate_semantic_version, validate_status, validate_non_empty_string
from omnibase.model.model_semver import SemVerModel
from omnibase.enums.enum_registry_output_status import RegistryOutputStatusEnum
from omnibase.model.model_output_field import OutputFieldModel

TEMPLATE_STATE_SCHEMA_VERSION = "1.0.0"

def validate_semantic_version(version: str) -> str:
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
    Canonical input state model for template_node.
    """
    version: str = Field(..., description="Schema version for input state (must be compatible with current schema)")
    template_required_field: str = Field(..., description="Required input field for template_node")
    template_optional_field: Optional[str] = Field(default="TEMPLATE_DEFAULT_VALUE", description="Optional input field for template_node")

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        return validate_semantic_version(v)

    @field_validator("template_required_field")
    @classmethod
    def validate_template_required_field(cls, v: str) -> str:
        if not v or not v.strip():
            raise OnexError(
                "template_required_field cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()

class TemplateOutputState(BaseModel):
    """
    Canonical output state model for template_node.
    """
    version: str = Field(..., description="Schema version for output state (must match input version)")
    status: str = Field(..., description="Result status of the template operation")
    message: str = Field(..., description="Human-readable result or error message")
    template_output_field: Optional[str] = Field(default=None, description="Optional output field for template_node")

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        return validate_semantic_version(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
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
        if not v or not v.strip():
            raise OnexError(
                "message cannot be empty", CoreErrorCode.MISSING_REQUIRED_PARAMETER
            )
        return v.strip()

def create_template_input_state(
    template_required_field: str,
    template_optional_field: Optional[str] = "TEMPLATE_DEFAULT_VALUE",
    version: Optional[str] = None,
) -> TemplateInputState:
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
    return TemplateOutputState(
        version=input_state.version,
        status=status,
        message=message,
        template_output_field=template_output_field,
    )

# === Canonical Input/Output Models for template_node ===
# These models are the single source of truth for all input/output state for the template_node node.
# Do not duplicate or redefine elsewhere. Update only here for protocol compliance.

TEMPLATE_NODE_STATE_SCHEMA_VERSION = "1.0.0"

class TemplateNodeInputState(BaseModel):
    """
    Canonical input state model for template_node.
    """
    version: SemVerModel = Field(..., description="Schema version for input state (must be compatible with current schema)")
    required_field: str = Field(..., description="Required input field for template_node")
    optional_field: Optional[str] = Field(default=None, description="Optional input field for template_node")

    @field_validator("required_field")
    @classmethod
    def validate_required_field(cls, v: str) -> str:
        return validate_non_empty_string(v, field_name="required_field")

class TemplateNodeOutputState(BaseModel):
    """
    Canonical output state model for template_node.
    """
    version: SemVerModel = Field(..., description="Schema version for output state (must match input version)")
    status: RegistryOutputStatusEnum = Field(..., description="Result status of the template_node operation")
    message: str = Field(..., description="Human-readable result or error message")
    output_field: Optional[OutputFieldModel] = Field(default=None, description="Extensible output field for template_node; must be a Pydantic model")

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        return validate_non_empty_string(v, field_name="message")
