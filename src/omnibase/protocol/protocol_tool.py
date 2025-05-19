# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 508d690c-fb52-48b6-bbbd-a21f12145350
# name: protocol_tool.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:54.480372
# last_modified_at: 2025-05-19T16:19:54.480376
# description: Stamped Python file: protocol_tool.py
# state_contract: none
# lifecycle: active
# hash: f662ce47042a2439081d549c493aeb0ce55f811471812074e4dcc4546e81bd34
# entrypoint: {'type': 'python', 'target': 'protocol_tool.py'}
# namespace: onex.stamped.protocol_tool.py
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Any, Dict, Protocol

from omnibase.model.model_result_cli import ModelResultCLI
from omnibase.protocol.protocol_cli import ProtocolCLI


class ProtocolTool(ProtocolCLI, Protocol):
    """
    Protocol for CLI scripts that can modify files. Adds --apply flag, defaults to dry-run, and enforces safety messaging.
    All file-modifying logic must be gated behind --apply. Dry-run is always the default.

    Example:
        class MyTool(ProtocolTool):
            def dry_run_main(self, args) -> ModelResultCLI:
                ...
            def apply_main(self, args) -> ModelResultCLI:
                ...
            def execute(self, input_data: dict) -> ModelResultCLI:
                ...
    """

    def dry_run_main(self, args: Any) -> ModelResultCLI: ...
    def apply_main(self, args: Any) -> ModelResultCLI: ...

    def execute(self, input_data: Dict[str, Any]) -> ModelResultCLI: ...
