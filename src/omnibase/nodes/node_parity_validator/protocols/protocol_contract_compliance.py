from typing import Protocol, Any
from omnibase.enums.enum_validation_result import EnumValidationResult

class ProtocolContractCompliance(Protocol):
    def validate_contract_compliance(self, node: Any) -> EnumValidationResult: ...  # TODO: Replace Any with canonical model if needed 