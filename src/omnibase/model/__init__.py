# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:07.849824'
# description: Stamped by PythonHandler
# entrypoint: python://__init__
# hash: 4d598ad148ef850421a43c4acc573cf86e767379b0cc71918fe69a73b729ccd6
# last_modified_at: '2025-05-29T14:13:58.726636+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: __init__.py
# namespace: python://omnibase.model.__init__
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 5ef4541a-532c-4bc5-b738-d5264b55c571
# version: 1.0.0
# === /OmniNode:Metadata ===


from .model_metadata import MetadataBlockModel
from .model_onex_message_result import (
    OnexBatchResultModel,
    OnexMessageModel,
    OnexResultModel,
    UnifiedRunMetadataModel,
    UnifiedSummaryModel,
    UnifiedVersionModel,
)
from .model_result_cli import CLIOutputModel, ModelResultCLI
from .model_validate_error import (
    ValidateMessageModel,
    ValidateResultModel,
    insert_template_marker,
)

__all__ = [
    "MetadataBlockModel",
    "ModelResultCLI",
    "CLIOutputModel",
    "OnexMessageModel",
    "OnexResultModel",
    "UnifiedSummaryModel",
    "UnifiedVersionModel",
    "UnifiedRunMetadataModel",
    "OnexBatchResultModel",
    "ValidateMessageModel",
    "ValidateResultModel",
    "insert_template_marker",
    # "OnexStatus",  # Moved to avoid circular dependency
]
