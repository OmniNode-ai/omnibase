from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class OnexEventTypeEnum(str, Enum):
    NODE_START = "NODE_START"
    NODE_SUCCESS = "NODE_SUCCESS"
    NODE_FAILURE = "NODE_FAILURE"
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
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional event metadata or payload"
    )
