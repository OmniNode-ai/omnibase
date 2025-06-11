from pydantic import BaseModel, Field
from typing import List, Union, Literal
from omnibase.enums.enum_node_arg import NodeArgEnum
from ..enums.enum_node_kafka_arg import NodeKafkaArgEnum
from ..enums.enum_node_kafka_command import NodeKafkaCommandEnum
from omnibase.nodes.node_manager.v1_0_0.models.model_metadata import ModelMetadata

class MessageArgument(BaseModel):
    """Secure message argument with validation."""
    flag: Literal["--message"] = "--message"
    value: str = Field(..., max_length=1000, description="Message content (max 1000 chars)")

class GroupIdArgument(BaseModel):
    """Secure group ID argument with validation."""
    flag: Literal["--group-id"] = "--group-id"
    value: str = Field(..., pattern="^[a-zA-Z0-9_-]+$", max_length=100, description="Valid group ID (alphanumeric, underscore, hyphen only)")

class TopicArgument(BaseModel):
    """Secure topic argument with validation."""
    flag: Literal["--topic"] = "--topic"
    value: str = Field(..., pattern="^[a-zA-Z0-9_-]+$", max_length=100, description="Valid topic name (alphanumeric, underscore, hyphen only)")

# Union of all valid typed arguments
KafkaTypedArgument = Union[MessageArgument, GroupIdArgument, TopicArgument]

class ModelCliCommand(BaseModel):
    """
    Canonical model for CLI command execution in the kafka node.
    command_name must be a NodeKafkaCommandEnum value.
    args may include both shared (NodeArgEnum) and node-specific (NodeKafkaArgEnum) flags,
    or typed arguments for security.
    """
    command_name: NodeKafkaCommandEnum = Field(..., description="The CLI command to execute.")
    args: List[Union[NodeArgEnum, NodeKafkaArgEnum]] = Field(default_factory=list, description="CLI arguments (enum values only for security).")
    typed_args: List[KafkaTypedArgument] = Field(default_factory=list, description="Typed arguments with validation for security.")
    metadata: ModelMetadata = Field(default_factory=lambda: ModelMetadata(name="kafka_cli_command"), description="Metadata for the CLI command.") 