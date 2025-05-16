"""
ProtocolTestableCLI: Protocol for all testable CLI entrypoints. Requires main(argv) -> ModelResultCLI.
"""

from typing import List, Protocol

from omnibase.model.model_result_cli import ModelResultCLI


class ProtocolTestableCLI(Protocol):
    """
    Protocol for all testable CLI entrypoints. Requires main(argv) -> ModelResultCLI.

    Example:
        class MyTestableCLI(ProtocolTestableCLI):
            def main(self, argv: List[str]) -> ModelResultCLI:
                ...
    """

    def main(self, argv: List[str]) -> ModelResultCLI: ...
