from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from omnibase.model.model_semver import SemVerModel

class ModelMetadata(BaseModel):
    """
    Canonical metadata model for ONEX nodes, targets, and artifacts.
    Reuse this model for all metadata fields across the codebase.
    """
    description: Optional[str] = Field(default=None, description="Description of the entity.")
    version: Optional[SemVerModel] = Field(default=None, description="Semantic version, if applicable.")
    author: Optional[str] = Field(default=None, description="Author or owner of the entity.")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp, if available.") 