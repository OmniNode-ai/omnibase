# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.122722'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_cli.py
# hash: 59556a4635f3dea11a4acb4c21484a203d8628093781c6c739a8a5ddec8bdfcb
# last_modified_at: '2025-05-29T11:50:12.076577+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_cli.py
# namespace: omnibase.protocol_cli
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: c1263cdb-9416-4a80-9e34-e7082521932b
# version: 1.0.0
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
