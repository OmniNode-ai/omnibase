# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.872639'
# description: Stamped by PythonHandler
# entrypoint: python://model_base_result.py
# hash: 74b818ddd12188fd215478b75ae954ba972dd771b7baad2213d7380db3b63c92
# last_modified_at: '2025-05-29T11:50:10.913680+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_base_result.py
# namespace: omnibase.model_base_result
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 78b1c43e-97d5-44da-a533-2e1a0f24a884
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from omnibase.model.model_base_error import BaseErrorModel


class BaseResultModel(BaseModel):
    exit_code: int
    success: bool
    errors: List[BaseErrorModel] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None  # Arbitrary metadata, extensible
