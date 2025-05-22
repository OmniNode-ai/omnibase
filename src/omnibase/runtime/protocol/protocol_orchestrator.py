# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_orchestrator.py
# version: 1.0.0
# uuid: b55c40c5-3f72-4396-8019-d96f4d382e95
# author: OmniNode Team
# created_at: 2025-05-21T13:18:56.569386
# last_modified_at: 2025-05-22T20:50:39.718981
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 8476713a478237dc08e627634700997f42174b5c6213480c5f71556cd1de1e55
# entrypoint: python@protocol_orchestrator.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_orchestrator
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
