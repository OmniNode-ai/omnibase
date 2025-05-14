from typing import Protocol, Any, runtime_checkable

@runtime_checkable
class OrchestratorProtocol(Protocol):
    """
    Protocol for all orchestrators (validate, tool, etc.) in the Foundation codebase.
    All orchestrators must implement this interface for registry, DI, and orchestrator standardization compliance.
    See: validator_refactor_checklist.yaml, validator_testing_standards.md
    """
    registry: Any
    di_container: Any
    logger: Any
    config: Any

    def run(self) -> Any:
        ...

    def parse_args(self, args: list[str] | None = None) -> Any:
        ...

    def discover_targets(self) -> Any:
        ...

    def execute_actions(self) -> Any:
        ...

    def summarize_results(self) -> Any:
        ... 