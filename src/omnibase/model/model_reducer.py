# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: e8a6cfd2-1fd8-4ff7-b527-f0f268df1201
# name: model_reducer.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:53.095928
# last_modified_at: 2025-05-19T16:19:53.095932
# description: Stamped Python file: model_reducer.py
# state_contract: none
# lifecycle: active
# hash: fdf974eff08b498b095b8c0af43f6fd3d719079db54a30caf118574ad21bee31
# entrypoint: {'type': 'python', 'target': 'model_reducer.py'}
# namespace: onex.stamped.model_reducer.py
# meta_type: tool
# === /OmniNode:Metadata ===

from pydantic import BaseModel


class StateModel(BaseModel):
    # Placeholder for ONEX state fields
    pass


class ActionModel(BaseModel):
    # Placeholder for ONEX action fields
    pass
