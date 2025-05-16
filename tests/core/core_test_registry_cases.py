# Canonical test case definitions for core registry tests
# This file is the single source of truth for all registry test cases (positive and negative).
# All field references must use the NodeMetadataField Enum for type safety and maintainability.
# The Enum must be kept in sync with the NodeMetadataBlock model (see model_enum_metadata.py).
#
# Pattern notes:
# - Use classes for test cases to allow future setup/teardown, state, and extensibility.
# - Each test case must have a unique registry ID (used for pytest parameterization and CI reporting).
# - This registry pattern is ready for plugin-based extension in future milestones (see stub below).

import pytest

from omnibase.model.model_enum_metadata import NodeMetadataField
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.protocol.protocol_testable_registry import ProtocolTestableRegistry

# Central registry for all core registry test cases
CORE_REGISTRY_TEST_CASES = {}


def register_core_registry_test_case(name):
    """
    Decorator to register a test case class in the core registry test case registry.
    The name is used as the pytest ID and for reporting/coverage.
    """

    def decorator(cls):
        CORE_REGISTRY_TEST_CASES[name] = cls
        return cls

    return decorator


@register_core_registry_test_case("canonical_node_success")
class CanonicalNodeSuccessCase:
    """
    Positive test: Registry returns a canonical node stub with all required and optional fields.
    """

    node_id = "example_node_id"
    expect_success = True

    def run(self, registry: ProtocolTestableRegistry):
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

    node_id = "nonexistent_node_id"
    expect_success = False

    def run(self, registry: ProtocolTestableRegistry):
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


def test_node_metadata_field_enum_matches_model():
    model_fields = set(NodeMetadataBlock.model_fields.keys())
    enum_fields = set(f.value for f in NodeMetadataField)
    assert model_fields == enum_fields, (
        f"Enum fields: {enum_fields}\nModel fields: {model_fields}\n"
        "NodeMetadataField Enum and NodeMetadataBlock model are out of sync!"
    )
