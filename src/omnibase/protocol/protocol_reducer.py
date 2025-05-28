# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_reducer.py
# version: 1.0.0
# uuid: d98cbd0f-43e9-455c-9706-a0b804aee580
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.265467
# last_modified_at: 2025-05-28T17:20:04.613395
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: cc2558fd0ec009bad44adb4f99250bd613ce2c7e8a4a546f8da49a4b0b30cfa6
# entrypoint: python@protocol_reducer.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_reducer
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
