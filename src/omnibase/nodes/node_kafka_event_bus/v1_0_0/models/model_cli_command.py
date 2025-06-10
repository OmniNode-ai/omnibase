from pydantic import BaseModel, Field
from typing import List, Optional, Union
from omnibase.enums.enum_node_arg import NodeArgEnum
from ..enums.enum_node_kafka_arg import NodeKafkaArgEnum
from ..enums.enum_node_kafka_command import NodeKafkaCommandEnum
from omnibase.nodes.node_manager.v1_0_0.models.model_metadata import ModelMetadata

class ModelCliCommand(BaseModel):
    """
    Canonical model for CLI command execution in the kafka node.
    command_name must be a NodeKafkaCommandEnum value.
    args may include both shared (NodeArgEnum) and node-specific (NodeKafkaArgEnum) flags.
    """
    command_name: NodeKafkaCommandEnum = Field(..., description="The CLI command to execute.")
    args: List[Union[NodeArgEnum, NodeKafkaArgEnum]] = Field(default_factory=list, description="List of CLI argument flags (shared and node-specific).")
    metadata: Optional[ModelMetadata] = Field(default=None, description="Optional canonical metadata for the CLI command.") 