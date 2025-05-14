
# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "model_prompt_log_entry"
# namespace: "omninode.tools.model_prompt_log_entry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "model_prompt_log_entry.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseLogEntry', 'BaseModel']
# base_class: ['BaseLogEntry', 'BaseModel']
# mock_safe: true
# === /OmniNode:Metadata ===






from datetime import datetime
from typing import List, Optional
from uuid import UUID

from foundation.logging.model.model_log_entry_abc import BaseLogEntry, LogTypeTag
from pydantic import BaseModel, Field
# TODO: IPromptLogEntry import removed; interface not found in codebase. Restore or replace with standards-compliant interface if required.


class ModelPromptLogEntry(BaseModel, BaseLogEntry):
    """
    Pydantic model for prompt log entries, enforcing required fields and structure.
    Implements IPromptLogEntry interface.
    Complies with project logging/metadata standards.
    - ticket_reference: Optional URL or ticket ID for associated task/ticket (e.g., GitHub, Jira, etc.)
    - agent_name: Optional name of the agent (if applicable)
    - github_reference: Optional GitHub reference (harmonized with velocity log entry)
    - type_tags: List of allowed LogTypeTag enum values
    """
    uuid: UUID = Field(..., description="UUID v4, lowercase, no braces/quotes")
    timestamp: datetime = Field(..., description="Timestamp of the log entry")
    parent_id: Optional[UUID] = Field(None, description="Optional parent log entry UUID")
    type_tags: List[LogTypeTag] = Field(..., description="List of allowed LogTypeTag enum values for the log entry")
    prompt: str = Field(..., description="The prompt text")
    summary: str = Field(..., description="Summary of work or action")
    lessons_learned: Optional[str] = Field(None, description="Lessons learned or notes")
    ticket_reference: Optional[str] = Field(None, description="Optional ticket reference (URL or ID)")
    github_reference: Optional[str] = Field(None, description="Optional GitHub reference (harmonized field)")
    agent_name: Optional[str] = Field(None, description="Optional agent name")
    response_summary: Optional[str] = Field(None, description="Optional response summary")
    execution_context: Optional[str] = Field(None, description="Optional execution context")

    def to_dict(self) -> dict:
        return self.dict()