# AUTO-GENERATED FILE. DO NOT EDIT.
# Generated from contract.yaml
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.enums.onex_status import OnexStatus
from omnibase.model.model_output_field import OnexFieldModel
from omnibase.model.model_semver import SemVerModel
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models.model_kafka_event_bus_config import (
    ModelKafkaEventBusConfig,
)
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models.model_kafka_event_bus_output_field import (
    ModelKafkaEventBusOutputField,
)


class ModelKafkaEventBusInputState(BaseModel):
    version: str  # Schema version for input state
    input_field: str  # Required input field for template node
    optional_field: OnexFieldModel = None  # Optional input field for template node
    config: Optional[ModelKafkaEventBusConfig] = Field(
        default=None,
        description="Kafka event bus configuration (optional, overrides defaults)",
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


class ModelKafkaEventBusOutputState(BaseModel):
    version: SemVerModel  # Schema version for output state (matches input)
    status: OnexStatus  # Execution status  # Allowed: ['success', 'warning', 'error', 'skipped', 'fixed', 'partial', 'info', 'unknown']
    message: str  # Human-readable result message
    output_field: Optional[ModelKafkaEventBusOutputField] = (
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


class ModelKafkaEventBusInputOutputState(BaseModel):
    input_state: ModelKafkaEventBusInputState
    output_state: ModelKafkaEventBusOutputState
