# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 9602beee-aecc-420b-9371-d5598b77f9bf
# name: core_test_registry_cases.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:59.176084
# last_modified_at: 2025-05-19T16:19:59.176086
# description: Stamped Python file: core_test_registry_cases.py
# state_contract: none
# lifecycle: active
# hash: 2edf3cf58791c2259fbe5b9646696a834240663fae7f9f6ff3e426a38bd08757
# entrypoint: {'type': 'python', 'target': 'core_test_registry_cases.py'}
# namespace: onex.stamped.core_test_registry_cases.py
# meta_type: tool
# === /OmniNode:Metadata ===

# Canonical test case definitions for core registry tests
# This file is the single source of truth for all registry test cases (positive and negative).
# All field references must use the NodeMetadataField Enum for type safety and maintainability.
# The Enum must be kept in sync with the NodeMetadataBlock model (see model_enum_metadata.py).
#
# Pattern notes:
# - Use classes for test cases to allow future setup/teardown, state, and extensibility.
# - Each test case must have a unique registry ID (used for pytest parameterization and CI reporting).
# - This registry pattern is ready for plugin-based extension in future milestones (see stub below).

from typing import Any, Callable

import pytest

from omnibase.model.model_enum_metadata import NodeMetadataField
from omnibase.model.model_node_metadata import NodeMetadataBlock

# Central registry for all core registry test cases
CORE_REGISTRY_TEST_CASES: dict[str, type] = {}


def register_core_registry_test_case(name: str) -> Callable[[type], type]:
    """
    Decorator to register a test case class in the core registry test case registry.
    The name is used as the pytest ID and for reporting/coverage.
    """

    def decorator(cls: type) -> type:
        CORE_REGISTRY_TEST_CASES[name] = cls
        return cls

    return decorator


@register_core_registry_test_case("canonical_node_success")
class CanonicalNodeSuccessCase:
    """
    Positive test: Registry returns a canonical node stub with all required and optional fields.
    """

    node_id: str = "example_node_id"
    expect_success: bool = True

    def run(self, registry: Any) -> None:
        node = registry.get_node(self.node_id)
        assert isinstance(node, dict)
        assert node[NodeMetadataField.NODE_ID.value] == self.node_id
        assert node["stub"] is True
        for field in NodeMetadataField.required() + NodeMetadataField.optional():
            assert field.value in node, f"Missing field: {field.value}"


@register_core_registry_test_case("missing_node_error")
class MissingNodeErrorCase:
    """
    Negative test: Registry should raise an error for a nonexistent node ID.
    """

    node_id: str = "nonexistent_node_id"
    expect_success: bool = False

    def run(self, registry: Any) -> None:
        from omnibase.core.errors import OmniBaseError

        with pytest.raises(OmniBaseError):
            registry.get_node(self.node_id)


# ---
# Extensibility stub for future plugin/extension support:
# In future milestones, this registry can be replaced or extended by a plugin registry
# (e.g., via entry_points, dynamic import, or plugin discovery hooks).
# No test logic changes will be required—only the registry import will change.
# ---

# ---
# Enum/model sync enforcement test
# This test ensures the NodeMetadataField Enum and NodeMetadataBlock model are always in sync.
# If this test fails, update the Enum or the model to match.


# This enforcement test is intentionally skipped until the full implementation is ready.
# See project standards for stub/test enforcement.
@pytest.mark.skip(reason="Stub: not yet implemented")
def test_node_metadata_field_enum_matches_model() -> None:
    model_fields = set(NodeMetadataBlock.model_fields.keys())
    enum_fields = set(f.value for f in NodeMetadataField)
    assert model_fields == enum_fields, (
        f"Enum fields: {enum_fields}\nModel fields: {model_fields}\n"
        "NodeMetadataField Enum and NodeMetadataBlock model are out of sync!"
    )
