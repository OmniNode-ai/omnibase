from typing import Protocol, Any
from omnibase.enums.enum_validation_result import EnumValidationResult

class ProtocolErrorCodeUsage(Protocol):
    def validate_error_code_usage(self, node: Any) -> EnumValidationResult: ...  # TODO: Replace Any with canonical model if needed 