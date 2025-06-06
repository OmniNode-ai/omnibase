# AUTO-GENERATED FILE. DO NOT EDIT.
# Generated from contract.yaml
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.enums.onex_status import OnexStatus
from omnibase.model.model_output_field import OnexFieldModel
from omnibase.model.model_semver import SemVerModel
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models.model_kafka_event_bus_config import (
    ModelEventBusConfig,
)
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models.model_kafka_event_bus_output_field import (
    ModelEventBusOutputField,
)
from omnibase.model.model_event_bus_input_state import ModelEventBusInputState
from omnibase.model.model_event_bus_output_state import ModelEventBusOutputState


class ModelEventBusInputState(BaseModel):
    """
    Input state for event bus nodes.
    """
    version: str  # Schema version for input state
    input_field: str  # Required input field for template node
    optional_field: OnexFieldModel = None  # Optional input field for template node
    config: Optional[ModelEventBusConfig] = Field(
        default=None,
        description="Event bus configuration (optional, overrides defaults)",
    )

    @field_validator("version")
    @classmethod
    def validate_version(cls, v):
        if isinstance(v, SemVerModel):
            return str(v)
        if isinstance(v, str):
            SemVerModel.parse(v)
            return v
        if isinstance(v, dict):
            SemVerModel(**v)
            return str(SemVerModel(**v))
        raise ValueError(
            "version must be a valid semantic version string, dict, or SemVerModel"
        )


class ModelEventBusOutputState(BaseModel):
    """
    Output state for event bus nodes.
    """
    version: SemVerModel  # Schema version for output state (matches input)
    status: OnexStatus  # Execution status  # Allowed: ['success', 'warning', 'error', 'skipped', 'fixed', 'partial', 'info', 'unknown']
    message: str  # Human-readable result message
    output_field: Optional[ModelEventBusOutputField] = (
        None  # Canonical output field
    )

    @field_validator("version", mode="before")
    @classmethod
    def parse_version(cls, v):
        if isinstance(v, SemVerModel):
            return v
        if isinstance(v, str):
            return SemVerModel.parse(v)
        if isinstance(v, dict):
            return SemVerModel(**v)
        raise ValueError("version must be a string, dict, or SemVerModel")


class ModelEventBusInputOutputState(BaseModel):
    input_state: ModelEventBusInputState
    output_state: ModelEventBusOutputState
