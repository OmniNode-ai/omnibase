from typing import List, Optional, Protocol, Any, Tuple
import argparse
from foundation.protocol.protocol_cli import ProtocolCLI

class ProtocolTreeCLI(ProtocolCLI, Protocol):
    """
    Protocol for tree-related CLI tools. Extends ProtocolCLI to provide dual root argument parsing:
    - Accepts both a positional root argument and an optional --root argument.
    - If both are provided, --root takes precedence.
    - Provides a helper method to resolve the root directory and return parsed args.
    """
    def parse_tree_cli_args(self, argv: Optional[List[str]] = None) -> Tuple[str, argparse.Namespace]:
        """
        Parse CLI arguments for tree tools, supporting both positional and --root arguments.
        Returns:
            root_dir: The resolved root directory (str)
            args: The parsed argparse.Namespace
        Raises:
            SystemExit if neither argument is provided.
        """
        ... 