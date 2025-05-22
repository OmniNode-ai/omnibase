# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_testable_cli.py
# version: 1.0.0
# uuid: 6ca4261b-b059-4cae-8d14-afeda0c87b04
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167827
# last_modified_at: 2025-05-21T16:42:46.047996
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 504c4bb78e4b7b8d6f0f3fe5405458683e14e699eee8bcb1191ec55c915126a6
# entrypoint: python@protocol_testable_cli.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_testable_cli
# meta_type: tool
# === /OmniNode:Metadata ===


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
