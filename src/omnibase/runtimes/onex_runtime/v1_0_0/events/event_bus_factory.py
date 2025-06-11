import os
from typing import Any, Optional

from omnibase.enums.log_level import LogLevelEnum
from omnibase.model.model_event_bus_config import ModelEventBusConfig
from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import (
    KafkaEventBus,
)
from omnibase.protocol.protocol_event_bus_types import EventBusCredentialsModel
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import (
    emit_log_event_sync,
    make_log_context,
)


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
    config: Optional config object for KafkaEventBus (must be ModelEventBusConfig if event_bus_type is 'kafka').
    """
    event_bus_type = (
        event_bus_type or os.getenv("ONEX_EVENT_BUS_TYPE", "inmemory").lower()
    )
    if event_bus_type == "inmemory":
        return InMemoryEventBus()
    elif event_bus_type == "kafka":
        if config is None or not isinstance(config, ModelEventBusConfig):
            raise ValueError(
                "KafkaEventBus requires a ModelEventBusConfig as config."
            )
        try:
            return KafkaEventBus(config)
        except ImportError as e:
            emit_log_event_sync(
                LogLevelEnum.WARNING,
                f"[event_bus_factory] aiokafka not available or import failed: {e}. Falling back to InMemoryEventBus.",
                make_log_context(node_id="event_bus_factory"),
            )
            return InMemoryEventBus()
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.WARNING,
                f"[event_bus_factory] KafkaEventBus unavailable: {e}. Falling back to InMemoryEventBus.",
                make_log_context(node_id="event_bus_factory"),
            )
            return InMemoryEventBus()
    else:
        raise ValueError(f"Unknown event bus type: {event_bus_type}")
