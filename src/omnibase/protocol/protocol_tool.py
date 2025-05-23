# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_tool.py
# version: 1.0.0
# uuid: 161eea24-6d9e-4967-9a63-a369930c81bc
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167962
# last_modified_at: 2025-05-21T16:42:46.038268
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 52fcfd6b7f91b09f6589eba12b4b47dfda9d2b0ee18523685bbaf51cabe8d1d4
# entrypoint: python@protocol_tool.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_tool
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
