from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from pathlib import Path
from omnibase.enums.enum_dependency_mode import DependencyModeEnum
from omnibase.model.model_external_service_config import ModelExternalServiceConfig
from omnibase.model.model_tool_collection import ToolCollection


class ModelRegistryResolutionContext(BaseModel):
    """
    Canonical model for registry resolution context.
    Contains all information needed to resolve and configure a registry for scenario execution.
    """
    scenario_path: Optional[Path] = Field(None, description="Path to the scenario YAML file")
    dependency_mode: DependencyModeEnum = Field(
        DependencyModeEnum.MOCK,
        description="Resolved dependency mode for tool injection"
    )
    external_services: Dict[str, ModelExternalServiceConfig] = Field(
        default_factory=dict,
        description="External service configurations when dependency_mode is REAL"
    )
    registry_tools: ToolCollection = Field(
        default_factory=dict,
        description="Tool collection for registry injection"
    )
    node_dir: Optional[Path] = Field(None, description="Node directory for context-aware tools")
    force_dependency_mode: Optional[DependencyModeEnum] = Field(
        None,
        description="CLI override for dependency mode (for debugging/CI)"
    )
    
    def get_effective_dependency_mode(self) -> DependencyModeEnum:
        """Get the effective dependency mode, considering force override."""
        return self.force_dependency_mode or self.dependency_mode
    
    def has_external_service(self, service_name: str) -> bool:
        """Check if a specific external service is configured."""
        return service_name in self.external_services
    
    def get_external_service(self, service_name: str) -> Optional[ModelExternalServiceConfig]:
        """Get configuration for a specific external service."""
        return self.external_services.get(service_name)


class ModelRegistryResolutionResult(BaseModel):
    """
    Result model for registry resolution operations.
    Contains the resolved registry and metadata about the resolution process.
    """
    registry: Any = Field(..., description="The resolved registry instance")
    resolution_context: ModelRegistryResolutionContext = Field(
        ..., description="Context used for resolution"
    )
    resolution_log: list[str] = Field(
        default_factory=list,
        description="Log of resolution steps for audit and debugging"
    )
    
    def add_log_entry(self, message: str) -> None:
        """Add a log entry to the resolution process."""
        self.resolution_log.append(message) 