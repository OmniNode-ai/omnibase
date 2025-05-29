# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.245096'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_orchestrator.py
# hash: 34f1128ac5ce16c48cfa4485db10d729d219c67556e20829e274a51644975587
# last_modified_at: '2025-05-29T11:50:12.157079+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_orchestrator.py
# namespace: omnibase.protocol_orchestrator
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 4ea8f61f-93a5-4e91-91ad-75b22a6b4060
# version: 1.0.0
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
