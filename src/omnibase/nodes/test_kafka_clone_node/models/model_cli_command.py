from pydantic import BaseModel, Field
from typing import List, Optional, Union
from omnibase.enums.enum_node_arg import NodeArgEnum
from ..enums.enum_test_kafka_clone_node_arg import TestKafkaCloneNodeArgEnum
from ..enums.enum_test_kafka_clone_node_command import TestKafkaCloneNodeCommandEnum
from .model_metadata import ModelMetadata

class ModelCliCommand(BaseModel):
    """
    Canonical model for CLI command execution in the test_kafka_clone node.
    command_name must be a TestKafkaCloneNodeCommandEnum value.
    args may include both shared (NodeArgEnum) and node-specific (TestKafkaCloneNodeArgEnum) flags.
    """
    command_name: TestKafkaCloneNodeCommandEnum = Field(..., description="The CLI command to execute.")
    args: List[Union[NodeArgEnum, TestKafkaCloneNodeArgEnum]] = Field(default_factory=list, description="List of CLI argument flags (shared and node-specific).")
    metadata: Optional[ModelMetadata] = Field(default=None, description="Optional canonical metadata for the CLI command.") 