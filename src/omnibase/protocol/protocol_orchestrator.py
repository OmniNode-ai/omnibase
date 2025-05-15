from typing import Protocol, List
from src.omnibase.model.model_orchestrator import GraphModel, PlanModel, OrchestratorResultModel

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
    def plan(self, graph: GraphModel) -> List[PlanModel]:
        ...
    def execute(self, plan: List[PlanModel]) -> OrchestratorResultModel:
        ... 