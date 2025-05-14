# === OmniNode:Tool_Metadata ===
# name: model_velocity_log_entry
# version: 0.1.0
# === /OmniNode:Tool_Metadata ===

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from foundation.logging.model.model_log_entry_abc import BaseLogEntry, LogTypeTag
from foundation.protocol.interface_log_entry import IVelocityLogEntry
from pydantic import BaseModel, Field


class ModelVelocityLogEntry(BaseModel):
    """
    Pydantic model for velocity log entries, enforcing required fields and structure.
    Implements IVelocityLogEntry interface.
    Complies with project logging/metadata standards.
    - github_reference: Optional GitHub reference
    - ticket_reference: Optional ticket reference (harmonized with prompt log entry)
    - type_tags: List of allowed LogTypeTag enum values
    """
    uuid: UUID = Field(..., description="UUID v4, lowercase, no braces/quotes")
    timestamp: datetime = Field(..., description="Timestamp of the log entry")
    parent_id: Optional[UUID] = Field(None, description="Optional parent log entry UUID")
    type_tags: List[LogTypeTag] = Field(..., description="List of allowed LogTypeTag enum values for the log entry")
    summary: str = Field(..., description="Summary of work or action")
    metrics: Dict[str, float] = Field(..., description="Velocity metrics (e.g., lines changed, files modified)")
    lessons_learned: Optional[str] = Field(None, description="Lessons learned or notes")
    github_reference: Optional[str] = Field(None, description="Optional GitHub reference")
    ticket_reference: Optional[str] = Field(None, description="Optional ticket reference (harmonized field)")
    agent_name: Optional[str] = Field(None, description="Optional agent name")
    response_summary: Optional[str] = Field(None, description="Optional response summary")
    execution_context: Optional[str] = Field(None, description="Optional execution context")

    def to_dict(self) -> dict:
        return self.dict()
