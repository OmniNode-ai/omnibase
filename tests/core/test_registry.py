import pytest
from omnibase.protocol.protocol_testable_registry import ProtocolTestableRegistry

REQUIRED_FIELDS = [
    "name",
    "stub",
    "schema_version",
    "uuid",
    "meta_type",
    "entrypoint",
    "state_contract",
    "dependencies",
    "base_class",
    "protocols_supported",
    "environment",
    "license",
]

OPTIONAL_FIELDS = [
    "reducer",
    "cache",
    "performance",
    "trust",
    "x-extensions",
]

class TestSchemaRegistry:
    def test_fixture_returns_testable_registry(self, registry: ProtocolTestableRegistry):
        """
        Ensure the registry fixture returns a ProtocolTestableRegistry instance (mock or real).
        """
        assert isinstance(registry, ProtocolTestableRegistry)

    def test_get_node_returns_canonical_stub(self, registry: ProtocolTestableRegistry):
        """
        Ensure get_node returns a dict with all required and optional fields for a given node ID (mock or real).
        """
        node_id = "example_node_id"
        node_stub = registry.get_node(node_id)
        assert isinstance(node_stub, dict)
        assert node_stub["name"] == node_id
        assert node_stub["stub"] is True
        for field in REQUIRED_FIELDS:
            assert field in node_stub, f"Missing required field: {field}"
        for field in OPTIONAL_FIELDS:
            assert field in node_stub, f"Missing optional/future field: {field}"
