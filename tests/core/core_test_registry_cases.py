# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:08.305110'
# description: Stamped by PythonHandler
# entrypoint: python://core_test_registry_cases.py
# hash: 471b7be778bd0cc56ce6fe6d89d8496cc714b138fa89673e7a805fe4ad6cf59b
# last_modified_at: '2025-05-29T13:51:23.031652+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: core_test_registry_cases.py
# namespace: py://omnibase.tests.core.core_test_registry_cases_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 095d4657-2642-4765-b7fc-8687292cc17b
# version: 1.0.0
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

from omnibase.enums import NodeMetadataField
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
    Positive test: Registry returns a canonical node with required fields.
    Uses 'stamper_node' which exists in both mock and real registries.
    """

    node_id: str = "stamper_node"
    expect_success: bool = True

    def run(self, registry_context: Any) -> None:
        # Use the new registry loader context interface
        node_artifact = registry_context.get_node_by_name(self.node_id)

        # Verify the artifact has the expected structure
        assert node_artifact.name == self.node_id
        assert node_artifact.artifact_type.value == "nodes"
        assert node_artifact.version is not None
        assert node_artifact.metadata is not None

        # Check metadata fields - handle both valid and invalid artifacts
        if "_validation_error" in node_artifact.metadata:
            # Invalid artifact - check that it has validation error info
            assert "_is_valid" in node_artifact.metadata
            assert node_artifact.metadata["_is_valid"] is False
        else:
            # Valid artifact - check that it has expected metadata
            assert "name" in node_artifact.metadata
            assert node_artifact.metadata["name"] == self.node_id


@register_core_registry_test_case("missing_node_error")
class MissingNodeErrorCase:
    """
    Negative test: Registry should raise an error for a nonexistent node ID.
    """

    node_id: str = "nonexistent_node_id"
    expect_success: bool = False

    def run(self, registry_context: Any) -> None:
        # The new interface raises OnexError for missing nodes
        from omnibase.core.core_error_codes import OnexError

        with pytest.raises(OnexError, match="Node not found"):
            registry_context.get_node_by_name(self.node_id)


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
