# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.265467'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_reducer.py
# hash: ea2912510e6cbf2234550e68a70b3d3de25e951ed87a5775ccb03b490d280dd2
# last_modified_at: '2025-05-29T11:50:12.167898+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_reducer.py
# namespace: omnibase.protocol_reducer
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: d98cbd0f-43e9-455c-9706-a0b804aee580
# version: 1.0.0
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
