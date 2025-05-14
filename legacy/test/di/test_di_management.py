# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_di_management"
# namespace: "omninode.tools.test_di_management"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:23+00:00"
# last_modified_at: "2025-05-05T13:00:23+00:00"
# entrypoint: "test_di_management.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Service']
# base_class: ['Service']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Tests for the container management features of the DI container.

This module tests the advanced container management features:
- Scoped container management
- Container factory and provider
- Async context management for scoped resolution
- Child container support with inheritance
- Container state snapshots for testing
- Middleware pattern for container extensions
"""

from unittest.mock import MagicMock

import pytest
from foundation.di import DIContainer, ServiceLifetime


class TestScopedContainers:
    """Tests for scoped container functionality."""

    def test_create_scoped_container(self):
        """Test creating a scoped container from a root container."""
        # Arrange
        root = DIContainer()

        # Act
        scoped = root.create_scope()

        # Assert
        assert scoped is not None
        assert scoped != root
        assert scoped.parent == root

    def test_scoped_container_inherits_registrations(self):
        """Test that scoped containers inherit registrations from parent."""
        # Arrange
        root = DIContainer()

        class Service:
            pass

        root.register(Service)

        # Act
        scoped = root.create_scope()
        resolved = scoped.resolve(Service)

        # Assert
        assert resolved is not None
        assert isinstance(resolved, Service)

    def test_scoped_container_isolation(self):
        """Test that scoped containers have isolated registrations."""
        # Arrange
        root = DIContainer()

        class RootService:
            pass

        class ScopedService:
            pass

        root.register(RootService)

        # Act
        scoped = root.create_scope()
        scoped.register(ScopedService)

        # Assert
        assert root.resolve(RootService) is not None
        with pytest.raises(
            Exception
        ):  # Should not be able to resolve ScopedService from root
            root.resolve(ScopedService)

        assert (
            scoped.resolve(RootService) is not None
        )  # Can resolve parent registrations
        assert (
            scoped.resolve(ScopedService) is not None
        )  # Can resolve own registrations

    def test_scoped_lifetimes(self):
        """Test that scoped lifetime services are properly scoped."""
        # Arrange
        root = DIContainer()

        class Service:
            pass

        # Register as scoped
        root.register(Service, lifetime=ServiceLifetime.SCOPED)

        # Act
        scoped1 = root.create_scope()
        scoped2 = root.create_scope()

        service1_a = scoped1.resolve(Service)
        service1_b = scoped1.resolve(Service)

        service2_a = scoped2.resolve(Service)
        service2_b = scoped2.resolve(Service)

        # Debug print statements to verify the objects are different
        print(f"Service1_a id: {id(service1_a)}")
        print(f"Service2_a id: {id(service2_a)}")
        print(f"Service1_a is Service2_a: {service1_a is service2_a}")

        # Assert
        # Same scope should return same instance
        assert service1_a is service1_b
        assert service2_a is service2_b

        # Different scopes should return different instances
        assert service1_a is not service2_a


class TestContainerFactory:
    """Tests for container factory functionality."""

    def test_container_factory_creation(self):
        """Test creating containers through a factory."""
        # Arrange
        factory = DIContainerFactory()

        # Act
        container = factory.create_container()

        # Assert
        assert container is not None
        assert isinstance(container, DIContainer)

    def test_factory_with_default_registrations(self):
        """Test factory with default registrations."""

        # Arrange
        class Logger:
            pass

        class Config:
            pass

        # Create factory with default registrations
        factory = DIContainerFactory()
        factory.add_default_registration(Logger)
        factory.add_default_registration(Config)

        # Act
        container = factory.create_container()

        # Assert
        assert container.resolve(Logger) is not None
        assert container.resolve(Config) is not None

    def test_factory_creates_child_containers(self):
        """Test factory creating child containers."""
        # Arrange
        factory = DIContainerFactory()
        parent = factory.create_container()

        # Act
        child = factory.create_child_container(parent)

        # Assert
        assert child is not None
        assert child.parent == parent


class TestAsyncContextManagement:
    """Tests for async context management functionality."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test using container as an async context manager."""
        # Arrange
        root = DIContainer()

        class Service:
            def __init__(self):
                self.disposed = False

            async def dispose(self):
                self.disposed = True

        root.register(Service, lifetime=ServiceLifetime.SCOPED)

        # Act
        service = None
        async with root.create_async_scope() as scope:
            service = scope.resolve(Service)
            assert not service.disposed

        # Assert
        assert service.disposed  # Should be disposed after exiting context

    @pytest.mark.asyncio
    async def test_nested_async_scopes(self):
        """Test nested async scopes."""
        # Arrange
        root = DIContainer()

        disposals = []

        class Service:
            def __init__(self, name: str):
                self.name = name
                self.disposed = False

            async def dispose(self):
                self.disposed = True
                disposals.append(self.name)

        class ServiceA(Service):
            def __init__(self):
                super().__init__("A")

        class ServiceB(Service):
            def __init__(self):
                super().__init__("B")

        class ServiceC(Service):
            def __init__(self):
                super().__init__("C")

        root.register(ServiceA, lifetime=ServiceLifetime.SCOPED)
        root.register(ServiceB, lifetime=ServiceLifetime.SCOPED)
        root.register(ServiceC, lifetime=ServiceLifetime.SCOPED)

        # Act
        async with root.create_async_scope() as scope1:
            service_a = scope1.resolve(ServiceA)

            async with scope1.create_async_scope() as scope2:
                service_b = scope2.resolve(ServiceB)

                async with scope2.create_async_scope() as scope3:
                    service_c = scope3.resolve(ServiceC)

        # Assert
        assert service_a.disposed
        assert service_b.disposed
        assert service_c.disposed

        # Disposal should happen in reverse order (C, B, A)
        assert disposals == ["C", "B", "A"]


