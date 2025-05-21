from typing import Any, Protocol


class ProtocolNodeRunner(Protocol):
    """
    Canonical protocol for ONEX node runners (runtime/ placement).
    Requires a run(*args, **kwargs) -> Any method for node execution and event emission.
    All node runner implementations must conform to this interface.
    """

    def run(self, *args, **kwargs) -> Any: ...
