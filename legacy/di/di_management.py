# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "di_management"
# namespace: "omninode.tools.di_management"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:12+00:00"
# last_modified_at: "2025-05-05T13:00:12+00:00"
# entrypoint: "di_management.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ABC', 'DIContainer', 'ScopedContainer']
# base_class: ['ABC', 'DIContainer', 'ScopedContainer']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Container management functionality for the dependency injection framework.

This module provides advanced container management features:
- Scoped container management
- Container factory and provider
- Async context management for scoped resolution
- Child container support with inheritance
- Container state snapshots for testing
- Middleware pattern for container extensions
"""

import asyncio
import copy
import threading
import uuid
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, Callable, Optional, Type

from foundation.di.di_container import DIContainer, ServiceLifetime
from foundation.di.di_protocol_registration import register_protocols

# Dictionary to store scoped instances by scope ID and service type
_global_scoped_instances = {}

# Counter to ensure unique scope IDs in the unlikely case of a UUID collision
_scope_counter = 0
_scope_lock = threading.Lock()


def get_unique_scope_id():
    """Generate a guaranteed unique scope ID.

    Returns:
        A unique string ID for a scope
    """
    global _scope_counter
    with _scope_lock:
        unique_id = f"{uuid.uuid4()}_{_scope_counter}"
        _scope_counter += 1
        return unique_id


class ScopedContainer(DIContainer):
    """A container with a specific scope, inheriting from a parent container."""

    def __init__(self, parent: DIContainer):
        """Initialize a scoped container with a parent.

        Args:
            parent: The parent container to inherit from
        """
        super().__init__()
        self.parent = parent
        # Generate a unique ID for this scope - used for scoped lifetime
        self.scope_id = get_unique_scope_id()
        # Initialize scope-specific instance cache
        _global_scoped_instances[self.scope_id] = {}

    def resolve(self, service_type: Type, name: str = "", **kwargs):
        """Resolve a service from this container or its parent.

        Args:
            service_type: The type of service to resolve
            name: The name of the service for named resolution
            **kwargs: Additional resolution parameters

        Returns:
            An instance of the requested service
        """
        # Check if this service type is registered with SCOPED lifetime in the parent
        # This is the key change - we need to check the parent for scoped registrations
        parent_has_scoped = False
        if (
            hasattr(self.parent, "_registrations")
            and service_type in self.parent._registrations
        ):
            for reg in self.parent._registrations[service_type]:
                if reg["name"] == name and reg["lifetime"] == ServiceLifetime.SCOPED:
                    parent_has_scoped = True
                    break

        # If parent has a scoped registration, create a new instance for this scope
        if parent_has_scoped:
            # For scoped lifetime, get or create instance specific to this scope
            key = (str(service_type), name)
            scoped_instances = _global_scoped_instances[self.scope_id]

            if key not in scoped_instances:
                # Resolve from parent but don't store the instance directly
                # Instead, we'll create our own instance using the parent's registration
                for reg in self.parent._registrations[service_type]:
                    if (
                        reg["name"] == name
                        and reg["lifetime"] == ServiceLifetime.SCOPED
                    ):
                        if reg["factory"]:
                            # Use factory if available
                            instance = reg["factory"]()
                        elif reg["instance"]:
                            # Use predefined instance if available
                            instance = reg["instance"]
                        else:
                            # Create new instance using parent's implementation type
                            impl_type = reg["implementation_type"]
                            instance = impl_type()

                        scoped_instances[key] = instance
                        break

            return scoped_instances[key]

        # Special handling for scoped services in this container
        if service_type in self._registrations:
            for reg in self._registrations[service_type]:
                if reg["name"] == name and reg["lifetime"] == ServiceLifetime.SCOPED:
                    # For scoped lifetime, get or create instance specific to this scope
                    key = (str(service_type), name)
                    scoped_instances = _global_scoped_instances[self.scope_id]

                    if key not in scoped_instances:
                        if reg["factory"]:
                            # Use factory if available
                            instance = reg["factory"]()
                        elif reg["instance"]:
                            # Use predefined instance if available
                            instance = reg["instance"]
                        else:
                            # Create new instance
                            impl_type = reg["implementation_type"]
                            instance = impl_type()

                        scoped_instances[key] = instance

                    return scoped_instances[key]

        # For non-scoped services or if not found in registrations,
        # first try to resolve locally
        try:
            return super().resolve(service_type, name)
        except Exception:
            # If not found locally, try to resolve from parent
            return self.parent.resolve(service_type, name)

    def __del__(self):
        """Clean up scoped instances when container is destroyed."""
        if self.scope_id in _global_scoped_instances:
            del _global_scoped_instances[self.scope_id]


class AsyncScopedContainer(ScopedContainer):
    """A scoped container with async context management support."""

    def __init__(self, parent: DIContainer):
        """Initialize an async scoped container.

        Args:
            parent: The parent container to inherit from
        """
        super().__init__(parent)
        self._disposables = []  # Services to dispose on exit
        self._child_scopes = []  # Track child scopes to avoid duplicate disposal

    async def __aenter__(self):
        """Enter the async context, returning the container itself."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context, disposing of all scoped services."""
        # Dispose all the registered disposables in reverse order
        # Only dispose services that haven't been disposed yet
        for service in reversed(self._disposables):
            if hasattr(service, "disposed") and service.disposed:
                continue  # Skip already disposed services

            if hasattr(service, "dispose") and callable(service.dispose):
                if asyncio.iscoroutinefunction(service.dispose):
                    await service.dispose()
                else:
                    service.dispose()

    def resolve(self, service_type: Type, name: str = "", **kwargs):
        """Resolve a service and register it for disposal if it has a dispose method.

        Args:
            service_type: The type of service to resolve
            name: The name of the service for named resolution
            **kwargs: Additional resolution parameters

        Returns:
            An instance of the requested service
        """
        instance = super().resolve(service_type, name)

        # If the service has a dispose method, register it for disposal
        if hasattr(instance, "dispose") and callable(instance.dispose):
            # Only add to disposables if not already in the list
            if instance not in self._disposables:
                self._disposables.append(instance)

        return instance

    def create_async_scope(self):
        """Create a child async scope that inherits from this scope.

        Returns:
            An async context manager for a child scoped container
        """
        # Create a child scope with this as the parent
        child_scope = AsyncScopedContainer(self)
        # Keep track of this child scope
        self._child_scopes.append(child_scope)

        @asynccontextmanager
        async def async_scope_context():
            try:
                yield child_scope
            finally:
                await child_scope.__aexit__(None, None, None)

        return async_scope_context()


