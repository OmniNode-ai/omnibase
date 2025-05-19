# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 4f00dac4-b5d2-44fa-b396-40f10bdbea23
# name: model_context.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:04.357397
# last_modified_at: 2025-05-19T16:20:04.357406
# description: Stamped Python file: model_context.py
# state_contract: none
# lifecycle: active
# hash: b044b0859c9679421716f4db622a353fd6c92ac2e5fbe624ce40c97c91c377cd
# entrypoint: {'type': 'python', 'target': 'model_context.py'}
# namespace: onex.stamped.model_context.py
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Dict

from pydantic import BaseModel, Field


class ContextModel(BaseModel):
    data: Dict[str, str] = Field(default_factory=dict)
