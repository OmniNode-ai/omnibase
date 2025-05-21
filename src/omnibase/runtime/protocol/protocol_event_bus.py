from typing import Callable, Protocol

from omnibase.model.model_onex_event import OnexEvent


class ProtocolEventBus(Protocol):
    """
    Canonical protocol for ONEX event bus (runtime/ placement).
    Defines publish/subscribe interface for event emission and handling.
    All event bus implementations must conform to this interface.
    Follows the Protocol<Name> naming convention for consistency.
    Optionally supports clear() for test/lifecycle management.
    """

    def publish(self, event: OnexEvent) -> None:
        """
        Publish an event to the bus.
        Args:
            event: OnexEvent to emit
        """
        ...

    def subscribe(self, callback: Callable[[OnexEvent], None]) -> None:
        """
        Subscribe a callback to receive events.
        Args:
            callback: Callable invoked with each OnexEvent
        """
        ...

    def unsubscribe(self, callback: Callable[[OnexEvent], None]) -> None:
        """
        Unsubscribe a previously registered callback.
        Args:
            callback: Callable to remove
        """
        ...

    def clear(self) -> None:
        """
        Remove all subscribers from the event bus. Optional, for test/lifecycle management.
        """
        ...
