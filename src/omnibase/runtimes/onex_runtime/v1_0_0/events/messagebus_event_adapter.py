# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.346017'
# description: Stamped by PythonHandler
# entrypoint: python://messagebus_event_adapter.py
# hash: 5dcc70016d37afe82a1ef9e4708c533451763ce706cd93e1a8bcdfb901e6fe02
# last_modified_at: '2025-05-29T11:50:12.246395+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: messagebus_event_adapter.py
# namespace: omnibase.messagebus_event_adapter
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 113bbe6e-9575-4a4f-ade5-ce15edda783d
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Callable

from omnibase.model.model_onex_event import OnexEvent
from omnibase.protocol.protocol_event_bus import ProtocolEventBus


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
