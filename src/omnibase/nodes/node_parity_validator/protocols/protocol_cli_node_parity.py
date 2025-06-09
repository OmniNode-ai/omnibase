from typing import Protocol, Any
from omnibase.enums.enum_validation_result import EnumValidationResult

class ProtocolCliNodeParity(Protocol):
    def validate_cli_node_parity(self, node: Any) -> EnumValidationResult: ...  # TODO: Replace Any with canonical model if needed 