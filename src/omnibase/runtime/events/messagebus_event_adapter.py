from typing import Callable

from omnibase.model.model_onex_event import OnexEvent
from omnibase.runtime.protocol.protocol_event_bus import ProtocolEventBus


class MessageBusEventAdapter(ProtocolEventBus):
    """
    Stub implementation of ProtocolEventBus for forwarding events to a message bus.
    Canonical runtime/ placement. To be implemented for real message bus integration.
    """

    def publish(self, event: OnexEvent) -> None:
        """TODO: Forward event to message bus (not yet implemented)."""
        pass

    def subscribe(self, callback: Callable[[OnexEvent], None]) -> None:
        """TODO: Register callback for message bus events (not yet implemented)."""
        pass

    def unsubscribe(self, callback: Callable[[OnexEvent], None]) -> None:
        """TODO: Unregister callback (not yet implemented)."""
        pass

    def clear(self) -> None:
        """TODO: Clear all subscribers (not yet implemented)."""
        pass
