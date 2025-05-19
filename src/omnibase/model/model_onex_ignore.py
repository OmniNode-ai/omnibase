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
