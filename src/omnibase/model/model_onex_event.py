# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.677980'
# description: Stamped by PythonHandler
# entrypoint: python://model_onex_event
# hash: de98dbd4ad2b8aceb9d54f5f0911f0500bb06f4005203f57aa3d6dd44c0b62c8
# last_modified_at: '2025-05-29T14:13:58.847934+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_onex_event.py
# namespace: python://omnibase.model.model_onex_event
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: fe3fe6eb-ac1a-4f91-a5d1-8fba44bbb898
# version: 1.0.0
# === /OmniNode:Metadata ===


from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class OnexEventTypeEnum(str, Enum):
    NODE_START = "NODE_START"
    NODE_SUCCESS = "NODE_SUCCESS"
    NODE_FAILURE = "NODE_FAILURE"
    NODE_REGISTER = "NODE_REGISTER"
    TELEMETRY_OPERATION_START = "TELEMETRY_OPERATION_START"
    TELEMETRY_OPERATION_SUCCESS = "TELEMETRY_OPERATION_SUCCESS"
    TELEMETRY_OPERATION_ERROR = "TELEMETRY_OPERATION_ERROR"
    STRUCTURED_LOG = "STRUCTURED_LOG"
    INTROSPECTION_REQUEST = "INTROSPECTION_REQUEST"
    INTROSPECTION_RESPONSE = "INTROSPECTION_RESPONSE"
    NODE_DISCOVERY_REQUEST = "NODE_DISCOVERY_REQUEST"
    NODE_DISCOVERY_RESPONSE = "NODE_DISCOVERY_RESPONSE"
    NODE_ANNOUNCE = "NODE_ANNOUNCE"  # Emitted by nodes on startup or registration
    NODE_ANNOUNCE_ACCEPTED = "NODE_ANNOUNCE_ACCEPTED"  # Emitted by registry node on successful registration
    NODE_ANNOUNCE_REJECTED = "NODE_ANNOUNCE_REJECTED"  # Emitted by registry node if registration fails
    # Add more event types as needed


class OnexEventMetadataModel(BaseModel):
    # Canonical fields for event metadata; extend for event-type-specific models
    input_state: Optional[dict] = None
    output_state: Optional[dict] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    error_code: Optional[str] = None
    recoverable: Optional[bool] = None
    node_version: Optional[str] = None
    operation_type: Optional[str] = None
    execution_time_ms: Optional[float] = None
    result_summary: Optional[str] = None
    status: Optional[str] = None
    reason: Optional[str] = None
    registry_id: Optional[Union[str, UUID]] = None
    trust_state: Optional[str] = None
    ttl: Optional[int] = None
    # Add more fields as needed for protocol
    # For custom event types, subclass this model


class OnexEvent(BaseModel):
    """
    Canonical event model for ONEX event emission and bus logic.
    Used by all event bus, node runner, and event store components.
    """

    event_id: UUID = Field(default_factory=uuid4, description="Unique event identifier")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Event timestamp (UTC)"
    )
    node_id: Union[str, UUID] = Field(
        ..., description="ID of the node emitting the event"
    )
    event_type: OnexEventTypeEnum = Field(..., description="Type of event emitted")
    correlation_id: Optional[str] = Field(
        default=None, description="Optional correlation ID for request tracking"
    )
    metadata: Optional[OnexEventMetadataModel] = Field(
        default=None, description="Optional event metadata or payload"
    )

# Optionally, document the expected metadata structure for node_announce events:
# NODE_ANNOUNCE metadata fields:
#   node_id: str or UUID
#   metadata_block: dict (canonical node metadata)
#   status: str ("ephemeral" | "online" | "validated")
#   execution_mode: str ("memory" | "container" | "external")
#   inputs: dict (schema summary)
#   outputs: dict (schema summary)
#   graph_binding: Optional[str]
#   trust_state: Optional[str]
#   ttl: Optional[int]
# NODE_ANNOUNCE_ACCEPTED/REJECTED metadata fields:
#   node_id: str or UUID
#   status: str ("accepted" | "rejected")
#   reason: Optional[str] (for rejection)
#   registry_id: Optional[str or UUID]
#   trust_state: Optional[str]
#   ttl: Optional[int]

class TelemetryOperationStartMetadataModel(OnexEventMetadataModel):
    """
    Metadata for TELEMETRY_OPERATION_START events.
    """
    operation: str
    function: str
    args_count: int
    kwargs_keys: list[str]

class TelemetryOperationSuccessMetadataModel(OnexEventMetadataModel):
    """
    Metadata for TELEMETRY_OPERATION_SUCCESS events.
    """
    operation: str
    function: str
    execution_time_ms: float
    result_type: str
    success: bool

class TelemetryOperationErrorMetadataModel(OnexEventMetadataModel):
    """
    Metadata for TELEMETRY_OPERATION_ERROR events.
    """
    operation: str
    function: str
    execution_time_ms: float
    error_type: str
    error_message: str
    success: bool

OnexEvent.model_rebuild()
OnexEventMetadataModel.model_rebuild()
