# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:25.677980'
# description: Stamped by PythonHandler
# entrypoint: python://model_onex_event.py
# hash: 7c61f54a712c05e17c9ef7c40f032bda930863b143a42de5616a8f0fbc5912b6
# last_modified_at: '2025-05-29T11:50:10.998584+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_onex_event.py
# namespace: omnibase.model_onex_event
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
    # Add more event types as needed


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
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional event metadata or payload"
    )
