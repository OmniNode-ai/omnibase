# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_di_advanced"
# namespace: "omninode.tools.test_di_advanced"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:23+00:00"
# last_modified_at: "2025-05-05T13:00:23+00:00"
# entrypoint: "test_di_advanced.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['IDIService']
# base_class: ['IDIService']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Tests for advanced features of the dependency injection container (pytest style, flexible setup).

This module tests the advanced features of the DI container such as
named service registration, conditional resolution, and circular dependency detection.
"""

from typing import Optional

import pytest
from foundation.di.di_advanced import CircularDependencyError, DependencyValidationError
from foundation.di.di_container import DIContainer, ServiceLifetime


class DevConfigProvider:
    """A configuration provider for development environments."""

    def get_config(self) -> dict:
        """Get the development configuration."""
        return {"env": "dev", "debug": True}


class ProdConfigProvider:
    """A configuration provider for production environments."""

    def get_config(self) -> dict:
        """Get the production configuration."""
        return {"env": "prod", "debug": False}


class ConditionalService:
    """A service that uses different configurations based on environment."""

    def __init__(
        self,
        dev_config: Optional[DevConfigProvider] = None,
        prod_config: Optional[ProdConfigProvider] = None,
    ):
        """Initialize the service with optional configurations.

        Args:
            dev_config: Development configuration provider.
            prod_config: Production configuration provider.
        """
        self.dev_config = dev_config
        self.prod_config = prod_config

        # Use the appropriate config based on availability
        if dev_config is not None:
            self.config = dev_config
        elif prod_config is not None:
            self.config = prod_config
        else:
            self.config = None


class NamedService:
    """A service with a name."""

    def __init__(self, name: str):
        """Initialize the service with a name.

        Args:
            name: The name of the service.
        """
        self.name = name


class ServiceWithMissingDependency:
    """A service with a missing dependency."""

    def __init__(self, nonexistent_service: object):
        """Initialize the service with a dependency.

        Args:
            nonexistent_service: A service that doesn't exist.
        """
        self.nonexistent_service = nonexistent_service


# Test doubles for circular dependency using IDIService
class DIServiceA:
    """First service in a circular dependency chain."""

    def __init__(self, service_b: "IDIService"):
        """Initialize with a dependency on ServiceB.

        Args:
            service_b: An instance of ServiceB.
        """
        self.service_b = service_b

    def do_something(self):
        return f"A with {self.service_b.do_something()}"


class DIServiceB:
    """Second service in a circular dependency chain."""

    def __init__(self, service_c: "IDIService"):
        """Initialize with a dependency on ServiceC.

        Args:
            service_c: An instance of ServiceC.
        """
        self.service_c = service_c

    def do_something(self):
        return f"B with {self.service_c.do_something()}"


class DIServiceC:
    """Third service in a circular dependency chain."""

    def __init__(self, service_a: "IDIService"):
        """Initialize with a dependency on ServiceA.

        Args:
            service_a: An instance of ServiceA.
        """
        self.service_a = service_a

    def do_something(self):
        return f"C with {self.service_a.do_something()}"


@pytest.fixture
def container():
    """Fixture for a fresh DIContainer instance."""
    return DIContainer()


def test_named_service_registration(container):
    """Test registering and resolving named services."""
    container.register_instance(NamedService, NamedService("service1"), name="service1")
    container.register_instance(NamedService, NamedService("service2"), name="service2")
    service1 = container.resolve(NamedService, name="service1")
    service2 = container.resolve(NamedService, name="service2")
    assert service1.name == "service1"
    assert service2.name == "service2"
    with pytest.raises(Exception):
        container.resolve(NamedService, name="service3")


def test_conditional_dependencies():
    """Test conditional resolution of dependencies."""
    container = DIContainer()
    dev_config = DevConfigProvider()
    prod_config = ProdConfigProvider()
    container.register_instance(
        DevConfigProvider, dev_config, condition=lambda ctx: ctx.get("env") == "dev"
    )
    container.register_instance(
        ProdConfigProvider, prod_config, condition=lambda ctx: ctx.get("env") == "prod"
    )
    container.register_instance(DevConfigProvider, dev_config)
    container.register_instance(ProdConfigProvider, prod_config)
    container.set_context("env", "dev")
    container.register_factory(
        ConditionalService,
        lambda: ConditionalService(dev_config=container.resolve(DevConfigProvider)),
    )
    service = container.resolve(ConditionalService)
    assert isinstance(service.config, DevConfigProvider)
    container2 = DIContainer()
    container2.register_instance(
        DevConfigProvider, dev_config, condition=lambda ctx: ctx.get("env") == "dev"
    )
    container2.register_instance(
        ProdConfigProvider, prod_config, condition=lambda ctx: ctx.get("env") == "prod"
    )
    container2.register_instance(DevConfigProvider, dev_config)
    container2.register_instance(ProdConfigProvider, prod_config)
    container2.set_context("env", "prod")
    container2.register_factory(
        ConditionalService,
        lambda: ConditionalService(prod_config=container2.resolve(ProdConfigProvider)),
    )
    service2 = container2.resolve(ConditionalService)
    assert isinstance(service2.config, ProdConfigProvider)


def test_dependency_validation():
    """Test validation of dependencies."""
    container = DIContainer()
    container.register(ServiceWithMissingDependency)
    with pytest.raises(DependencyValidationError):
        container.validate_dependencies()


def test_circular_dependency_detection():
    """Test detection of circular dependencies using IDIService test doubles."""
    container = DIContainer()
    container.register(DIServiceA)
    container.register(DIServiceB)
    container.register(DIServiceC)
    with pytest.raises(CircularDependencyError):
        container.detect_circular_dependencies()


def test_service_lifetimes(container):
    """Test different service lifetimes."""
    container.register(DevConfigProvider, lifetime=ServiceLifetime.SINGLETON)
    container.register(ProdConfigProvider, lifetime=ServiceLifetime.TRANSIENT)
    singleton1 = container.resolve(DevConfigProvider)
    singleton2 = container.resolve(DevConfigProvider)
    assert singleton1 is singleton2
    transient1 = container.resolve(ProdConfigProvider)
    transient2 = container.resolve(ProdConfigProvider)
    assert transient1 is not transient2