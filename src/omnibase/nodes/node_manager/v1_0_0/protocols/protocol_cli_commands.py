"""
Protocol for CLI commands tool for node_manager node.
Defines the interface for CLI command operations and orchestration.
"""
from typing import Protocol

class ProtocolCliCommands(Protocol):
    """
    Protocol for CLI commands tool for node_manager node.
    Implementations should provide methods for running, parsing, and managing CLI commands.
    """
    def run_command(self, command: str, args: list) -> int:
        """
        Run a CLI command with the given arguments.
        Args:
            command (str): The command to run.
            args (list): List of arguments for the command.
        Returns:
            int: The exit code of the command.
        """
        ... 