# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:25.711248'
# description: Stamped by PythonHandler
# entrypoint: python://model_onextree_validation.py
# hash: 9931cb7682944d075da0ab3844fe881d811729f39c00ccb9cdb235cacc63ae80
# last_modified_at: '2025-05-29T11:50:11.026644+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_onextree_validation.py
# namespace: omnibase.model_onextree_validation
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 5fedac0f-4389-45c5-9226-999b2ec93d79
# version: 1.0.0
# === /OmniNode:Metadata ===


from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ValidationStatusEnum(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class ValidationErrorCodeEnum(str, Enum):
    MISSING_FILE = "missing_file"
    EXTRA_FILE = "extra_file"
    TYPE_MISMATCH = "type_mismatch"
    STRUCTURE_MISMATCH = "structure_mismatch"
    UNKNOWN = "unknown"


class OnextreeValidationError(BaseModel):
    code: ValidationErrorCodeEnum
    message: str
    path: Optional[str] = None


class OnextreeValidationWarning(BaseModel):
    message: str
    path: Optional[str] = None


class OnextreeTreeNode(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

    name: str
    type: str  # "file" or "directory"
    children: Optional[List["OnextreeTreeNode"]] = None


# Use model_rebuild instead of update_forward_refs for Pydantic v2
OnextreeTreeNode.model_rebuild()


class OnextreeValidationResultModel(BaseModel):
    status: ValidationStatusEnum
    errors: List[OnextreeValidationError] = []
    warnings: List[OnextreeValidationWarning] = []
    summary: Optional[str] = None
    tree: Optional[OnextreeTreeNode] = None
