# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_naming_convention.py
# version: 1.0.0
# uuid: 19a4aaec-5b65-4f2e-9ad2-0d2bc398d34a
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165844
# last_modified_at: 2025-05-21T16:42:46.079082
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 82f8f7cbaacc24e5c34e56318aa914407931922e22d9341778ac252de62b15b3
# entrypoint: {'type': 'python', 'target': 'model_naming_convention.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_naming_convention
# meta_type: tool
# === /OmniNode:Metadata ===

from pydantic import BaseModel


class NamingConventionResultModel(BaseModel):
    valid: bool
    reason: str = ""
