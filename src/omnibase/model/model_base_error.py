# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_base_error.py
# version: 1.0.0
# uuid: 0fce53b7-27a8-4cd5-b4f5-1f1a15f70d02
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.164632
# last_modified_at: 2025-05-21T16:42:46.075408
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: ed8695c68e8026708a3941d6371840412cdebaaea89d71cf51dc2c6039188dae
# entrypoint: {'type': 'python', 'target': 'model_base_error.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_base_error
# meta_type: tool
# === /OmniNode:Metadata ===

from pydantic import BaseModel


class BaseErrorModel(BaseModel):
    message: str
    code: str = "unknown"
    details: str = ""
