# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: node_runner.py
# version: 1.0.0
# uuid: 5fa96f8b-6a0d-4842-9f88-b855d10dfdf8
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.459346
# last_modified_at: 2025-05-28T17:20:04.605307
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 9018df5abc9e48cc2a99d991230084450e9cc3edcd77f73661ad49beaee309cf
# entrypoint: python@node_runner.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.node_runner
# meta_type: tool
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Any, Callable

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum
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
                LogLevelEnum.ERROR,
                f"Node execution failed: {exc}",
                node_id=_COMPONENT_NAME,
            )
            failure_event = OnexEvent(
                event_type=OnexEventTypeEnum.NODE_FAILURE,
                node_id=self.node_id,
                metadata={"error": str(exc)},
            )
            self.event_bus.publish(failure_event)
            raise
