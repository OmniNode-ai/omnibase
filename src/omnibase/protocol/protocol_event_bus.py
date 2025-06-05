# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.128231'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_event_bus
# hash: d08b73065d9e8de6ac3b18881f8669d08f07ca6678ec78d1f0cdb96e3b9016eb
# last_modified_at: '2025-05-29T14:14:00.220362+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_event_bus.py
# namespace: python://omnibase.protocol.protocol_event_bus
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 2d9c79c5-6422-462b-b10c-e080a10c1d42
# version: 1.0.0
# === /OmniNode:Metadata ===


import os
from typing import Any, Callable, Dict, Optional, Protocol, runtime_checkable

from omnibase.model.model_onex_event import OnexEvent
from omnibase.protocol.protocol_event_bus_types import (
    EventBusCredentialsModel,
)
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus


@runtime_checkable
class ProtocolEventBus(Protocol):
    """
    Canonical protocol for ONEX event bus (runtime/ placement).
    Defines publish/subscribe interface for event emission and handling.
    All event bus implementations must conform to this interface.
    Follows the Protocol<Name> naming convention for consistency.
    Optionally supports clear() for test/lifecycle management.

    # TODO: Future: Add pluggable backends (Kafka, message persistence, authentication, multi-tenant support)
    """

    def __init__(
        self, credentials: Optional[EventBusCredentialsModel] = None, **kwargs
    ): ...

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
