# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_event_bus.py
# version: 1.0.0
# uuid: 54146c1f-bcd2-41e4-b1db-3444ee92e9f3
# author: OmniNode Team
# created_at: 2025-05-22T17:18:16.710902
# last_modified_at: 2025-05-22T21:19:13.549105
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 8d512e335adda203c2fabea903b2c72cc3dddbbf7c5feaf20a689f24bf5ee471
# entrypoint: python@protocol_event_bus.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_event_bus
# meta_type: tool
# === /OmniNode:Metadata ===


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
