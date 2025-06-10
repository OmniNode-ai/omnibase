from pydantic import BaseModel, Field
from typing import List, Optional, Union
from omnibase.enums.enum_node_arg import NodeArgEnum
from ..enums.enum_node_manager_arg import NodeManagerArgEnum
from ..enums.enum_node_manager_command import NodeManagerCommandEnum
from .model_metadata import ModelMetadata

class ModelCliCommand(BaseModel):
    """
    Canonical model for CLI command execution in node_manager.
    args may include both shared (NodeArgEnum) and node-specific (NodeManagerArgEnum) flags.
    """
    command_name: NodeManagerCommandEnum = Field(..., description="The CLI command to execute.")
    args: List[Union[NodeArgEnum, NodeManagerArgEnum]] = Field(default_factory=list, description="List of CLI argument flags (shared and node-specific).")
    metadata: Optional[ModelMetadata] = Field(default=None, description="Optional canonical metadata for the CLI command.") 