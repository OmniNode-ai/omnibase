"""
ModelArtifactTypeConfig: Canonical artifact type config model for ONEX scenarios.
Follows ONEX standards for model prefixing (see docs/standards.md).
"""
from typing import Optional
from pydantic import BaseModel, Field

class ModelArtifactTypeConfig(BaseModel):
    name: str = Field(
        ..., description="Artifact type name (e.g., nodes, cli_tools, modules)"
    )
    metadata_file: str = Field(
        ..., description="Canonical metadata filename for this artifact type"
    )
    version_pattern: Optional[str] = Field(
        None, description="Glob or pattern for version directories (e.g., v*)"
    ) 