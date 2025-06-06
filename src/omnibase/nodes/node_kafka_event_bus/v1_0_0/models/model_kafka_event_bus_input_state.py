from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.model.model_semver import SemVerModel


class ModelKafkaEventBusInputState(BaseModel):
    """
    Canonical input state for KafkaEventBus.
    version: Must be a quoted string (e.g., '1.0.0'), a dict, or a SemVerModel.
    """

    version: SemVerModel
    input_field: str  # Required input field for template node
    integration: Optional[bool] = None
    custom: Optional[Any] = None
    # ... other fields as needed ...

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