class ChildContainer(DIContainer):
    """A child container that inherits registrations from its parent."""

    def __init__(self, parent: DIContainer):
        """Initialize a child container with a parent.

        Args:
            parent: The parent container to inherit from
        """
        super().__init__()
        self.parent = parent

    def resolve(self, service_type: Type, name: str = "", **kwargs):
        """Resolve a service from this container or its parent.

        Args:
            service_type: The type of service to resolve
            name: The name of the service for named resolution
            **kwargs: Additional resolution parameters

        Returns:
            An instance of the requested service
        """
        # Try to resolve locally first
        try:
            return super().resolve(service_type, name)
        except Exception:
            # If not found locally, try to resolve from parent
            return self.parent.resolve(service_type, name)


class ContainerSnapshot:
    """A snapshot of container state for testing and restoration."""

    def __init__(self, container: DIContainer):
        """Create a snapshot of the container's state.

        Args:
            container: The container to snapshot
        """
        self.registrations = copy.deepcopy(container._registrations)
        self.instances = copy.deepcopy(container._singleton_instances)
        self.scoped_instances = copy.deepcopy(container._scoped_instances)
        self.context = copy.deepcopy(container._context)


class ContainerMiddleware(ABC):
    """Base interface for container middleware."""

    @abstractmethod
    def process(
        self,
        service: Any,
        service_type: Type,
        next_middleware: Callable[[Any, Type], Any],
    ) -> Any:
        """Process a service instance during resolution.

        Args:
            service: The service instance being resolved
            service_type: The type of service being resolved
            next_middleware: The next middleware in the chain

        Returns:
            The processed service instance
        """
        pass


# Store original methods before monkey-patching
_original_di_register = DIContainer.register
_original_di_register_factory = DIContainer.register_factory


