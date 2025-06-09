from pydantic import BaseModel, Field
from typing import Optional
from .model_metadata import ModelMetadata

class ModelFileContent(BaseModel):
    """
    Canonical model for file content and metadata in file generation tools.
    """
    content: str = Field(..., description="File content as a string.")
    encoding: str = Field(default="utf-8", description="File encoding.")
    metadata: Optional[ModelMetadata] = Field(default=None, description="Optional canonical metadata for the file.") 