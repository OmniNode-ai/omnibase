from pydantic import BaseModel, Field
from typing import List, Optional, Union
from omnibase.enums.enum_node_arg import NodeArgEnum
from ..enums.enum_template_node_arg import TemplateNodeArgEnum
from ..enums.enum_template_node_command import TemplateNodeCommandEnum
from .model_metadata import ModelMetadata

class ModelCliCommand(BaseModel):
    """
    Canonical model for CLI command execution in the template node.
    command_name must be a TemplateNodeCommandEnum value.
    args may include both shared (NodeArgEnum) and node-specific (TemplateNodeArgEnum) flags.
    """
    command_name: TemplateNodeCommandEnum = Field(..., description="The CLI command to execute.")
    args: List[Union[NodeArgEnum, TemplateNodeArgEnum]] = Field(default_factory=list, description="List of CLI argument flags (shared and node-specific).")
    metadata: Optional[ModelMetadata] = Field(default=None, description="Optional canonical metadata for the CLI command.") 