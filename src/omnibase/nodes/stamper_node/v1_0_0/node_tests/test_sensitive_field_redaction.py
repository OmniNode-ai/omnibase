# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_sensitive_field_redaction.py
# version: 1.0.0
# uuid: 91ebdb35-3038-4791-9321-07d362836d11
# author: OmniNode Team
# created_at: 2025-05-26T10:50:18.437943
# last_modified_at: 2025-05-26T16:53:38.727781
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 47d83dd6c7e27866d5a30321b1dea02ff2af20f8e7943cedc091a0c0a8ef510b
# entrypoint: python@test_sensitive_field_redaction.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_sensitive_field_redaction
# meta_type: tool
# === /OmniNode:Metadata ===


from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Set

import pytest

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.nodes.stamper_node.v1_0_0.models.state import (
    STAMPER_STATE_SCHEMA_VERSION,
    StamperInputState,
    StamperOutputState,
)

# Registry for redaction test cases
REDACTION_TEST_CASES = {}


def register_redaction_test_case(case_id: str) -> Any:
    """Decorator to register redaction test cases in the central registry."""

    def decorator(test_case_class: Any) -> Any:
        REDACTION_TEST_CASES[case_id] = test_case_class
        return test_case_class

    return decorator


class RedactionTestType(Enum):
    """Enum for redaction test case types."""

    BASIC_REDACTION = "basic_redaction"
    NESTED_REDACTION = "nested_redaction"
    ADDITIONAL_FIELDS = "additional_fields"
    NONE_VALUES = "none_values"
    PATTERN_DETECTION = "pattern_detection"


class RedactionExpectation(Enum):
    """Enum for expected redaction values."""

    KEY_REDACTED = "[KEY_REDACTED]"
    TOKEN_MASKED = "[MASKED]"
    PASSWORD_REDACTED = "[PASSWORD_REDACTED]"
    SECRET_REDACTED = "[SECRET]"
    GENERIC_REDACTED = "[REDACTED]"
    SENSITIVE_REDACTED = "[SENSITIVE]"


@dataclass
class RedactionTestCase:
    """Protocol-compliant test case for redaction testing."""

    case_id: str
    test_type: RedactionTestType
    input_data: Dict[str, Any]
    expected_redactions: Dict[str, RedactionExpectation]
    preserved_fields: Set[str]
    additional_sensitive_fields: Optional[Set[str]] = None
    description: str = ""


# Context constants for fixture parameterization
MOCK_CONTEXT = 1
INTEGRATION_CONTEXT = 2


@pytest.fixture(
    params=[
        pytest.param(MOCK_CONTEXT, id="mock", marks=pytest.mark.mock),
        pytest.param(
            INTEGRATION_CONTEXT, id="integration", marks=pytest.mark.integration
        ),
    ]
)
def redaction_test_context(request: Any) -> RedactionTestCase:
    """
    Canonical context-switching fixture for redaction tests.

    Context mapping:
      MOCK_CONTEXT = 1 (mock context; in-memory, isolated)
      INTEGRATION_CONTEXT = 2 (integration context; full model validation)
    """
    if request.param == MOCK_CONTEXT:
        return BasicInputRedactionTestCase()
    elif request.param == INTEGRATION_CONTEXT:
        return BasicOutputRedactionTestCase()
    else:
        raise OnexError(
            f"Unknown redaction test context: {request.param}",
            CoreErrorCode.INVALID_PARAMETER,
        )


@pytest.fixture
def redaction_test_registry() -> Dict[str, Any]:
    """Fixture providing access to the redaction test case registry."""
    return REDACTION_TEST_CASES


@pytest.fixture
def stamper_input_state_factory(redaction_test_context: RedactionTestCase) -> Any:
    """
    Factory fixture for creating StamperInputState instances.
    Context-aware for different testing scenarios.
    """

    def create_input_state(**kwargs: Any) -> StamperInputState:
        # Set defaults based on context
        defaults: Dict[str, Any] = {
            "version": STAMPER_STATE_SCHEMA_VERSION,
            "file_path": "/test/file.py",
            "author": "Test User",
            "correlation_id": "test-correlation-123",
            "discover_functions": False,
            "api_key": None,
            "access_token": None,
        }

        # Merge with provided kwargs
        defaults.update(kwargs)

        return StamperInputState(
            version=defaults["version"],
            file_path=defaults["file_path"],
            author=defaults.get("author", "Test User"),
            correlation_id=defaults.get("correlation_id"),
            discover_functions=defaults.get("discover_functions", False),
            api_key=defaults.get("api_key"),
            access_token=defaults.get("access_token"),
        )

    return create_input_state


