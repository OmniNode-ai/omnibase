from typing import Optional, Any, TYPE_CHECKING
from pydantic import BaseModel, Field
from pathlib import Path
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.enums.handler_source import HandlerSourceEnum
from omnibase.model.model_extracted_block import ExtractedBlockModel

if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock

class CanHandleResultModel(BaseModel):
    """
    Result model for can_handle protocol method.
    """
    can_handle: bool = Field(..., description="Whether the handler can process the file/content.")

    def __bool__(self):
        return self.can_handle

class SerializedBlockModel(BaseModel):
    """
    Result model for serialize_block protocol method.
    """
    serialized: str = Field(..., description="Serialized metadata block as a string.")

class HandlerMetadataModel(BaseModel):
    """
    Canonical metadata for a file type handler.
    """
    handler_name: str = Field(..., description="Handler name.")
    handler_version: str = Field(..., description="Handler version.")
    handler_author: str = Field(..., description="Handler author.")
    handler_description: str = Field(..., description="Handler description.")
    supported_extensions: list[str] = Field(default_factory=list, description="Supported file extensions.")
    supported_filenames: list[str] = Field(default_factory=list, description="Supported special filenames.")
    handler_priority: int = Field(..., description="Handler priority (higher = preferred).")
    requires_content_analysis: bool = Field(..., description="Whether handler requires content analysis.")
    source: HandlerSourceEnum = Field(..., description="Handler source (core, plugin, runtime, etc.)") 