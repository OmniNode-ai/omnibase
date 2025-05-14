from foundation.protocol.protocol_in_memory_validate import ProtocolInMemoryValidate
from foundation.model.model_validate import ValidationResult

class InMemoryValidationTestMixin:
    def run_in_memory_validation(self, validator: ProtocolInMemoryValidate, content: str, expected: dict, config: dict = None):
        result: ValidationResult = validator.validate_content(content, config)
        assert result.is_valid == expected["is_valid"], f"Expected is_valid={expected['is_valid']}, got {result.is_valid}"
        if "errors" in expected:
            assert len(result.errors) == expected["errors"], f"Expected {expected['errors']} errors, got {len(result.errors)}"
        if "warnings" in expected:
            assert len(result.warnings) == expected["warnings"], f"Expected {expected['warnings']} warnings, got {len(result.warnings)}"
        # Additional assertions can be added as needed 