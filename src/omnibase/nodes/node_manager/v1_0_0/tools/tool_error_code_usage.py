from omnibase.enums.enum_validation_result import EnumValidationResult
from omnibase.nodes.node_manager.v1_0_0.models import ModelDiscoveredNode
from omnibase.nodes.node_manager.v1_0_0.protocols.protocol_error_code_usage import ProtocolErrorCodeUsage
from omnibase.nodes.node_logger.protocols.protocol_logger_emit_log_event import ProtocolLoggerEmitLogEvent

class ToolErrorCodeUsage(ProtocolErrorCodeUsage):
    def __init__(self, logger_tool: ProtocolLoggerEmitLogEvent = None):
        if logger_tool is None:
            raise RuntimeError("Logger tool must be provided via DI or registry (protocol-pure).")
        self.logger_tool = logger_tool

    def validate_error_code_usage(self, node: ModelDiscoveredNode) -> EnumValidationResult:
        try:
            import importlib
            error_codes_module_path = (
                f"omnibase.nodes.{node.name}.{node.version}.error_codes"
            )
            error_codes_module = importlib.import_module(error_codes_module_path)
            has_error_codes = any(
                "ErrorCode" in attr
                for attr in dir(error_codes_module)
                if not attr.startswith("_")
            )
            if has_error_codes:
                return EnumValidationResult.PASS
            else:
                return EnumValidationResult.FAIL
        except ImportError:
            return EnumValidationResult.FAIL
        except Exception:
            return EnumValidationResult.ERROR 