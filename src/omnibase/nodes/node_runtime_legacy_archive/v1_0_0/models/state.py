# === Canonical Runtime Node State Models ===

from typing import Optional

from pydantic import BaseModel, Field, field_validator

# Import OnexError and CoreErrorCode from the canonical location
from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums.enum_registry_output_status import RegistryOutputStatusEnum
from omnibase.model.model_output_field import OutputFieldModel
from omnibase.model.model_semver import SemVerModel
from omnibase.utils.validators import (
    validate_non_empty_string,
    validate_semantic_version,
    validate_status,
)

RUNTIME_STATE_SCHEMA_VERSION = "1.0.0"


def validate_semantic_version(version: str) -> str:
    import re

    semver_pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
    if not re.match(semver_pattern, version):
        raise OnexError(
            f"Version '{version}' does not follow semantic versioning format (e.g., '1.0.0')",
            CoreErrorCode.INVALID_PARAMETER,
        )
    return version


class RuntimeInputState(BaseModel):
    """
    Canonical input state model for runtime_node.
    """

    version: str = Field(
        ...,
        description="Schema version for input state (must be compatible with current schema)",
    )
    runtime_required_field: str = Field(
        ..., description="Required input field for runtime_node"
    )
    runtime_optional_field: Optional[str] = Field(
        default="RUNTIME_DEFAULT_VALUE",
        description="Optional input field for runtime_node",
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        return validate_semantic_version(v)

    @field_validator("runtime_required_field")
    @classmethod
    def validate_runtime_required_field(cls, v: str) -> str:
        if not v or not v.strip():
            raise OnexError(
                "runtime_required_field cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()


class RuntimeOutputState(BaseModel):
    """
    Canonical output state model for runtime_node.
    """

    version: str = Field(
        ..., description="Schema version for output state (must match input version)"
    )
    status: str = Field(..., description="Result status of the runtime operation")
    message: str = Field(..., description="Human-readable result or error message")
    runtime_output_field: Optional[str] = Field(
        default=None, description="Optional output field for runtime_node"
    )

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


def create_runtime_input_state(
    runtime_required_field: str,
    runtime_optional_field: Optional[str] = "RUNTIME_DEFAULT_VALUE",
    version: Optional[str] = None,
) -> RuntimeInputState:
    if version is None:
        version = RUNTIME_STATE_SCHEMA_VERSION
    return RuntimeInputState(
        version=version,
        runtime_required_field=runtime_required_field,
        runtime_optional_field=runtime_optional_field,
    )


def create_runtime_output_state(
    status: str,
    message: str,
    input_state: RuntimeInputState,
    runtime_output_field: Optional[str] = None,
) -> RuntimeOutputState:
    return RuntimeOutputState(
        version=input_state.version,
        status=status,
        message=message,
        runtime_output_field=runtime_output_field,
    )


# === Canonical Input/Output Models for runtime_node ===
# These models are the single source of truth for all input/output state for the runtime_node node.
# Do not duplicate or redefine elsewhere. Update only here for protocol compliance.

RUNTIME_NODE_STATE_SCHEMA_VERSION = "1.0.0"


class RuntimeNodeInputState(BaseModel):
    """
    Canonical input state model for runtime_node.
    """

    version: SemVerModel = Field(
        ...,
        description="Schema version for input state (must be compatible with current schema)",
    )
    required_field: str = Field(
        ..., description="Required input field for runtime_node"
    )
    optional_field: Optional[str] = Field(
        default=None, description="Optional input field for runtime_node"
    )

    @field_validator("required_field")
    @classmethod
    def validate_required_field(cls, v: str) -> str:
        return validate_non_empty_string(v, field_name="required_field")


class RuntimeNodeOutputState(BaseModel):
    """
    Canonical output state model for runtime_node.
    """

    version: SemVerModel = Field(
        ..., description="Schema version for output state (must match input version)"
    )
    status: RegistryOutputStatusEnum = Field(
        ..., description="Result status of the runtime_node operation"
    )
    message: str = Field(..., description="Human-readable result or error message")
    output_field: Optional[OutputFieldModel] = Field(
        default=None,
        description="Extensible output field for runtime_node; must be a Pydantic model",
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        return validate_non_empty_string(v, field_name="message")
