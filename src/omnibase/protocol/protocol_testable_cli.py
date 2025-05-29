# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.174119'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_testable_cli.py
# hash: 27e3cb4642947f1ee893a165a4a3b1145150966bac13b7b9ba2a6d8dfe05cfad
# last_modified_at: '2025-05-29T11:50:12.201569+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_testable_cli.py
# namespace: omnibase.protocol_testable_cli
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 890bf413-c5aa-4a85-89b2-3a53892d7830
# version: 1.0.0
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
