# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: messagebus_event_adapter.py
# version: 1.0.0
# uuid: 7e0e007e-4359-4564-8ad0-f832b8501ddd
# author: OmniNode Team
# created_at: 2025-05-22T17:18:16.710631
# last_modified_at: 2025-05-22T21:19:13.539020
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 2155515bd3ab58332a1c4e14ce1780f3d294a0fab1b5573d14a4c923e1fc54aa
# entrypoint: python@messagebus_event_adapter.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.messagebus_event_adapter
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
