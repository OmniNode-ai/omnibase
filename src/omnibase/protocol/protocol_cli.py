from typing import List, Optional, Protocol, Any
import argparse

class ProtocolCLI(Protocol):
    """
    Protocol for all CLI entrypoints. Provides shared CLI logic: argument parsing, logging setup, exit codes, metadata enforcement.
    Does NOT handle --apply or dry-run; those are handled in subclasses/protocols.
    """
    description: str
    logger: Any

    def get_parser(self) -> argparse.ArgumentParser: ...
    def main(self, argv: Optional[List[str]] = None) -> int: ...
    def run(self, args) -> int: ...

    def describe_flags(self, format: str = "json") -> Any:
        """
        Return a structured description of all CLI flags (name, type, default, help, etc.).
        Args:
            format: Output format ('json' or 'yaml').
        Returns:
            List[dict] or dict describing all CLI flags and their metadata.
        """
        ...
