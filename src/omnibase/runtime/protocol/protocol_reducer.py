# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_reducer.py
# version: 1.0.0
# uuid: '4d0e426d-a345-4f64-ac81-592812f6bf78'
# author: OmniNode Team
# created_at: '2025-05-21T13:18:56.569686'
# last_modified_at: '2025-05-22T18:05:26.860902'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: protocol_reducer.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_reducer
# meta_type: tool
# trust_score: null
# tags: null
# capabilities: null
# protocols_supported: null
# base_class: null
# dependencies: null
# inputs: null
# outputs: null
# environment: null
# license: null
# signature_block: null
# x_extensions: {}
# testing: null
# os_requirements: null
# architectures: null
# container_image_reference: null
# compliance_profiles: []
# data_handling_declaration: null
# logging_config: null
# source_repository: null
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
