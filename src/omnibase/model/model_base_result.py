# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_base_result.py
# version: 1.0.0
# uuid: beba53da-d225-4a1b-a835-5efdb41e47ed
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.164707
# last_modified_at: 2025-05-21T16:42:46.065617
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 3b86954b70d8c0abe2947bce0ae9f5fbec0007797e35bff3a29b85ce99f4fd39
# entrypoint: {'type': 'python', 'target': 'model_base_result.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_base_result
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from omnibase.model.model_base_error import BaseErrorModel


class BaseResultModel(BaseModel):
    exit_code: int
    success: bool
    errors: List[BaseErrorModel] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None  # Arbitrary metadata, extensible
