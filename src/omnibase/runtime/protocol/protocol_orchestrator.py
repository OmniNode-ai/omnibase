# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_orchestrator.py
# version: 1.0.0
# uuid: 'b55c40c5-3f72-4396-8019-d96f4d382e95'
# author: OmniNode Team
# created_at: '2025-05-21T13:18:56.569386'
# last_modified_at: '2025-05-22T18:05:26.863502'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: protocol_orchestrator.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_orchestrator
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


from typing import List, Protocol

from omnibase.model.model_orchestrator import (
    GraphModel,
    OrchestratorResultModel,
    PlanModel,
)


class ProtocolOrchestrator(Protocol):
    """
    Protocol for ONEX orchestrator components (workflow/graph execution).

    Example:
        class MyOrchestrator:
            def plan(self, graph: GraphModel) -> List[PlanModel]:
                ...
            def execute(self, plan: List[PlanModel]) -> OrchestratorResultModel:
                ...
    """

    def plan(self, graph: GraphModel) -> List[PlanModel]: ...
    def execute(self, plan: List[PlanModel]) -> OrchestratorResultModel: ...
