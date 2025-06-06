from typing import Any
from omnibase.enums.onex_status import OnexStatus
from omnibase.model.model_onex_message_result import OnexResultModel, OnexMessageModel
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync, make_log_context
from omnibase.protocol.protocol_tool_health_check import ToolHealthCheckProtocol

class ToolHealthCheck(ToolHealthCheckProtocol):
    def health_check(self, config: Any, node_id: str = "service_node") -> OnexResultModel:
        try:
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[tool_health_check] Health check passed.",
                make_log_context(node_id=node_id),
            )
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                messages=[OnexMessageModel(summary="Health check passed.", level=LogLevelEnum.INFO)],
            )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[tool_health_check] Health check failed: {e}",
                make_log_context(node_id=node_id),
            )
            return OnexResultModel(
                status=OnexStatus.ERROR,
                messages=[OnexMessageModel(summary=f"Health check failed: {e}", level=LogLevelEnum.ERROR)],
            )

tool_health_check = ToolHealthCheck() 