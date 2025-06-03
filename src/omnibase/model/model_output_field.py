from typing import Protocol, Any
from pydantic import BaseModel, Field
from typing import Optional

class OutputFieldModel(BaseModel):
    """
    Canonical, extensible output field model for ONEX nodes.
    Use this as the base for all node output fields that need to return arbitrary or structured data.
    Extend or subclass as needed for node-specific outputs.
    """
    data: Optional[dict] = Field(default=None, description="Arbitrary output data for ONEX node")

    # Optionally, add more required methods or attributes as needed 