from typing import Protocol

from omnibase.model.model_onex_event import OnexEvent


class ProtocolEventStore(Protocol):
    """
    Canonical protocol for ONEX event stores (runtime/ placement).
    Requires store_event(event: OnexEvent) -> None and close() -> None methods for event durability.
    All event store implementations must conform to this interface.
    """

    def store_event(self, event: OnexEvent) -> None: ...

    def close(self) -> None: ...
