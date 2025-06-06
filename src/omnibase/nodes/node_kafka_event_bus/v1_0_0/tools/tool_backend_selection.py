from omnibase.enums.log_level import LogLevelEnum
from omnibase.protocol.protocol_tool_backend_selection import (
    ToolBackendSelectionProtocol,
)
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import ModelKafkaEventBusConfig
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import (
    emit_log_event_sync,
    make_log_context,
)


class ToolBackendSelection(ToolBackendSelectionProtocol):
    """
    Protocol-compliant tool for selecting and instantiating the event bus backend (Kafka or InMemory).
    Accepts a strongly-typed ModelKafkaEventBusConfig and returns a ProtocolEventBus instance.
    Emits log events for backend selection and degraded mode.

    Usage:
        from .tool_backend_selection import tool_backend_selection
        event_bus = tool_backend_selection.select_event_bus(config)
    """

    def select_event_bus(
        self, config: ModelKafkaEventBusConfig = None, logger=None
    ) -> ProtocolEventBus:
        node_id = "node_kafka_event_bus"
        if config is not None:
            try:
                # Isolated import: Only place KafkaEventBus is referenced per ONEX standards
                from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import (
                    KafkaEventBus,
                )

                bus = KafkaEventBus(config)
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[tool_backend_selection] Using KafkaEventBus backend.",
                    make_log_context(node_id=node_id),
                )
                return bus
            except Exception as e:
                emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"[tool_backend_selection] Failed to instantiate KafkaEventBus: {e}. Falling back to InMemoryEventBus.",
                    make_log_context(node_id=node_id),
                )
        emit_log_event_sync(
            LogLevelEnum.INFO,
            "[tool_backend_selection] Using InMemoryEventBus backend.",
            make_log_context(node_id=node_id),
        )
        return InMemoryEventBus()


# Singleton instance for import
tool_backend_selection = ToolBackendSelection()
