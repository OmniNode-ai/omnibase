# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_tree_sync_result.py
# version: 1.0.0
# uuid: 242eb533-be65-4cf6-bd60-4d57e22db138
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.166536
# last_modified_at: 2025-05-21T16:42:46.087450
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 02057896250b13102c904c6030ebcb8e5a3723d8a3866172db75e64d27452226
# entrypoint: python@model_tree_sync_result.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_tree_sync_result
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
