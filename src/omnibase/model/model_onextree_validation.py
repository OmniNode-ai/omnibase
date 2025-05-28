# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: model_onextree_validation.py
# version: 1.0.0
# uuid: 5fedac0f-4389-45c5-9226-999b2ec93d79
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.711248
# last_modified_at: 2025-05-28T17:20:03.869291
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: d4271103433d2a806823745420113cf5f58f3bf8cbdc7d0d9270df3a33aeb23d
# entrypoint: python@model_onextree_validation.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.model_onextree_validation
# meta_type: tool
# === /OmniNode:Metadata ===


from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ValidationStatusEnum(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"


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
