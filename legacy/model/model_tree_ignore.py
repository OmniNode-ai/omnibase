from typing import List, Optional
from pydantic import BaseModel, Field

class TreeIgnorePattern(BaseModel):
    """
    Submodel for a single ignore pattern in .treeignore.
    """
    pattern: str = Field(..., description="Glob pattern to ignore.")
    description: Optional[str] = Field(None, description="Optional description of the pattern.")

class TreeIgnoreModel(BaseModel):
    """
    Protocol model for .treeignore files. Defines ignore patterns and optional metadata.
    """
    metadata_version: str = Field(default="0.1", description="Version of the .treeignore schema.")
    patterns: List[TreeIgnorePattern] = Field(..., description="List of ignore patterns.")
    description: Optional[str] = Field(default=None, description="Optional description of the ignore file.")
    author: Optional[str] = Field(default=None, description="Author of the ignore file.") 