@pytest.fixture
def stamper_output_state_factory(redaction_test_context: RedactionTestCase) -> Any:
    """
    Factory fixture for creating StamperOutputState instances.
    Context-aware for different testing scenarios.
    """

    def create_output_state(
        input_state: StamperInputState, **kwargs: Any
    ) -> StamperOutputState:
        defaults: Dict[str, Any] = {
            "version": input_state.version,
            "status": "success",
            "message": "Test operation completed",
            "correlation_id": input_state.correlation_id,
            "operation_signature": None,
        }

        # Merge with provided kwargs
        defaults.update(kwargs)

        return StamperOutputState(
            version=defaults["version"],
            status=defaults["status"],
            message=defaults["message"],
            correlation_id=defaults.get("correlation_id"),
            operation_signature=defaults.get("operation_signature"),
        )

    return create_output_state


# Register test cases using the canonical pattern
@register_redaction_test_case("basic_input_redaction")
class BasicInputRedactionTestCase(RedactionTestCase):
    """Test case for basic input state redaction."""

    def __init__(self) -> None:
        super().__init__(
            case_id="basic_input_redaction",
            test_type=RedactionTestType.BASIC_REDACTION,
            input_data={
                "api_key": "sk-1234567890abcdef",
                "access_token": "token_abcdef123456",
                "author": "Alice Smith",  # Contains "auth" pattern
            },
            expected_redactions={
                "api_key": RedactionExpectation.KEY_REDACTED,
                "access_token": RedactionExpectation.TOKEN_MASKED,
                "author": RedactionExpectation.GENERIC_REDACTED,
            },
            preserved_fields={
                "file_path",
                "correlation_id",
                "discover_functions",
                "version",
            },
            description="Basic redaction of sensitive fields in input state",
        )


@register_redaction_test_case("basic_output_redaction")
class BasicOutputRedactionTestCase(RedactionTestCase):
    """Test case for basic output state redaction."""

    def __init__(self) -> None:
        super().__init__(
            case_id="basic_output_redaction",
            test_type=RedactionTestType.BASIC_REDACTION,
            input_data={
                "operation_signature": "sha256:abcdef1234567890",
            },
            expected_redactions={
                "operation_signature": RedactionExpectation.GENERIC_REDACTED,
            },
            preserved_fields={"status", "message", "version", "correlation_id"},
            description="Basic redaction of sensitive fields in output state",
        )


@register_redaction_test_case("none_values_redaction")
class NoneValuesRedactionTestCase(RedactionTestCase):
    """Test case for redaction behavior with None values."""

    def __init__(self) -> None:
        super().__init__(
            case_id="none_values_redaction",
            test_type=RedactionTestType.NONE_VALUES,
            input_data={
                "api_key": None,
                "access_token": "real-token",
            },
            expected_redactions={
                "access_token": RedactionExpectation.TOKEN_MASKED,
            },
            preserved_fields={
                "api_key",
                "file_path",
                "author",
            },  # api_key should remain None
            description="None values should not be redacted",
        )


@register_redaction_test_case("additional_sensitive_fields")
class AdditionalSensitiveFieldsTestCase(RedactionTestCase):
    """Test case for additional sensitive fields specification."""

    def __init__(self) -> None:
        super().__init__(
            case_id="additional_sensitive_fields",
            test_type=RedactionTestType.ADDITIONAL_FIELDS,
            input_data={
                "correlation_id": "secret-correlation-123",
                "author": "Alice Smith",
            },
            expected_redactions={
                "correlation_id": RedactionExpectation.GENERIC_REDACTED,
                "author": RedactionExpectation.GENERIC_REDACTED,
            },
            preserved_fields={"file_path", "version"},
            additional_sensitive_fields={"correlation_id"},
            description="Additional fields can be marked as sensitive",
        )


