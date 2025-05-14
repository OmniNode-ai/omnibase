from typing import Protocol
from foundation.protocol.protocol_cli import ProtocolCLI

class ProtocolTool(ProtocolCLI, Protocol):
    """
    Protocol for CLI scripts that can modify files. Adds --apply flag, defaults to dry-run, and enforces safety messaging.
    All file-modifying logic must be gated behind --apply. Dry-run is always the default.
    """
    def dry_run_main(self, args) -> int: ...
    def apply_main(self, args) -> int: ...
