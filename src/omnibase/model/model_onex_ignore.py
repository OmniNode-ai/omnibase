# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 5e7d0808-b685-4079-9c85-9cbaa73b913e
# name: model_onex_ignore.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:03.571998
# last_modified_at: 2025-05-19T16:20:03.572000
# description: Stamped Python file: model_onex_ignore.py
# state_contract: none
# lifecycle: active
# hash: 3acbf08675ad4c6294908343f26f226fab22764c8e6ec5c9670b86a767227f9a
# entrypoint: {'type': 'python', 'target': 'model_onex_ignore.py'}
# namespace: onex.stamped.model_onex_ignore.py
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class OnexIgnoreSection(BaseModel):
    patterns: List[str] = Field(
        default_factory=list, description="Glob patterns to ignore for this tool/type."
    )


class OnexIgnoreModel(BaseModel):
    stamper: Optional[OnexIgnoreSection] = None
    validator: Optional[OnexIgnoreSection] = None
    tree: Optional[OnexIgnoreSection] = None
    all: Optional[OnexIgnoreSection] = None
    # Allow arbitrary tool keys for extensibility
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "stamper": {"patterns": ["src/omnibase/schemas/*.yaml", "*.json"]},
                "validator": {"patterns": ["tests/legacy/*"]},
                "tree": {"patterns": ["docs/generated/*"]},
                "all": {"patterns": ["*.bak", "*.tmp"]},
            }
        },
    )
