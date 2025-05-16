"""
ProtocolTestableRegistry: Protocol for all testable ONEX registry interfaces.
Extends ProtocolTestable. Used for registry-driven tests and swappable registry fixtures.
"""

from typing import Protocol, runtime_checkable

from omnibase.protocol.protocol_testable import ProtocolTestable


@runtime_checkable
class ProtocolTestableRegistry(ProtocolTestable, Protocol):
    """
    Protocol for testable ONEX registries (mock/real).
    Used for registry-driven tests and fixtures.
    """

    @classmethod
    def load_from_disk(cls) -> "ProtocolTestableRegistry": ...
    @classmethod
    def load_mock(cls) -> "ProtocolTestableRegistry": ...
    def get_node(self, node_id: str) -> dict: ...
