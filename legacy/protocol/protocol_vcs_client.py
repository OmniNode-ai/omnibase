from typing import Protocol, Any

class VCSClientProtocol(Protocol):
    """
    Protocol for VCS (e.g., git) abstraction in orchestrators.
    Enables DI, mocking, and testability for all VCS operations.
    See: validator_refactor_checklist.yaml, validator_testing_standards.md
    """
    def add(self, path: str) -> Any:
        ...

    def commit(self, message: str) -> Any:
        ...

    def status(self) -> Any:
        ... 