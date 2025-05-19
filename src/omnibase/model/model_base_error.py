# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 6e23a551-7ed7-4139-8670-3d90c389905b
# name: model_base_error.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:56.174721
# last_modified_at: 2025-05-19T16:19:56.174723
# description: Stamped Python file: model_base_error.py
# state_contract: none
# lifecycle: active
# hash: 860601f3b2067f91776176738b05061a2bff5727104a4fe518f25f225fb44a59
# entrypoint: {'type': 'python', 'target': 'model_base_error.py'}
# namespace: onex.stamped.model_base_error.py
# meta_type: tool
# === /OmniNode:Metadata ===

from pydantic import BaseModel


class BaseErrorModel(BaseModel):
    message: str
    code: str = "unknown"
    details: str = ""
