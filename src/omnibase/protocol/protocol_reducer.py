# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 55d70c54-f18e-419b-ad15-90b260aee820
# name: protocol_reducer.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:52.854303
# last_modified_at: 2025-05-19T16:19:52.854307
# description: Stamped Python file: protocol_reducer.py
# state_contract: none
# lifecycle: active
# hash: 9f04cd97868320ec529e73a207ad84c10b6ad8ce6099b1c9cdab6865b38b53e8
# entrypoint: {'type': 'python', 'target': 'protocol_reducer.py'}
# namespace: onex.stamped.protocol_reducer.py
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Protocol

from omnibase.model.model_reducer import ActionModel, StateModel


class ProtocolReducer(Protocol):
    """
    Protocol for ONEX reducers (state transition logic).

    Example:
        class MyReducer:
            def initial_state(self) -> StateModel:
                ...
            def dispatch(self, state: StateModel, action: ActionModel) -> StateModel:
                ...
    """

    def initial_state(self) -> StateModel: ...
    def dispatch(self, state: StateModel, action: ActionModel) -> StateModel: ...
