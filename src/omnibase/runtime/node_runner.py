# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: node_runner.py
# version: 1.0.0
# uuid: '5868b004-788a-4676-b447-ec0e406b9b65'
# author: OmniNode Team
# created_at: '2025-05-22T05:34:29.791347'
# last_modified_at: '2025-05-22T18:33:30.857451'
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: '0000000000000000000000000000000000000000000000000000000000000000'
# entrypoint:
#   type: python
#   target: node_runner.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.node_runner
# meta_type: tool
# trust_score: null
# tags: null
# capabilities: null
# protocols_supported: null
# base_class: null
# dependencies: null
# inputs: null
# outputs: null
# environment: null
# license: null
# signature_block: null
# x_extensions: {}
# testing: null
# os_requirements: null
# architectures: null
# container_image_reference: null
# compliance_profiles: []
# data_handling_declaration: null
# logging_config: null
# source_repository: null
# === /OmniNode:Metadata ===


import logging
from typing import Any, Callable

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
