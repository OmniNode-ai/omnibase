# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_logger.py
# version: 1.0.0
# uuid: cb81d2f3-59c0-45f6-a1f3-dabf8cfa5c0b
# author: OmniNode Team
# created_at: 2025-05-21T13:18:56.569133
# last_modified_at: 2025-05-22T20:50:39.728708
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 6d9262a1a3445a95bcb7972094089f4230500cf62bedd3484eac457ee9f8b69a
# entrypoint: python@protocol_logger.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_logger
# meta_type: tool
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
