# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_logger.py
# version: 1.0.0
# uuid: 7b8980fb-af23-4105-81e0-f252d015cca8
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167198
# last_modified_at: 2025-05-21T16:42:46.141400
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: cf87165fd1b6a307284b37eb582988b02f6fbd15d8eec01e0b852a784900dfa9
# entrypoint: {'type': 'python', 'target': 'protocol_logger.py'}
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
