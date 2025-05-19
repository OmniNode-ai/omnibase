# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 8b468cb8-a360-4e8f-81f6-769eec182ae8
# name: protocol_testable_cli.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:52.884088
# last_modified_at: 2025-05-19T16:19:52.884092
# description: Stamped Python file: protocol_testable_cli.py
# state_contract: none
# lifecycle: active
# hash: aef724856a30cc331d167eaa1a287e8135ef7ec5c687f1a120e8a12921ce8dd9
# entrypoint: {'type': 'python', 'target': 'protocol_testable_cli.py'}
# namespace: onex.stamped.protocol_testable_cli.py
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
