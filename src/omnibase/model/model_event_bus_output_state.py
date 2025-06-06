from typing import Optional
from pydantic import BaseModel, Field, field_validator
from omnibase.enums.onex_status import OnexStatus
from omnibase.model.model_semver import SemVerModel
from omnibase.model.model_event_bus_output_field import ModelEventBusOutputField

class ModelEventBusOutputState(BaseModel):
    """
    Output state for event bus nodes.
    """
    version: SemVerModel  # Schema version for output state (matches input)
    status: OnexStatus  # Execution status
    message: str  # Human-readable result message
    output_field: Optional[ModelEventBusOutputField] = None  # Canonical output field

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