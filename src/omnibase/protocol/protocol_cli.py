# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 5b5e477e-3916-453e-af54-eba7b4dc5c6d
# name: protocol_cli.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:05.143255
# last_modified_at: 2025-05-19T16:20:05.143257
# description: Stamped Python file: protocol_cli.py
# state_contract: none
# lifecycle: active
# hash: 4892c2fed0c72b5c47a7dbb542c264a0444235dc10619fde70b139ffe18cf89b
# entrypoint: {'type': 'python', 'target': 'protocol_cli.py'}
# namespace: onex.stamped.protocol_cli.py
# meta_type: tool
# === /OmniNode:Metadata ===

import argparse
from typing import Any, List, Optional, Protocol

from omnibase.model.model_result_cli import ModelResultCLI


class ProtocolCLI(Protocol):
    """
    Protocol for all CLI entrypoints. Provides shared CLI logic: argument parsing, logging setup, exit codes, metadata enforcement.
    Does NOT handle --apply or dry-run; those are handled in subclasses/protocols.

    Example:
        class MyCLI(ProtocolCLI):
            def get_parser(self) -> argparse.ArgumentParser:
                ...
            def main(self, argv: Optional[List[str]] = None) -> ModelResultCLI:
                ...
            def run(self, args: List[str]) -> ModelResultCLI:
                ...
            def describe_flags(self, format: str = "json") -> Any:
                ...
    """

    description: str
    logger: Any

    def get_parser(self) -> argparse.ArgumentParser: ...
    def main(self, argv: Optional[List[str]] = None) -> ModelResultCLI: ...
    def run(self, args: List[str]) -> ModelResultCLI: ...

    def describe_flags(self, format: str = "json") -> Any:
        """
        Return a structured description of all CLI flags (name, type, default, help, etc.).
        Args:
            format: Output format ('json' or 'yaml').
        Returns:
            List[dict] or dict describing all CLI flags and their metadata.
        """
        ...