class TestChildContainers:
    """Tests for child container functionality."""

    def test_child_container_creation(self):
        """Test creating a child container."""
        # Arrange
        parent = DIContainer()

        # Act
        child = parent.create_child()

        # Assert
        assert child is not None
        assert child.parent == parent

    def test_child_container_inheritance(self):
        """Test that child containers inherit registrations."""
        # Arrange
        parent = DIContainer()

        class ParentService:
            pass

        parent.register(ParentService)

        # Act
        child = parent.create_child()
        service = child.resolve(ParentService)

        # Assert
        assert service is not None
        assert isinstance(service, ParentService)

    def test_child_container_override(self):
        """Test that child containers can override parent registrations."""
        # Arrange
        parent = DIContainer()

        class Service:
            def get_name(self):
                return "Parent"

        class ChildService(Service):
            def get_name(self):
                return "Child"

        parent.register(Service)

        # Act
        child = parent.create_child()
        child.register(Service, factory=lambda c: ChildService())

        parent_service = parent.resolve(Service)
        child_service = child.resolve(Service)

        # Assert
        assert parent_service.get_name() == "Parent"
        assert child_service.get_name() == "Child"


class TestContainerSnapshots:
    """Tests for container state snapshot functionality."""

    def test_create_snapshot(self):
        """Test creating a snapshot of container state."""
        # Arrange
        container = DIContainer()

        class Service:
            def __init__(self):
                self.value = 0

        container.register(Service, lifetime=ServiceLifetime.SINGLETON)

        # Modify the state
        service = container.resolve(Service)
        service.value = 42

        # Act
        snapshot = container.create_snapshot()

        # Assert
        assert snapshot is not None

    def test_restore_snapshot(self):
        """Test restoring a container state from snapshot."""
        # Arrange
        container = DIContainer()

        class Service:
            def __init__(self):
                self.value = 0

        container.register(Service, lifetime=ServiceLifetime.SINGLETON)

        # Modify the state
        service = container.resolve(Service)
        service.value = 42

        # Create snapshot
        snapshot = container.create_snapshot()

        # Modify state again
        service.value = 100

        # Act
        container.restore_snapshot(snapshot)
        restored_service = container.resolve(Service)

        # Assert
        assert restored_service.value == 42  # Should have the value from snapshot


class TestContainerMiddleware:
    """Tests for container middleware functionality."""

    def test_middleware_registration(self):
        """Test registering middleware with the container."""
        # Arrange
        container = DIContainer()
        middleware = MagicMock()

        # Act
        container.use_middleware(middleware)

        # Assert
        assert middleware in container.middleware

    def test_middleware_execution_on_resolve(self):
        """Test that middleware is executed during resolve operations."""
        # Arrange
        container = DIContainer()

        class Service:
            pass

        container.register(Service)

        middleware = MagicMock()
        middleware.process.return_value = Service()
        container.use_middleware(middleware)

        # Act
        container.resolve(Service)

        # Assert
        middleware.process.assert_called_once()
        args, kwargs = middleware.process.call_args
        assert kwargs["service_type"] == Service

    def test_middleware_chain(self):
        """Test that multiple middleware form a chain."""
        # Arrange
        container = DIContainer()

        class Service:
            def __init__(self):
                self.value = 0

        container.register(Service)

        # Create middleware to modify the service
        middleware1 = MockMiddleware(
            lambda service: setattr(service, "value", 1) or service
        )
        middleware2 = MockMiddleware(
            lambda service: setattr(service, "value", service.value + 1) or service
        )
        middleware3 = MockMiddleware(
            lambda service: setattr(service, "value", service.value * 2) or service
        )

        # Add middleware in order
        container.use_middleware(middleware1)
        container.use_middleware(middleware2)
        container.use_middleware(middleware3)

        # Act
        service = container.resolve(Service)

        # Assert
        assert service.value == 4  # (1 + 1) * 2 = 4


# Mock classes for testing container middleware
class MockMiddleware:
    def __init__(self, processor):
        self.processor = processor

    def process(self, service, service_type, next_middleware):
        # Process the service
        modified_service = self.processor(service)
        # Call the next middleware in the chain
        return next_middleware(modified_service, service_type)


# Container factory class (to be implemented)
class DIContainerFactory:
    def __init__(self):
        self.default_registrations = []

    def add_default_registration(self, service_type, **kwargs):
        self.default_registrations.append((service_type, kwargs))
        return self

    def create_container(self):
        container = DIContainer()
        for service_type, kwargs in self.default_registrations:
            container.register(service_type, **kwargs)
        return container

    def create_child_container(self, parent):
        child = parent.create_child()
        return child