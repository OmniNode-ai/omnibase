# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.079159'
# description: Stamped by PythonHandler
# entrypoint: python://model_tree_sync_result.py
# hash: 8e588f522d8ef5867c07a81203ee4f31170fc61e61f083b85eccda1aab6f795c
# last_modified_at: '2025-05-29T11:50:11.076912+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_tree_sync_result.py
# namespace: omnibase.model_tree_sync_result
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: f8e726da-f556-48ef-8b60-37be6cf292ee
# version: 1.0.0
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
