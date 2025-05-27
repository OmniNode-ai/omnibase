# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_onex_ignore.py
# version: 1.0.0
# uuid: 5fc57266-2de0-4feb-8fed-cd22784d40f1
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165983
# last_modified_at: 2025-05-21T16:42:46.077557
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: bced469da0ee0a2129c11d1f1f2ad03016218cef95308c8b65b3ec237da25b2a
# entrypoint: python@model_onex_ignore.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_onex_ignore
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
                "validator": {"patterns": ["tests/shared/legacy/*"]},
                "tree": {"patterns": ["docs/generated/*"]},
                "all": {"patterns": ["*.bak", "*.tmp"]},
            }
        },
    )
