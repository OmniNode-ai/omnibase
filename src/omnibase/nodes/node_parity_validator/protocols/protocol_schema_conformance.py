from typing import Protocol, Any
from omnibase.enums.enum_validation_result import EnumValidationResult

class ProtocolSchemaConformance(Protocol):
    def validate_schema_conformance(self, node: Any) -> EnumValidationResult: ...  # TODO: Replace Any with canonical model if needed 