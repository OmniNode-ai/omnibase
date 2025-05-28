# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_orchestrator.py
# version: 1.0.0
# uuid: 4ea8f61f-93a5-4e91-91ad-75b22a6b4060
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.245096
# last_modified_at: 2025-05-28T17:20:04.451956
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: b22189cb4ab65fead7943f3ec545bb56163e3455528ae207ae3045fad2d5a3c4
# entrypoint: python@protocol_orchestrator.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_orchestrator
# meta_type: tool
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
