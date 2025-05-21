import logging
from typing import Any, Callable, Protocol

from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.runtime.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtime.protocol.protocol_node_runner import ProtocolNodeRunner

logger = logging.getLogger(__name__)


class NodeRunner(ProtocolNodeRunner):
    """
    Canonical runner for ONEX node execution with event emission.
    Emits NODE_START, NODE_SUCCESS, and NODE_FAILURE events via ProtocolEventBus.
    Handles exceptions and lifecycle management.
    Implements ProtocolNodeRunner.
    """

    def __init__(
        self,
        node_callable: Callable[..., Any],
        event_bus: ProtocolEventBus,
        node_id: str,
    ) -> None:
        self.node_callable = node_callable
        self.event_bus = event_bus
        self.node_id = node_id

    def run(self, *args, **kwargs) -> Any:
        start_event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id=self.node_id,
            metadata={"args": args, "kwargs": kwargs},
        )
        self.event_bus.publish(start_event)
        try:
            result = self.node_callable(*args, **kwargs)
            success_event = OnexEvent(
                event_type=OnexEventTypeEnum.NODE_SUCCESS,
                node_id=self.node_id,
                metadata={"result": result},
            )
            self.event_bus.publish(success_event)
            return result
        except Exception as exc:
            logger.exception(f"Node execution failed: {exc}")
            failure_event = OnexEvent(
                event_type=OnexEventTypeEnum.NODE_FAILURE,
                node_id=self.node_id,
                metadata={"error": str(exc)},
            )
            self.event_bus.publish(failure_event)
            raise
