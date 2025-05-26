# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: model_onex_event.py
# version: 1.0.0
# uuid: 17bce001-849a-4824-b5e9-9be667c6dada
# author: OmniNode Team
# created_at: 2025-05-22T17:18:16.700974
# last_modified_at: 2025-05-22T21:19:13.358551
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: b469fa7134c7f1649eb8583ca689296afcfd361398d1c77b657ba4e75bf58625
# entrypoint: python@model_onex_event.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_onex_event
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
    TELEMETRY_OPERATION_START = "TELEMETRY_OPERATION_START"
    TELEMETRY_OPERATION_SUCCESS = "TELEMETRY_OPERATION_SUCCESS"
    TELEMETRY_OPERATION_ERROR = "TELEMETRY_OPERATION_ERROR"
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
