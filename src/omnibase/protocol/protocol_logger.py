# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_logger.py
# version: 1.0.0
# uuid: de679165-4fb9-422e-8b85-35b30fab7495
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.202429
# last_modified_at: 2025-05-28T17:20:06.149643
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 655301220944c850c13a6f85938e8b3a9a4df366a05136d4adae9b6746c79dd2
# entrypoint: python@protocol_logger.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_logger
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
