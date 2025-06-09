from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional
from .model_validation_target_type import ModelValidationTargetType
from .model_metadata import ModelMetadata

class ModelValidationTarget(BaseModel):
    """
    Canonical input model for validation engine tools.
    Specifies the target node, contract, or artifact to validate.
    Extensible: target_type is a model, not an Enum, to support plugins/custom types.
    Optionally includes canonical metadata.
    """
    target_path: Path = Field(..., description="Path to the node, contract, or artifact to validate.")
    target_type: Optional[ModelValidationTargetType] = Field(default=None, description="Type of target (model, extensible for plugins/custom types).")
    description: Optional[str] = Field(default=None, description="Optional description or context for the validation target.")
    metadata: Optional[ModelMetadata] = Field(default=None, description="Optional canonical metadata for the validation target.") 