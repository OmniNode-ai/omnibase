# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_orchestrator.py
# version: 1.0.0
# uuid: c54a1d4b-eb31-4b06-be79-3a828100e62f
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167326
# last_modified_at: 2025-05-21T16:42:46.064970
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 35052a820508c7abffe03485081e0d79e32e0af804fed131ef8ab670421ae959
# entrypoint: {'type': 'python', 'target': 'protocol_orchestrator.py'}
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
