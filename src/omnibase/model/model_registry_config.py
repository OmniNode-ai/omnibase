"""
ModelRegistryConfig: Canonical registry configuration model for ONEX scenarios.
Follows ONEX standards for model prefixing (see docs/standards.md).
"""
from typing import Dict, Optional
from pydantic import BaseModel, Field
from omnibase.model.model_tool_collection import ToolCollection

class ModelRegistryConfig(BaseModel):
    """
    Canonical registry configuration for a scenario.
    - name: Name of this registry config (e.g., 'default', 'mock', 'kafka').
    - tools: Mapping of canonical tool keys to tool implementations.
    - description: Optional description or notes for this config.
    - version_constraints: Optional version constraints for tools.
    """
    name: str = Field(..., description="Name of this registry config (e.g., 'default', 'mock', 'kafka').")
    tools: ToolCollection = Field(..., description="Mapping of canonical tool keys to tool implementations.")
    description: Optional[str] = Field(None, description="Optional description or notes for this config.")
    version_constraints: Optional[Dict[str, str]] = Field(default_factory=dict, description="Optional version constraints for tools.")

    def validate_tools(self, required_keys: list) -> None:
        missing = [k for k in required_keys if k not in self.tools]
        if missing:
            raise ValueError(f"ModelRegistryConfig '{self.name}' is missing required tools: {missing}") 