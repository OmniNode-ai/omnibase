# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 18ec992b-c7db-4c18-bdc7-33b60c9a3989
# name: protocol_orchestrator.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:57.200856
# last_modified_at: 2025-05-19T16:19:57.200858
# description: Stamped Python file: protocol_orchestrator.py
# state_contract: none
# lifecycle: active
# hash: 3f98aa9c78ea19272c88e52e8e7af2859066fee95ca3bb1ed972baddc3252b48
# entrypoint: {'type': 'python', 'target': 'protocol_orchestrator.py'}
# namespace: onex.stamped.protocol_orchestrator.py
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
