# AUTO-GENERATED FILE. DO NOT EDIT.
# Generated from contract.yaml
from typing import Optional
from pydantic import BaseModel, Field
from omnibase.model.model_output_field import OnexFieldModel
from omnibase.enums.onex_status import OnexStatus
from omnibase.model.model_semver import SemVerModel
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models.config import KafkaEventBusConfigModel


class NodeKafkaEventBusInputState(BaseModel):
    version: SemVerModel  # Schema version for input state
    input_field: str  # Required input field for template node
    optional_field: OnexFieldModel = None  # Optional input field for template node
    config: Optional[KafkaEventBusConfigModel] = Field(default=None, description="Kafka event bus configuration (optional, overrides defaults)")

class NodeKafkaEventBusOutputState(BaseModel):
    version: SemVerModel  # Schema version for output state (matches input)
    status: OnexStatus  # Execution status  # Allowed: ['success', 'warning', 'error', 'skipped', 'fixed', 'partial', 'info', 'unknown']
    message: str  # Human-readable result message
    output_field: OnexFieldModel = None  # 
