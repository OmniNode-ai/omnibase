from foundation.protocol.protocol_orchestrator import OrchestratorProtocol
from typing import Dict, Type, List

class OrchestratorRegistry:
    """
    Registry for all orchestrators implementing OrchestratorProtocol.
    Supports registration, lookup, and listing for orchestrator discovery and meta-orchestration.
    See: validator_refactor_checklist.yaml, validator_testing_standards.md
    """
    def __init__(self):
        self._registry: Dict[str, Type[OrchestratorProtocol]] = {}

    def register(self, name: str, orchestrator_cls: Type[OrchestratorProtocol]) -> None:
        self._registry[name] = orchestrator_cls

    def get(self, name: str) -> Type[OrchestratorProtocol]:
        return self._registry[name]

    def list(self) -> List[str]:
        return list(self._registry.keys()) 