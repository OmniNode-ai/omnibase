from pydantic import BaseModel, Field
from typing import Dict

class ContextModel(BaseModel):
    data: Dict[str, str] = Field(default_factory=dict) 