# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: interface_logger_abc
# namespace: foundation.interface
# version: 0.1.0
# author: Foundation Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-29
# last_modified_at: 2025-04-29
# entrypoint: interface_logger_abc.py
# protocols_supported: ["O.N.E. v0.1"]
# interface_type: ABC
# interface_name: ILogger
# mock_safe: false
# === /OmniNode:Tool_Metadata ===

from abc import ABC, abstractmethod


class ILogger(ABC):
    """Interface for logging implementations."""

    @abstractmethod
    def log(self, message: str) -> None:
        """Log a message."""
        pass
