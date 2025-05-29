# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.193906'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_tool.py
# hash: ad9a2e7d21c02876813c88f77154ff2afe44fcdcb7d52e01d23c2cb67f76a694
# last_modified_at: '2025-05-29T11:50:12.217701+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_tool.py
# namespace: omnibase.protocol_tool
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: e8651074-b687-485a-a38e-233f05375ce0
# version: 1.0.0
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
