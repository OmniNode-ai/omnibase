"""
Hybrid pattern test for MetadataRegistryTemplate: protocol compliance, empty registry, and registration/lookup.
Subclasses BaseRegistryTest and implements ProtocolTestRegistryTemplate.
"""
import pytest
from foundation.template.metadata.metadata_template_registry import MetadataRegistryTemplate
from foundation.protocol.protocol_template_registry import ProtocolRegistryTemplate
from foundation.base.base_registry_test import BaseRegistryTest
from foundation.protocol.protocol_test_registry_template import ProtocolTestRegistryTemplate

class TestMetadataRegistryTemplate(BaseRegistryTest):
    """
    Hybrid pattern test for MetadataRegistryTemplate: protocol compliance, empty registry, and registration/lookup.
    """
    registry_class = MetadataRegistryTemplate
    protocol_class = ProtocolRegistryTemplate

    def test_protocol_compliance(self) -> None:
        """Ensure the registry implements ProtocolRegistryTemplate."""
        registry = self.registry_class()
        assert isinstance(registry, self.protocol_class)

    def test_registry_empty_before_registration(self) -> None:
        """Registry should be empty before templates are registered."""
        registry = self.registry_class()
        assert registry.list() == []
        assert registry.get("python") is None
        assert registry.get_template_for_extension(".py") is None

    def test_register_and_lookup_templates(self) -> None:
        """Register templates and verify lookup by name and extension."""
        registry = self.registry_class()
        registry.register_templates()
        # Check all expected names
        expected_names = {"python", "yaml", "markdown"}
        assert set(registry.list()) == expected_names
        # Check get by name
        for name in expected_names:
            template = registry.get(name)
            assert isinstance(template, str)
            assert template  # Not empty
        # Check get_template_for_extension
        assert registry.get_template_for_extension(".py") == registry.get("python")
        assert registry.get_template_for_extension(".yaml") == registry.get("yaml")
        assert registry.get_template_for_extension(".yml") == registry.get("yaml")
        assert registry.get_template_for_extension(".md") == registry.get("markdown")
        # Unknown extension returns None
        assert registry.get_template_for_extension(".txt") is None
        # Unknown name returns None
        assert registry.get("not_a_template") is None 