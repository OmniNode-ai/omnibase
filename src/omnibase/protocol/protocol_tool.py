from typing import Protocol

from omnibase.model.model_result_cli import ModelResultCLI
from omnibase.protocol.protocol_cli import ProtocolCLI


class ProtocolTool(ProtocolCLI, Protocol):
    """
    Protocol for CLI scripts that can modify files. Adds --apply flag, defaults to dry-run, and enforces safety messaging.
    All file-modifying logic must be gated behind --apply. Dry-run is always the default.

    Example:
        class MyTool(ProtocolTool):
            def dry_run_main(self, args) -> ModelResultCLI:
                ...
            def apply_main(self, args) -> ModelResultCLI:
                ...
            def execute(self, input_data: dict) -> ModelResultCLI:
                ...
    """

    def dry_run_main(self, args) -> ModelResultCLI: ...
    def apply_main(self, args) -> ModelResultCLI: ...

    def execute(self, input_data: dict) -> ModelResultCLI: ...
