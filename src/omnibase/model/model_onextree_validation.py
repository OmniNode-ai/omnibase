# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: model_onextree_validation.py
# version: 1.0.0
# uuid: f434d367-6c85-44ba-bf54-f816efe650f3
# author: OmniNode Team
# created_at: 2025-05-24T12:06:09.192184
# last_modified_at: 2025-05-24T16:13:11.907254
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 2ee91309274c3844ef55bf2196b99da0833800698251beeea7c9079606f09f62
# entrypoint: python@model_onextree_validation.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_onextree_validation
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
