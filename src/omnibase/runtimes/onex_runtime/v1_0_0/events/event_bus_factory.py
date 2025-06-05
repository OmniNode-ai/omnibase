import os
from typing import Optional, Any

from omnibase.protocol.protocol_event_bus_types import EventBusCredentialsModel
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.kafka_event_bus import KafkaEventBus
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import KafkaEventBusConfigModel


def get_event_bus(
    event_bus_type: Optional[str] = None,
    socket_path: Optional[str] = None,
    credentials: Optional[EventBusCredentialsModel] = None,
    mode: Optional[str] = None,
    config: Optional[Any] = None,
) -> "ProtocolEventBus":
    """
    Factory to get the appropriate event bus implementation.
    event_bus_type: 'inmemory', 'kafka', or from ONEX_EVENT_BUS_TYPE env var.
    mode: 'bind' (publisher) or 'connect' (subscriber). Default: 'bind' for publisher, 'connect' for subscriber.
    config: Optional config object for KafkaEventBus (must be KafkaEventBusConfigModel if event_bus_type is 'kafka').
    """
    event_bus_type = (
        event_bus_type or os.getenv("ONEX_EVENT_BUS_TYPE", "inmemory").lower()
    )
    if event_bus_type == "inmemory":
        return InMemoryEventBus()
    elif event_bus_type == "kafka":
        if config is None or not isinstance(config, KafkaEventBusConfigModel):
            raise ValueError("KafkaEventBus requires a KafkaEventBusConfigModel as config.")
        return KafkaEventBus(config)
    else:
        raise ValueError(f"Unknown event bus type: {event_bus_type}")
