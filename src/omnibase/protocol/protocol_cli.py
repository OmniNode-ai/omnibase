# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_cli.py
# version: 1.0.0
# uuid: 96e6f4c3-0456-4deb-9249-69937d2a666e
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.166865
# last_modified_at: 2025-05-21T16:42:46.104775
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 94d2eb2e43df515d8802f3c60c5c6c4b5e777fa38b654c66c985f85d20fb27d7
# entrypoint: python@protocol_cli.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_cli
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
