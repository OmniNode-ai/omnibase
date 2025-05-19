# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 8ef0a8a4-2501-45a2-bdfd-5de0759f8d72
# name: protocol_logger.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:55.108588
# last_modified_at: 2025-05-19T16:19:55.108592
# description: Stamped Python file: protocol_logger.py
# state_contract: none
# lifecycle: active
# hash: baac1b164f400790744c5a82db7173f1013f29da69a00b2e1e3eddf0132748aa
# entrypoint: {'type': 'python', 'target': 'protocol_logger.py'}
# namespace: onex.stamped.protocol_logger.py
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
