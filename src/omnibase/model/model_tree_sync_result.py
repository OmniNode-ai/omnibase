"""
Model for .tree and filesystem sync validation results.
"""
from pathlib import Path
from typing import Set, List
from enum import Enum
from pydantic import BaseModel, Field
from omnibase.model.model_onex_message_result import OnexMessageModel

class TreeSyncStatusEnum(str, Enum):
    OK = "ok"
    DRIFT = "drift"
    ERROR = "error"

class TreeSyncResultModel(BaseModel):
    """
    Result model for validating .tree and filesystem sync.
    """
    extra_files_on_disk: Set[Path] = Field(default_factory=set, description="Files present on disk but not in .tree")
    missing_files_in_tree: Set[Path] = Field(default_factory=set, description="Files listed in .tree but missing on disk")
    status: TreeSyncStatusEnum = Field(..., description="Sync status: ok, drift, or error")
    messages: List[OnexMessageModel] = Field(default_factory=list, description="Validation messages and errors") 