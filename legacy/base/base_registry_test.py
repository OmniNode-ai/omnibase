"""
BaseRegistryTest: Canonical base class for all registry/protocol tests (hybrid pattern).
Defines required test methods for protocol compliance, empty registry, and registration/lookup.
"""
import abc
from typing import Type, Any

class BaseRegistryTest(abc.ABC):
    """
    Abstract base class for registry/protocol tests. All registry test classes must subclass this.
    """
    registry_class: Type[Any]
    protocol_class: Type[Any]

    @abc.abstractmethod
    def test_protocol_compliance(self) -> None:
        """Test that the registry implements the required protocol."""
        pass

    @abc.abstractmethod
    def test_registry_empty_before_registration(self) -> None:
        """Test that the registry is empty before templates are registered."""
        pass

    @abc.abstractmethod
    def test_register_and_lookup_templates(self) -> None:
        """Test registration and lookup of templates by name and extension."""
        pass 