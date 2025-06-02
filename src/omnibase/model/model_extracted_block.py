"""
Strongly typed models for extracted metadata blocks, decoupled from model_node_metadata.py to avoid circular imports.
"""

from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock


class ExtractedBlockModel(BaseModel):
    """
    Result model for extract_block protocol method.
    """

    metadata: Optional["NodeMetadataBlock"] = Field(
        None, description="Extracted metadata block (NodeMetadataBlock or None)"
    )
    body: Optional[str] = Field(
        None, description="File content with metadata block removed"
    )


# NOTE: model_rebuild() is not called here to avoid circular import issues.
# If runtime forward reference resolution is needed, call ExtractedBlockModel.model_rebuild() after all models are loaded (e.g., in CLI entrypoint or test setup).
