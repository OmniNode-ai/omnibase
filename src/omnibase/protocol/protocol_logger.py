# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.202429'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_logger
# hash: acdddae45e452c0a6de44fa250471b51ec1c8edbff4041180129a32392324405
# last_modified_at: '2025-05-29T14:14:00.269378+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_logger.py
# namespace: python://omnibase.protocol.protocol_logger
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
