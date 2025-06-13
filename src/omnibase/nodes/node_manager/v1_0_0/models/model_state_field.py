from pydantic import BaseModel
from typing import Optional, List, Any


class StateFieldModel(BaseModel):
    """Represents a field in a contract state schema"""
    name: str
    type: str
    description: str
    required: bool
    default: Optional[Any] = None
    enum_values: Optional[List[str]] = None
    format: Optional[str] = None
    ref: Optional[str] = None 