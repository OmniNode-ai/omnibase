# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 778c7dfd-29bc-4754-9170-08142ccfda5c
# name: utils_test_stamper_cases.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:54.108002
# last_modified_at: 2025-05-19T16:19:54.108004
# description: Stamped Python file: utils_test_stamper_cases.py
# state_contract: none
# lifecycle: active
# hash: 5751fd5296525338fc8b5d81bd4778efa6e6a567f6b7996988d10d68192b46a8
# entrypoint: {'type': 'python', 'target': 'utils_test_stamper_cases.py'}
# namespace: onex.stamped.utils_test_stamper_cases.py
# meta_type: tool
# === /OmniNode:Metadata ===

"""
Registry-driven test case definitions for CLIStamper protocol tests.
Each case defines file content, type, expected status, and expected message.
"""

from typing import Any, Callable

from omnibase.model.enum_onex_status import OnexStatus

STAMPER_TEST_CASES: dict[str, type] = {}


def register_stamper_test_case(name: str) -> Callable[[type], type]:
    """Decorator to register a test case class in the stamper test case registry."""

    def decorator(cls: type) -> type:
        STAMPER_TEST_CASES[name] = cls
        return cls

    return decorator


@register_stamper_test_case("valid_node_yaml")
class ValidNodeYaml:
    file_type: str = "yaml"

    def __init__(self) -> None:
        self.content: dict[str, Any] = {
            "metadata_version": "0.1.0",
            "protocol_version": "0.1.0",
            "owner": "foundation",
            "copyright": "Copyright foundation",
            "schema_version": "0.0.1",
            "name": "Stub Node",
            "version": "0.0.1",
            "uuid": "00000000-0000-0000-0000-000000000000",
            "author": "OmniNode Team",
            "created_at": "2024-01-01T00:00:00Z",
            "last_modified_at": "2024-01-01T00:00:00Z",
            "description": "Stub node for testing.",
            "state_contract": "stub://contract",
            "lifecycle": "draft",
            "hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "entrypoint": {"type": "python", "target": "main.py"},
            "namespace": "omninode.stub",
            "meta_type": "tool",
            "contract_type": "io_schema",
            "contract": {"inputs": {}, "outputs": {}},
        }
        self.expected_status: OnexStatus = OnexStatus.SUCCESS
        self.expected_message: str = "Simulated stamping for M0:"


@register_stamper_test_case("invalid_node_yaml")
class InvalidNodeYaml:
    file_type: str = "yaml"

    def __init__(self) -> None:
        self.content: dict[str, Any] = {
            "node_id": "test-node-id"
        }  # Missing required fields
        self.expected_status: OnexStatus = OnexStatus.ERROR
        self.expected_message: str = "Semantic validation failed:"


@register_stamper_test_case("empty_yaml")
class EmptyYaml:
    file_type: str = "yaml"

    def __init__(self) -> None:
        self.content: None = None
        self.expected_status: OnexStatus = OnexStatus.WARNING
        self.expected_message: str = "File is empty; stamped with empty status."


@register_stamper_test_case("malformed_yaml")
class MalformedYaml:
    file_type: str = "yaml"

    def __init__(self) -> None:
        self.content: str = "::not:yaml::"
        self.expected_status: OnexStatus = OnexStatus.ERROR
        self.expected_message: str = "Malformed YAML: not a mapping or sequence"


@register_stamper_test_case("valid_node_json")
class ValidNodeJson:
    file_type: str = "json"

    def __init__(self) -> None:
        self.content: dict[str, Any] = {
            "metadata_version": "0.1.0",
            "protocol_version": "0.1.0",
            "owner": "foundation",
            "copyright": "Copyright foundation",
            "schema_version": "0.0.1",
            "name": "Stub Node",
            "version": "0.0.1",
            "uuid": "00000000-0000-0000-0000-000000000000",
            "author": "OmniNode Team",
            "created_at": "2024-01-01T00:00:00Z",
            "last_modified_at": "2024-01-01T00:00:00Z",
            "description": "Stub node for testing.",
            "state_contract": "stub://contract",
            "lifecycle": "draft",
            "hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "entrypoint": {"type": "python", "target": "main.py"},
            "namespace": "omninode.stub",
            "meta_type": "tool",
            "contract_type": "io_schema",
            "contract": {"inputs": {}, "outputs": {}},
        }
        self.expected_status: OnexStatus = OnexStatus.SUCCESS
        self.expected_message: str = "Simulated stamping for M0:"


@register_stamper_test_case("invalid_node_json")
class InvalidNodeJson:
    file_type: str = "json"

    def __init__(self) -> None:
        self.content: dict[str, Any] = {"node_id": "test-node-id"}
        self.expected_status: OnexStatus = OnexStatus.ERROR
        self.expected_message: str = "Semantic validation failed:"


@register_stamper_test_case("empty_json")
class EmptyJson:
    file_type: str = "json"

    def __init__(self) -> None:
        self.content: None = None
        self.expected_status: OnexStatus = OnexStatus.WARNING
        self.expected_message: str = "File is empty; stamped with empty status."


@register_stamper_test_case("malformed_json")
class MalformedJson:
    file_type: str = "json"

    def __init__(self) -> None:
        self.content: str = "{not: json,]"
        self.expected_status: OnexStatus = OnexStatus.ERROR
        self.expected_message: str = "Malformed JSON: not a mapping or sequence"