class TestSensitiveFieldRedaction:
    """
    Protocol-first test suite for sensitive field redaction functionality.

    Tests validate the public redaction contract without relying on
    implementation details.
    """

    def test_input_state_redaction_registry_driven(
        self,
        redaction_test_registry: Dict[str, Any],
        stamper_input_state_factory: Any,
        redaction_test_context: RedactionTestCase,
    ) -> None:
        """Test input state redaction using registry-driven test cases."""
        # Get test case from registry
        test_case = redaction_test_registry["basic_input_redaction"]()

        # Create input state using factory
        input_state = stamper_input_state_factory(**test_case.input_data)

        # Execute redaction
        redacted = input_state.redact(
            additional_sensitive_fields=test_case.additional_sensitive_fields
        )

        # Validate redactions using enum-based assertions
        for field_name, expected_redaction in test_case.expected_redactions.items():
            assert (
                redacted[field_name] == expected_redaction.value
            ), f"Field '{field_name}' should be redacted to '{expected_redaction.value}'"

        # Validate preserved fields
        for field_name in test_case.preserved_fields:
            if field_name in redacted and redacted[field_name] is not None:
                # Field should not be redacted (unless it's a known sensitive pattern)
                original_value = getattr(input_state, field_name)
                if not input_state.is_sensitive_field(field_name):
                    assert (
                        redacted[field_name] == original_value
                    ), f"Non-sensitive field '{field_name}' should be preserved"

    def test_output_state_redaction_registry_driven(
        self,
        redaction_test_registry: Dict[str, Any],
        stamper_input_state_factory: Any,
        stamper_output_state_factory: Any,
        redaction_test_context: RedactionTestCase,
    ) -> None:
        """Test output state redaction using registry-driven test cases."""
        # Get test case from registry
        test_case = redaction_test_registry["basic_output_redaction"]()

        # Create states using factories
        input_state = stamper_input_state_factory()
        output_state = stamper_output_state_factory(input_state, **test_case.input_data)

        # Execute redaction
        redacted = output_state.redact(
            additional_sensitive_fields=test_case.additional_sensitive_fields
        )

        # Validate redactions using enum-based assertions
        for field_name, expected_redaction in test_case.expected_redactions.items():
            assert (
                redacted[field_name] == expected_redaction.value
            ), f"Field '{field_name}' should be redacted to '{expected_redaction.value}'"

        # Validate preserved fields
        for field_name in test_case.preserved_fields:
            if field_name in redacted:
                original_value = getattr(output_state, field_name)
                if not output_state.is_sensitive_field(field_name):
                    assert (
                        redacted[field_name] == original_value
                    ), f"Non-sensitive field '{field_name}' should be preserved"

    def test_none_values_redaction_registry_driven(
        self,
        redaction_test_registry: Dict[str, Any],
        stamper_input_state_factory: Any,
        redaction_test_context: RedactionTestCase,
    ) -> None:
        """Test None value redaction behavior using registry-driven test cases."""
        # Get test case from registry
        test_case = redaction_test_registry["none_values_redaction"]()

        # Create input state using factory
        input_state = stamper_input_state_factory(**test_case.input_data)

        # Execute redaction
        redacted = input_state.redact()

        # Validate that None values are preserved
        assert redacted["api_key"] is None, "None values should not be redacted"

        # Validate that non-None sensitive values are redacted
        for field_name, expected_redaction in test_case.expected_redactions.items():
            assert (
                redacted[field_name] == expected_redaction.value
            ), f"Non-None sensitive field '{field_name}' should be redacted"

    def test_additional_sensitive_fields_registry_driven(
        self,
        redaction_test_registry: Dict[str, Any],
        stamper_input_state_factory: Any,
        redaction_test_context: RedactionTestCase,
    ) -> None:
        """Test additional sensitive fields using registry-driven test cases."""
        # Get test case from registry
        test_case = redaction_test_registry["additional_sensitive_fields"]()

        # Create input state using factory
        input_state = stamper_input_state_factory(**test_case.input_data)

        # Execute redaction with additional sensitive fields
        redacted = input_state.redact(
            additional_sensitive_fields=test_case.additional_sensitive_fields
        )

        # Validate redactions using enum-based assertions
        for field_name, expected_redaction in test_case.expected_redactions.items():
            assert (
                redacted[field_name] == expected_redaction.value
            ), f"Field '{field_name}' should be redacted when marked as additional sensitive"

    def test_redaction_preserves_model_structure(
        self,
        stamper_input_state_factory: Any,
        redaction_test_context: RedactionTestCase,
    ) -> None:
        """Test that redaction preserves the overall model structure."""
        # Create input state using factory
        input_state = stamper_input_state_factory(
            api_key="secret-key", access_token="bearer-token"
        )

        # Get both normal and redacted dumps
        normal_dump = input_state.model_dump()
        redacted_dump = input_state.redact()

        # Validate structure preservation using model-based assertions
        assert set(normal_dump.keys()) == set(
            redacted_dump.keys()
        ), "Redacted model should have same keys as original"

        # Validate type preservation
        for key in normal_dump.keys():
            if normal_dump[key] is not None and redacted_dump[key] is not None:
                assert isinstance(
                    normal_dump[key], type(redacted_dump[key])
                ) or isinstance(
                    redacted_dump[key], type(normal_dump[key])
                ), f"Field '{key}' type should be preserved during redaction"

    def test_model_dump_redacted_convenience_method(
        self,
        stamper_input_state_factory: Any,
        redaction_test_context: RedactionTestCase,
    ) -> None:
        """Test the model_dump_redacted convenience method."""
        # Create input state using factory
        input_state = stamper_input_state_factory(
            api_key="secret-key-123", access_token="bearer-token-456"
        )

        # Test convenience method
        redacted = input_state.model_dump_redacted()

        # Validate using enum-based assertions
        assert redacted["api_key"] == RedactionExpectation.KEY_REDACTED.value
        assert redacted["access_token"] == RedactionExpectation.TOKEN_MASKED.value

        # Test with kwargs
        redacted_excluded = input_state.model_dump_redacted(
            exclude={"discover_functions"}
        )
        assert "discover_functions" not in redacted_excluded
        assert redacted_excluded["api_key"] == RedactionExpectation.KEY_REDACTED.value


# TODO: Automate test case registration via import hooks (Milestone 1 requirement)
# Currently using manual registration with decorators as temporary exception
# See testing.md section 2.1 for automation roadmap
