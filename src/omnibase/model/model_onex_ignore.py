# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.986915'
# description: Stamped by PythonHandler
# entrypoint: python://model_onex_ignore.py
# hash: 2b4d7ae0f9d96aebaa45efb78b2186424022eb7b03c46e30b438003b11375ced
# last_modified_at: '2025-05-29T11:50:11.004257+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_onex_ignore.py
# namespace: omnibase.model_onex_ignore
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: cee08e8c-c690-411d-be17-7ba8658a92fa
# version: 1.0.0
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
                "validator": {"patterns": ["tests/shared/legacy/*"]},
                "tree": {"patterns": ["docs/generated/*"]},
                "all": {"patterns": ["*.bak", "*.tmp"]},
            }
        },
    )
