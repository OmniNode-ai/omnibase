# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.459346'
# description: Stamped by PythonHandler
# entrypoint: python://node_runner
# hash: 5584c749c01fef55ebd28d11b9ff1770d4b364572b86f6ce2ac2277c7e39e975
# last_modified_at: '2025-05-29T14:14:00.659576+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: node_runner.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.node_runner
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 5fa96f8b-6a0d-4842-9f88-b855d10dfdf8
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Any, Callable

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevel
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.protocol.protocol_node_runner import ProtocolNodeRunner

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


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

    def run(self, *args: Any, **kwargs: Any) -> Any:
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
            emit_log_event(
                LogLevel.ERROR,
                f"Node execution failed: {exc}",
                node_id=_COMPONENT_NAME,
                event_bus=self.event_bus,
            )
            failure_event = OnexEvent(
                event_type=OnexEventTypeEnum.NODE_FAILURE,
                node_id=self.node_id,
                metadata={"error": str(exc)},
            )
            self.event_bus.publish(failure_event)
            raise
