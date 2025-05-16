# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: protocol_logger
# namespace: foundation.protocol
# version: 0.1.0
# author: AI-Dev Migration
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-06-28
# last_modified_at: 2025-06-28
# entrypoint: protocol_logger.py
# protocols_supported: ["O.N.E. v0.1"]
# interface_type: Protocol
# interface_name: Logger
# mock_safe: true
# rationale: Provides a swappable, testable logging interface for use throughout the codebase. Enables DI and future structlog integration.
# === /OmniNode:Tool_Metadata ===

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
