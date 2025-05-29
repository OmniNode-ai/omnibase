# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.202429'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_logger.py
# hash: b75d2cac84379b40b277f6f2cfca3391a2e8ba0a9c081d4464302f6c2adf6241
# last_modified_at: '2025-05-29T11:50:12.129052+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_logger.py
# namespace: omnibase.protocol_logger
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: de679165-4fb9-422e-8b85-35b30fab7495
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Protocol

from omnibase.model.model_log_entry import LogEntryModel


class ProtocolLogger(Protocol):
    """
    Protocol for ONEX logging interfaces.

    Example:
        class MyLogger:
            def log(self, entry: LogEntryModel) -> None:
                ...
    """

    def log(self, entry: LogEntryModel) -> None: ...
