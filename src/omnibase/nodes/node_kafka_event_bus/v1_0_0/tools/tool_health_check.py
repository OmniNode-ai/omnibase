from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import KafkaEventBus, KafkaEventBusConfigModel, KafkaHealthCheckResult
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync, make_log_context
from omnibase.nodes.node_kafka_event_bus.protocols.tool_health_check_protocol import ToolHealthCheckProtocol

class ToolHealthCheck(ToolHealthCheckProtocol):
    """
    Protocol-compliant tool for performing a health check on the Kafka event bus backend.
    Accepts a strongly-typed KafkaEventBusConfigModel and returns a KafkaHealthCheckResult.
    Emits log events for health check status.

    Usage:
        from .tool_health_check import tool_health_check
        result = tool_health_check.health_check(config)
    """
    def health_check(self, config: KafkaEventBusConfigModel) -> KafkaHealthCheckResult:
        node_id = "node_kafka_event_bus"
        try:
            bus = KafkaEventBus(config)
            import asyncio
            result = asyncio.run(bus.health_check())
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[tool_health_check] Kafka health check result: {result}",
                make_log_context(node_id=node_id),
            )
            return result
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[tool_health_check] Exception during health check: {e}",
                make_log_context(node_id=node_id),
            )
            return KafkaHealthCheckResult(connected=False, error=str(e))

# Singleton instance for import
tool_health_check = ToolHealthCheck() 