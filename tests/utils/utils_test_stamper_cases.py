"""
Registry-driven test case definitions for CLIStamper protocol tests.
Each case defines file content, type, expected status, and expected message.
"""
from typing import Any, Callable
from omnibase.model.model_onex_message_result import OnexStatus  # type: ignore[import-untyped]

STAMPER_TEST_CASES: dict[str, type] = {}

def register_stamper_test_case(name: str) -> Callable[[type], type]:
    def decorator(cls: type) -> type:
        STAMPER_TEST_CASES[name] = cls
        return cls
    return decorator

@register_stamper_test_case("valid_node_yaml")
class ValidNodeYaml:
    file_type: str = "yaml"
    content: dict[str, Any] = {
        "schema_version": "1.0.0",
        "name": "test_node",
        "version": "1.0.0",
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "author": "Test Author",
        "created_at": "2025-01-01T00:00:00Z",
        "last_modified_at": "2025-01-01T00:00:00Z",
        "description": "A valid node",
        "state_contract": "contract-1",
        "lifecycle": "active",
        "hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "entrypoint": {"type": "python", "target": "main.py"},
        "namespace": "onex.test",
        "meta_type": "tool",
    }
    expected_status: Any = OnexStatus.success
    expected_message: str = "Simulated stamping"

@register_stamper_test_case("invalid_node_yaml")
class InvalidNodeYaml:
    file_type: str = "yaml"
    content: dict[str, Any] = {
        "schema_version": "1.0.0",
        "name": "test_node",
        # Missing required field 'version'
        "uuid": "not-a-uuid",
        "author": "Test Author",
        "created_at": "2025-01-01T00:00:00Z",
        "last_modified_at": "2025-01-01T00:00:00Z",
        "description": "A node with errors",
        "state_contract": "contract-1",
        "lifecycle": "not_a_valid_lifecycle",
        "hash": "not-a-valid-hash",
        "entrypoint": {"type": "invalid_type", "target": 123},
        "namespace": "invalid namespace",
        "meta_type": "invalid_type",
    }
    expected_status: Any = OnexStatus.error
    expected_message: str = "Semantic validation failed"

@register_stamper_test_case("empty_yaml")
class EmptyYaml:
    file_type: str = "yaml"
    content: None = None
    expected_status: Any = OnexStatus.warning
    expected_message: str = "empty"

@register_stamper_test_case("malformed_yaml")
class MalformedYaml:
    file_type: str = "yaml"
    content: str = "::not yaml::"
    expected_status: Any = OnexStatus.error
    expected_message: str = "Malformed YAML: not a mapping or sequence"

@register_stamper_test_case("valid_node_json")
class ValidNodeJson:
    file_type: str = "json"
    content: dict[str, Any] = {
        "schema_version": "1.0.0",
        "name": "test_node",
        "version": "1.0.0",
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "author": "Test Author",
        "created_at": "2025-01-01T00:00:00Z",
        "last_modified_at": "2025-01-01T00:00:00Z",
        "description": "A valid node",
        "state_contract": "contract-1",
        "lifecycle": "active",
        "hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "entrypoint": {"type": "python", "target": "main.py"},
        "namespace": "onex.test",
        "meta_type": "tool",
    }
    expected_status: Any = OnexStatus.success
    expected_message: str = "Simulated stamping"

@register_stamper_test_case("invalid_node_json")
class InvalidNodeJson:
    file_type: str = "json"
    content: dict[str, Any] = {
        "schema_version": "1.0.0",
        "name": "test_node",
        # Missing required field 'version'
        "uuid": "not-a-uuid",
        "author": "Test Author",
        "created_at": "2025-01-01T00:00:00Z",
        "last_modified_at": "2025-01-01T00:00:00Z",
        "description": "A node with errors",
        "state_contract": "contract-1",
        "lifecycle": "not_a_valid_lifecycle",
        "hash": "not-a-valid-hash",
        "entrypoint": {"type": "invalid_type", "target": 123},
        "namespace": "invalid namespace",
        "meta_type": "invalid_type",
    }
    expected_status: Any = OnexStatus.error
    expected_message: str = "Semantic validation failed"

@register_stamper_test_case("empty_json")
class EmptyJson:
    file_type: str = "json"
    content: dict[str, Any] = {}
    expected_status: Any = OnexStatus.warning
    expected_message: str = "empty"

@register_stamper_test_case("malformed_json")
class MalformedJson:
    file_type: str = "json"
    content: str = "{not: json,}"
    expected_status: Any = OnexStatus.error
    expected_message: str = "Malformed JSON: not a mapping or sequence" 