import os
from typing import Optional

from omnibase.protocol.protocol_event_bus_types import EventBusCredentialsModel
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_zmq import ZmqEventBus


def get_event_bus(
    event_bus_type: Optional[str] = None,
    socket_path: Optional[str] = None,
    credentials: Optional[EventBusCredentialsModel] = None,
    mode: Optional[str] = None,
) -> "ProtocolEventBus":
    """
    Factory to get the appropriate event bus implementation.
    event_bus_type: 'inmemory', 'zmq', or from ONEX_EVENT_BUS_TYPE env var.
    mode: 'bind' (publisher) or 'connect' (subscriber). Default: 'bind' for publisher, 'connect' for subscriber.
    """
    event_bus_type = (
        event_bus_type or os.getenv("ONEX_EVENT_BUS_TYPE", "inmemory").lower()
    )
    if event_bus_type == "inmemory":
        return InMemoryEventBus()
    elif event_bus_type == "zmq":
        # Default mode: 'bind' for publisher, 'connect' for subscriber
        mode = mode or os.getenv("ONEX_EVENT_BUS_MODE", "bind")
        return ZmqEventBus(socket_path=socket_path, credentials=credentials, mode=mode)
    else:
        raise ValueError(f"Unknown event bus type: {event_bus_type}")
