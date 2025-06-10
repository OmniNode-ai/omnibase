# AUTO-GENERATED FILE. DO NOT EDIT.
# Generated from contract.yaml
# contract_hash: 800e01a21508c6c2fcf41d1b0ab8d5cb1f9e3466f74a6817b65a424d57d770c5
# To regenerate: poetry run onex run schema_generator_node --args='["src/omnibase/nodes/node_manager/v1_0_0/contract.yaml", "src/omnibase/nodes/node_manager/v1_0_0/models/state.py"]'
from typing import Optional
from pydantic import BaseModel, field_validator
from omnibase.model.model_output_field import OnexFieldModel
from omnibase.enums.onex_status import OnexStatus
from omnibase.model.model_semver import SemVerModel


class ModelNodeManagerOutputField(BaseModel):
    result: str
    details: Optional[str]

class NodeManagerInputState(BaseModel):
    version: SemVerModel  # Schema version for input state
    input_field: str  # Required input field for node_manager
    optional_field: OnexFieldModel = None  # Optional input field for node_manager
    external_dependency: Optional[bool] = None  # Optional flag to simulate integration context for scenario-driven testing
    event_id: Optional[str] = None  # Unique event identifier (UUID)
    correlation_id: Optional[str] = None  # Correlation ID for tracing requests/events
    node_name: Optional[str] = None  # Name of the node processing the event
    node_version: Optional[SemVerModel] = None  # Version of the node
    timestamp: Optional[str] = None  # ISO8601 timestamp of the event

    @field_validator("version", mode="before")
    @classmethod
    def parse_version(cls, v):
        from omnibase.model.model_semver import SemVerModel
        if isinstance(v, SemVerModel):
            return v
        if isinstance(v, str):
            return SemVerModel.parse(v)
        if isinstance(v, dict):
            return SemVerModel(**v)
        raise ValueError("version must be a string, dict, or SemVerModel")

    @field_validator("event_id")
    @classmethod
    def validate_event_id(cls, v):
        import uuid
        try:
            uuid.UUID(str(v))
            return str(v)
        except Exception:
            raise ValueError("event_id must be a valid UUID string")

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v):
        from datetime import datetime
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except Exception:
            raise ValueError("timestamp must be a valid ISO8601 string")

class NodeManagerOutputState(BaseModel):
    version: SemVerModel  # Schema version for output state (matches input)
    status: OnexStatus  # Execution status  # Allowed: ['success', 'warning', 'error', 'skipped', 'fixed', 'partial', 'info', 'unknown']
    message: str  # Human-readable result message
    output_field: ModelNodeManagerOutputField = None  # 
    event_id: Optional[str] = None  # Unique event identifier (UUID)
    correlation_id: Optional[str] = None  # Correlation ID for tracing requests/events
    node_name: Optional[str] = None  # Name of the node processing the event
    node_version: Optional[SemVerModel] = None  # Version of the node
    timestamp: Optional[str] = None  # ISO8601 timestamp of the event

    @field_validator("version", mode="before")
    @classmethod
    def parse_version(cls, v):
        from omnibase.model.model_semver import SemVerModel
        if isinstance(v, SemVerModel):
            return v
        if isinstance(v, str):
            return SemVerModel.parse(v)
        if isinstance(v, dict):
            return SemVerModel(**v)
        raise ValueError("version must be a string, dict, or SemVerModel")

    @field_validator("event_id")
    @classmethod
    def validate_event_id(cls, v):
        import uuid
        try:
            uuid.UUID(str(v))
            return str(v)
        except Exception:
            raise ValueError("event_id must be a valid UUID string")

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v):
        from datetime import datetime
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except Exception:
            raise ValueError("timestamp must be a valid ISO8601 string")
