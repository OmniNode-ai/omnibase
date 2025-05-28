# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: model_onex_event.py
# version: 1.0.0
# uuid: fe3fe6eb-ac1a-4f91-a5d1-8fba44bbb898
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.677980
# last_modified_at: 2025-05-28T17:20:04.438522
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: b5339c3ee71bbebdbb0d7b26678aac975e104424b14614e130653c365b0b2949
# entrypoint: python@model_onex_event.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.model_onex_event
# meta_type: tool
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