# Extend DIContainer with management methods directly
def add_container_management_methods():
    """Add management methods to the DIContainer class."""

    def create_scope(self) -> ScopedContainer:
        """Create a new scoped container.

        Returns:
            A new scoped container with this container as parent
        """
        return ScopedContainer(self)

    def create_child(self) -> ChildContainer:
        """Create a new child container.

        Returns:
            A new child container with this container as parent
        """
        return ChildContainer(self)

    @asynccontextmanager
    async def create_async_scope(self):
        """Create a new async scoped container.

        Returns:
            An async context manager for a scoped container
        """
        scoped = AsyncScopedContainer(self)
        try:
            yield scoped
        finally:
            # Manually trigger async exit to ensure disposal
            await scoped.__aexit__(None, None, None)

    def create_snapshot(self) -> ContainerSnapshot:
        """Create a snapshot of the current container state.

        Returns:
            A snapshot of the container state
        """
        return ContainerSnapshot(self)

    def restore_snapshot(self, snapshot: ContainerSnapshot) -> None:
        """Restore the container state from a snapshot.

        Args:
            snapshot: The snapshot to restore from
        """
        self._registrations = copy.deepcopy(snapshot.registrations)
        self._singleton_instances = copy.deepcopy(snapshot.instances)
        self._scoped_instances = copy.deepcopy(snapshot.scoped_instances)
        self._context = copy.deepcopy(snapshot.context)

    def use_middleware(self, middleware: ContainerMiddleware) -> None:
        """Add middleware to the container's resolution pipeline.

        Args:
            middleware: The middleware to add
        """
        # Initialize middleware list if not already done
        if not hasattr(self, "middleware"):
            self.middleware = []

        # Add middleware to the list
        self.middleware.append(middleware)

        # Replace the resolve method with middleware version
        if len(self.middleware) == 1:
            # Store original resolve method
            original_resolve = self.resolve

            # Define new resolve method with middleware
            def resolve_with_middleware(service_type, name="", **kwargs):
                # First get the service instance using original resolve
                service = original_resolve(service_type, name)

                # Define middleware chain recursively
                def process_middleware(svc, svc_type, middleware_index=0):
                    if middleware_index < len(self.middleware):
                        current_middleware = self.middleware[middleware_index]

                        # Define next middleware function
                        def next_middleware(processed_svc, processed_type):
                            return process_middleware(
                                processed_svc, processed_type, middleware_index + 1
                            )

                        # Process through current middleware
                        return current_middleware.process(
                            service=svc,
                            service_type=svc_type,
                            next_middleware=next_middleware,
                        )
                    else:
                        # End of middleware chain, return the service
                        return svc

                # Start processing through middleware chain
                return process_middleware(service, service_type)

            # Replace the resolve method
            self.resolve = resolve_with_middleware

    # Add methods to DIContainer
    setattr(DIContainer, "create_scope", create_scope)
    setattr(DIContainer, "create_child", create_child)
    setattr(DIContainer, "create_async_scope", create_async_scope)
    setattr(DIContainer, "create_snapshot", create_snapshot)
    setattr(DIContainer, "restore_snapshot", restore_snapshot)
    setattr(DIContainer, "use_middleware", use_middleware)

    # Define modified register method to handle factory
    def register_with_factory_support(
        self,
        service_type: Type,
        implementation_type: Optional[Type] = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
        name: str = "",
        factory: Optional[Callable] = None,
        **kwargs,
    ):
        """Extended register method with factory support.

        This allows using a factory keyword argument with register.

        Args:
            service_type: The service type to register
            implementation_type: Optional implementation type
            lifetime: Service lifetime
            name: Optional service name
            factory: Optional factory function to create the service
            **kwargs: Additional arguments passed to the original register
        """
        if factory is not None:
            # Use register_factory if a factory is provided
            return _original_di_register_factory(
                self, service_type, factory, lifetime, name
            )
        else:
            # Use the original register method
            return _original_di_register(
                self, service_type, implementation_type, lifetime, name, **kwargs
            )

    # Replace register method with extended version
    setattr(DIContainer, "register", register_with_factory_support)


class DIContainerFactory:
    """Factory for creating preconfigured DI containers."""

    def __init__(self):
        """Initialize the container factory."""
        self.default_registrations = []

    def add_default_registration(self, service_type, **kwargs):
        """Add a default registration for all containers created by this factory.

        Args:
            service_type: The type of service to register
            **kwargs: Additional registration parameters

        Returns:
            The factory instance for method chaining
        """
        self.default_registrations.append((service_type, kwargs))
        return self

    def create_container(self) -> DIContainer:
        """Create a new container with default registrations.

        Returns:
            A new DI container with default registrations
        """
        container = DIContainer()
        for service_type, kwargs in self.default_registrations:
            container.register(service_type, **kwargs)
        register_protocols(container)  # Register all core Protocols
        return container

    def create_child_container(self, parent: DIContainer) -> ChildContainer:
        """Create a new child container with the given parent.

        Args:
            parent: The parent container

        Returns:
            A new child container with the specified parent
        """
        return parent.create_child()


# Apply management extensions when this module is imported
add_container_management_methods()