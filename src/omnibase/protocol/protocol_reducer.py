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
