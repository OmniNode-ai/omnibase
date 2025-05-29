# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.336901'
# description: Stamped by PythonHandler
# entrypoint: python://event_bus_in_memory
# hash: 7e0863fd4dc8770deae28d74166370ef8631a63c3f81660f17dd75fe916f7840
# last_modified_at: '2025-05-29T14:14:00.410845+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: event_bus_in_memory.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: c0ff478c-011b-4afe-9595-ff748e5ede75
# version: 1.0.0
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
