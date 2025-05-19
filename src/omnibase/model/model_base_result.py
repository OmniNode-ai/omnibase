# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 0134ecb7-83dd-4b8b-b62d-b904059c5e05
# name: model_base_result.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:52.037366
# last_modified_at: 2025-05-19T16:19:52.037368
# description: Stamped Python file: model_base_result.py
# state_contract: none
# lifecycle: active
# hash: bf8c545842d554fbb5ea9ac6608fb4b7e0c93337ae0fc6eba80934a1326086ff
# entrypoint: {'type': 'python', 'target': 'model_base_result.py'}
# namespace: onex.stamped.model_base_result.py
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
