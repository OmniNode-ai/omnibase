# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.975262'
# description: Stamped by PythonHandler
# entrypoint: python://model_naming_convention.py
# hash: f2658caa6422b04fe262125d19b10d225669f55c9f39608446317acb9b48ce05
# last_modified_at: '2025-05-29T11:50:10.975811+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_naming_convention.py
# namespace: omnibase.model_naming_convention
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: b3e9593b-73d2-4fa8-bd77-f8faf952fd07
# version: 1.0.0
# === /OmniNode:Metadata ===


from pydantic import BaseModel


class NamingConventionResultModel(BaseModel):
    valid: bool
    reason: str = ""
