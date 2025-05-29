# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.895826'
# description: Stamped by PythonHandler
# entrypoint: python://model_context.py
# hash: 0234d1503fc13da3f976eb5b5b6b3703c801655628b39a03fa683e8c6acad922
# last_modified_at: '2025-05-29T11:50:10.925057+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_context.py
# namespace: omnibase.model_context
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 05a4c4aa-084e-4619-9048-18161ea7cd48
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Dict

from pydantic import BaseModel, Field


class ContextModel(BaseModel):
    data: Dict[str, str] = Field(default_factory=dict)
