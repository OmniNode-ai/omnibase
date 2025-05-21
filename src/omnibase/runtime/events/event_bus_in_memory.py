import logging
from typing import Callable, Set

from omnibase.model.model_onex_event import OnexEvent
from omnibase.runtime.protocol.protocol_event_bus import ProtocolEventBus

logger = logging.getLogger(__name__)


class InMemoryEventBus(ProtocolEventBus):
    """
    Canonical in-memory implementation of ProtocolEventBus for ONEX.
    Supports synchronous publish/subscribe for local event emission and testing.
    """

    def __init__(self) -> None:
        self._subscribers: Set[Callable[[OnexEvent], None]] = set()

    def publish(self, event: OnexEvent) -> None:
        logger.debug(f"Publishing event: {event}")
        for callback in self._subscribers.copy():
            try:
                callback(event)
            except Exception as exc:
                logger.exception(f"EventBus subscriber error: {exc}")

    def subscribe(self, callback: Callable[[OnexEvent], None]) -> None:
        logger.debug(f"Subscribing callback: {callback}")
        self._subscribers.add(callback)

    def unsubscribe(self, callback: Callable[[OnexEvent], None]) -> None:
        logger.debug(f"Unsubscribing callback: {callback}")
        self._subscribers.discard(callback)

    def clear(self) -> None:
        logger.debug("Clearing all subscribers")
        self._subscribers.clear()
