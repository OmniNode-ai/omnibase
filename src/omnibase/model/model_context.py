from typing import Dict

from pydantic import BaseModel, Field


class ContextModel(BaseModel):
    data: Dict[str, str] = Field(default_factory=dict)
