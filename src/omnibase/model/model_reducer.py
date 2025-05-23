# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_reducer.py
# version: 1.0.0
# uuid: b79a6ac1-6e7e-4bf7-814c-9ca4d988f573
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.166331
# last_modified_at: 2025-05-21T16:42:46.110831
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 422f287074a74d135acadf5a12645580a9c9b56a55abecbd9796d4f5ede97767
# entrypoint: python@model_reducer.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_reducer
# meta_type: tool
# === /OmniNode:Metadata ===


from pydantic import BaseModel


class StateModel(BaseModel):
    # Placeholder for ONEX state fields
    pass


class ActionModel(BaseModel):
    # Placeholder for ONEX action fields
    pass
