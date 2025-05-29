# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.861191'
# description: Stamped by PythonHandler
# entrypoint: python://model_base_error.py
# hash: e313674baa9907fea7a12dfe96dea67fc990b5e59535a80aa7aa5e82f26457fc
# last_modified_at: '2025-05-29T11:50:10.907999+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_base_error.py
# namespace: omnibase.model_base_error
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 5e943eab-c472-4cbf-a60b-d241b744b017
# version: 1.0.0
# === /OmniNode:Metadata ===


from pydantic import BaseModel


class BaseErrorModel(BaseModel):
    message: str
    code: str = "unknown"
    details: str = ""
