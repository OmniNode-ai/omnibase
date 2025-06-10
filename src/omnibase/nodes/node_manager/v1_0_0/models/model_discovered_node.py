from typing import Optional
from pydantic import BaseModel

class ModelDiscoveredNode(BaseModel):
    """
    Canonical model for discovered ONEX nodes (for validation, discovery, and registry).
    """
    name: str
    version: str
    module_path: str
    introspection_available: bool
    cli_entrypoint: Optional[str] = None
    error_count: int = 0 