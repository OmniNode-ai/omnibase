# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.047863'
# description: Stamped by PythonHandler
# entrypoint: python://model_reducer.py
# hash: f48949ecb740145a1c0255f20e3576eea9758656699942b706c5e9ae8f731734
# last_modified_at: '2025-05-29T11:50:11.054779+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_reducer.py
# namespace: omnibase.model_reducer
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: bad313b8-30cb-45ad-9141-ea8d43fe0a91
# version: 1.0.0
# === /OmniNode:Metadata ===


from pydantic import BaseModel


class StateModel(BaseModel):
    # Placeholder for ONEX state fields
    pass


class ActionModel(BaseModel):
    # Placeholder for ONEX action fields
    pass
