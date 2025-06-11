from typing import Protocol, TypeVar, runtime_checkable
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.model.model_event_bus_config import ModelEventBusConfig

TEventBus = TypeVar("TEventBus", bound=ProtocolEventBus)

@runtime_checkable
class ProtocolEventBusContextManager(Protocol[TEventBus]):
    """
    Protocol for async context managers that yield a ProtocolEventBus-compatible object.
    Used to abstract lifecycle management for event bus resources (e.g., Kafka).
    Implementations must support async context management and return a ProtocolEventBus on enter.
    """
    def __init__(self, config: ModelEventBusConfig): ...
    async def __aenter__(self) -> TEventBus: ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ... 