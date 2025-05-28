# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: event_bus_in_memory.py
# version: 1.0.0
# uuid: c0ff478c-011b-4afe-9595-ff748e5ede75
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.336901
# last_modified_at: 2025-05-28T17:20:04.798153
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: e9875bbd489545fac9c2828dc1772ee577b9fe27bfce6922d3e3deaeb61b51c6
# entrypoint: python@event_bus_in_memory.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.event_bus_in_memory
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Callable, Set

from omnibase.model.model_onex_event import OnexEvent
from omnibase.protocol.protocol_event_bus import ProtocolEventBus


class InMemoryEventBus(ProtocolEventBus):
    """
    Canonical in-memory implementation of ProtocolEventBus for ONEX.
    Supports synchronous publish/subscribe for local event emission and testing.
    """

    def __init__(self) -> None:
        self._subscribers: Set[Callable[[OnexEvent], None]] = set()

    def publish(self, event: OnexEvent) -> None:
        # Note: No logging here to avoid circular dependencies during structured logging setup
        for callback in self._subscribers.copy():
            try:
                callback(event)
            except Exception:
                # Note: No logging here to avoid circular dependencies during structured logging setup
                pass

    def subscribe(self, callback: Callable[[OnexEvent], None]) -> None:
        # Note: No logging here to avoid circular dependencies during structured logging setup
        self._subscribers.add(callback)

    def unsubscribe(self, callback: Callable[[OnexEvent], None]) -> None:
        # Note: No logging here to avoid circular dependencies during structured logging setup
        self._subscribers.discard(callback)

    def clear(self) -> None:
        # Note: No logging here to avoid circular dependencies during structured logging setup
        self._subscribers.clear()
