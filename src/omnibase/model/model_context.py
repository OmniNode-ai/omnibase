# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_context.py
# version: 1.0.0
# uuid: 91cb085f-e665-4b96-abae-7e8e5016318c
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.164850
# last_modified_at: 2025-05-21T16:42:46.041808
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 6ceda7cc78bb6c49bdfeb0dd3c9bec0a8279ce6c4382207f827d98624c3c4d23
# entrypoint: python@model_context.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_context
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Dict

from pydantic import BaseModel, Field


class ContextModel(BaseModel):
    data: Dict[str, str] = Field(default_factory=dict)
