# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 6667709d-fde7-4845-8996-630b23b52d16
# name: model_naming_convention.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:54.619248
# last_modified_at: 2025-05-19T16:19:54.619250
# description: Stamped Python file: model_naming_convention.py
# state_contract: none
# lifecycle: active
# hash: b2f569dc6848e43d5207fdd8f54941406add4d5f90a1d7bc6f6caed946632398
# entrypoint: {'type': 'python', 'target': 'model_naming_convention.py'}
# namespace: onex.stamped.model_naming_convention.py
# meta_type: tool
# === /OmniNode:Metadata ===

from pydantic import BaseModel


class NamingConventionResultModel(BaseModel):
    valid: bool
    reason: str = ""
