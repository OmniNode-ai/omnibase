from typing import Protocol, Any

class ProcessRunnerProtocol(Protocol):
    """
    Protocol for subprocess execution abstraction in orchestrators.
    Enables DI, mocking, and testability for all external process calls.
    See: validator_refactor_checklist.yaml, validator_testing_standards.md
    """
    def run(self, command: list[str], **kwargs) -> Any:
        ... 