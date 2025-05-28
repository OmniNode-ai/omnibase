# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: messagebus_event_adapter.py
# version: 1.0.0
# uuid: 113bbe6e-9575-4a4f-ade5-ce15edda783d
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.346017
# last_modified_at: 2025-05-28T17:20:04.976023
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 4b15bbf5dc96bbc833c43b6a5d72c6db1b333a2ef665f88b390cdbcafe64ee4e
# entrypoint: python@messagebus_event_adapter.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.messagebus_event_adapter
# meta_type: tool
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
