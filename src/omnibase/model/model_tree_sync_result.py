# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: e36f14d0-eee1-4102-be0b-0fdf23ce14e8
# name: model_tree_sync_result.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:52.302823
# last_modified_at: 2025-05-19T16:19:52.302824
# description: Stamped Python file: model_tree_sync_result.py
# state_contract: none
# lifecycle: active
# hash: 501ca9b41380d5e2a21cc533ec4331ba15e4b824620e2cb68eaafd2605d8954c
# entrypoint: {'type': 'python', 'target': 'model_tree_sync_result.py'}
# namespace: onex.stamped.model_tree_sync_result.py
# meta_type: tool
# === /OmniNode:Metadata ===

"""
Model for .tree and filesystem sync validation results.
"""

from enum import Enum
from pathlib import Path
from typing import List, Set

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

    extra_files_on_disk: Set[Path] = Field(
        default_factory=set, description="Files present on disk but not in .tree"
    )
    missing_files_in_tree: Set[Path] = Field(
        default_factory=set, description="Files listed in .tree but missing on disk"
    )
    status: TreeSyncStatusEnum = Field(
        ..., description="Sync status: ok, drift, or error"
    )
    messages: List[OnexMessageModel] = Field(
        default_factory=list, description="Validation messages and errors"
    )
