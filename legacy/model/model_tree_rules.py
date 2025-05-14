from typing import List, Optional
from pydantic import BaseModel, Field

class TreeRule(BaseModel):
    """
    Rule for validating files and directories at a specific path in the directory tree.
    """
    path: str = Field(..., description="Relative path where this rule applies.")
    allowed_files: Optional[List[str]] = Field(default=None, description="Glob patterns for allowed files.")
    allowed_dirs: Optional[List[str]] = Field(default=None, description="Glob patterns for allowed directories.")
    required_files: Optional[List[str]] = Field(default=None, description="Files that must exist at this path.")
    required_dirs: Optional[List[str]] = Field(default=None, description="Directories that must exist at this path.")
    deny_unlisted: bool = Field(default=True, description="If true, files/dirs not listed are forbidden.")
    allow_flexible: bool = Field(default=False, description="If true, allows extra files/dirs beyond those listed.")
    description: Optional[str] = Field(default=None, description="Description of the rule.")
    notes: Optional[str] = Field(default=None, description="Additional notes.")

class TreeRulesModel(BaseModel):
    """
    Model for .treerules files, containing a list of rules for directory tree validation.
    """
    rules: List[TreeRule] = Field(..., description="List of rules for directory tree validation.")
    version: Optional[str] = Field(default="1.0", description="Schema version.")
    description: Optional[str] = Field(default=None, description="Description of the ruleset.") 