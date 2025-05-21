# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_reducer.py
# version: 1.0.0
# uuid: a8b41be8-634f-4d98-a6fb-73c84961c37c
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167443
# last_modified_at: 2025-05-21T16:42:46.130320
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: ba6bbd27a73e7df73d36acff6dd8f536328c808946fa7de5726d01b4900ab546
# entrypoint: {'type': 'python', 'target': 'protocol_reducer.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_reducer
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
