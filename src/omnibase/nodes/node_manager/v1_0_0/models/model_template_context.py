from pydantic import BaseModel
from typing import Optional
from .model_metadata import ModelMetadata
from omnibase.model.model_semver import SemVerModel
from pathlib import Path

class ModelTemplateContext(BaseModel):
    """
    Canonical context model for template rendering in node_manager.
    Add fields as needed for your node generation and template logic.
    """
    node_name: str
    node_class: str  # Main node class name
    node_id: str  # Node ID string (lowercase, underscores)
    node_id_upper: str  # Node ID in uppercase (for constants)
    author: str
    year: int  # Copyright year
    description: Optional[str] = None
    version: Optional[SemVerModel] = None
    metadata: Optional[ModelMetadata] = None

class ModelRenderedTemplate(BaseModel):
    """
    Canonical model for rendered template output.
    """
    content: str 

class ModelRegenerationTarget(BaseModel):
    """
    Canonical model for specifying a regeneration target (artifact or directory).
    """
    path: Path
    type: Optional[str] = None  # Optionally use an Enum for artifact type 