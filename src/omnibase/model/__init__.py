# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.849824'
# description: Stamped by PythonHandler
# entrypoint: python://__init__.py
# hash: 9ca9c34ef6f6eea64196864a053d3c625a549b139bdfba513fc8884f6b15a99e
# last_modified_at: '2025-05-29T11:50:10.902414+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: __init__.py
# namespace: omnibase.init
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
