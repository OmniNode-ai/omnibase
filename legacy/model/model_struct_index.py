# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "model_struct_index"
# namespace: "omninode.tools.model_struct_index"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:01+00:00"
# last_modified_at: "2025-05-05T12:44:01+00:00"
# entrypoint: "model_struct_index.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseModel']
# base_class: ['BaseModel']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from typing import List, Optional, Dict, Any, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, field_validator

if TYPE_CHECKING:
    from foundation.util.util_tree_file_utils import UtilTreeFileUtils

class TreeNode(BaseModel):
    name: str
    type: str  # 'file' or 'directory'
    children: Optional[List['TreeNode']] = None
    size: Optional[int] = None
    mtime: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ('file', 'directory'):
            raise ValueError("type must be either 'file' or 'directory'")
        return v

    #
    # Note: Hash computation for TreeNode is provided by DI-compliant utilities (e.g., UtilTreeFileUtils).
    #       Do not use a property or method on the model for hashing; always use the injected utility.
    #       This ensures strict separation of concerns and testability.
    #

TreeNode.model_rebuild() 