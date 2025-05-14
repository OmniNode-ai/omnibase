# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: omninode_issue_model
# namespace: omninode.tools.omninode_issue_model
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:55+00:00
# last_modified_at: 2025-04-27T18:12:55+00:00
# entrypoint: omninode_issue_model.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class OmniNodeIssue(BaseModel):
    title: str = Field(..., description="Issue title")
    status: str = Field("Todo", description="Status of the issue")
    priority: str = Field("Medium", description="Priority of the issue")
    notes: Optional[str] = Field("", description="Additional notes")
    context: str = Field(..., description="Context for the issue")
    requirements: List[str] = Field(..., description="List of requirements")
    acceptance_criteria: List[str] = Field(..., description="List of acceptance criteria")
    additional_notes: Optional[str] = Field("", description="Any extra notes")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        allowed = ["Todo", "In Progress", "Done", "Blocked"]
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        allowed = ["Low", "Medium", "High", "Critical"]
        if v not in allowed:
            raise ValueError(f"Priority must be one of {allowed}")
        return v

    @field_validator("requirements", "acceptance_criteria")
    @classmethod
    def non_empty_list(cls, v):
        if not v or not isinstance(v, list) or not all(isinstance(i, str) and i.strip() for i in v):
            raise ValueError("Must be a non-empty list of non-empty strings")
        return v
