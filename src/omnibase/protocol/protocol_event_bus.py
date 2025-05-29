# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.128231'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_event_bus.py
# hash: 32b855279d7c32f9a2fe42d012ab59d7c4ab6a04e41406a764cbdad533540035
# last_modified_at: '2025-05-29T11:50:12.088295+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_event_bus.py
# namespace: omnibase.protocol_event_bus
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 2d9c79c5-6422-462b-b10c-e080a10c1d42
# version: 1.0.0
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
