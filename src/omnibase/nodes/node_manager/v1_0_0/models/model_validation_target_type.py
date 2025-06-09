from pydantic import BaseModel, Field
from typing import Optional
from .model_metadata import ModelMetadata

class ModelValidationTargetType(BaseModel):
    """
    Extensible model for validation target type.
    Allows for plugin/custom types with canonical metadata.
    """
    name: str = Field(..., description="Name of the target type (e.g., 'node', 'contract', 'artifact', or custom type).")
    metadata: Optional[ModelMetadata] = Field(default=None, description="Optional metadata for the target type.") 