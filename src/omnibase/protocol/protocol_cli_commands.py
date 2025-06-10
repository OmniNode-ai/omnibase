"""
Protocol for CLI commands tool (shared).
Defines the interface for CLI command operations and orchestration.
"""
from typing import Protocol, List

class ProtocolCliCommands(Protocol):
    """
    Protocol for CLI commands tool (shared).
    Implementations should provide methods for running, parsing, and managing CLI commands.
    """
    def run_command(self, command: str, args: List[str]) -> int:
        """
        Run a CLI command with the given arguments.
        Args:
            command (str): The command to run.
            args (List[str]): List of arguments for the command.
        Returns:
            int: The exit code of the command.
        """
        ... 