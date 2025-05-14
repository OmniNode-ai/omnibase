# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "di_container"
# namespace: "omninode.tools.di_container"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:12+00:00"
# last_modified_at: "2025-05-05T13:00:12+00:00"
# entrypoint: "di_container.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Enum']
# base_class: ['Enum']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Dependency Injection Container for the foundation module.

This module provides a wrapper around the Punq dependency injection container,
adding additional functionality such as service lifetime management.
"""

import inspect
import threading
from enum import Enum, auto
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
    get_type_hints,
)

if TYPE_CHECKING:
    from foundation.di.di_container import DIContainer

import punq
from foundation.di.di_advanced import (
    ConditionalResolver,
    DependencyValidationError,
    DependencyValidator,
)
from foundation.di.di_interfaces import InterfaceResolver, ProtocolResolver
from punq import MissingDependencyError

T = TypeVar("T")
TImplementation = TypeVar("TImplementation")


class ServiceLifetime(Enum):
    """Enumeration of service lifetimes."""

    TRANSIENT = auto()
    SCOPED = auto()
    SINGLETON = auto()


class DIContainer:
    """Dependency Injection Container for the foundation module."""

    def __init__(self) -> None:
        """Initialize a new DI container."""
        self._container = punq.Container()
        self._registrations: Dict[Type[Any], List[Dict[str, Any]]] = {}
        self._singleton_instances: Dict[Type[Any], Dict[str, Any]] = {}
        self._scoped_instances: Dict[int, Dict[Type[Any], Dict[str, Any]]] = {}
        self._context: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def register(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[TImplementation]] = None,
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
        name: str = "",
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        priority: int = 0,
    ) -> None:
        """Register a service with the container.

        Args:
            service_type: The service type to register.
            implementation_type: The implementation type to use.
            lifetime: The service lifetime.
            name: The name of the service. Used for named registrations.
            condition: Optional condition function for conditional resolution.
            priority: Priority for conditional resolution (higher priorities are chosen first).
        """
        with self._lock:
            if implementation_type is None:
                implementation_type = cast(Type[TImplementation], service_type)

            # Register with punq if not conditional
            if condition is None:
                self._register_with_punq(
                    service_type, implementation_type, lifetime, name
                )

            # Store registration metadata
            if service_type not in self._registrations:
                self._registrations[service_type] = []

            self._registrations[service_type].append(
                {
                    "implementation_type": implementation_type,
                    "lifetime": lifetime,
                    "factory": None,
                    "instance": None,
                    "name": name,
                    "condition": condition,
                    "priority": priority,
                }
            )

            # Clear any cached instances for this service type
            if lifetime == ServiceLifetime.SINGLETON:
                if (
                    service_type in self._singleton_instances
                    and name in self._singleton_instances[service_type]
                ):
                    del self._singleton_instances[service_type][name]

    def register_factory(
        self,
        service_type: Type[T],
        factory: Union[Callable[[], T], Callable[["DIContainer"], T]],
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
        name: str = "",
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> None:
        """Register a factory function for a service.

        Args:
            service_type: The service type to register.
            factory: The factory function to create the service.
                Either a function that takes no arguments,
                or a function that takes a DIContainer argument.
            lifetime: The lifetime of the service.
            name: The name of the service. Used for named registrations.
            condition: A condition function that decides if this registration should be used.
        """
        # Figure out if the factory takes a container argument
        sig = inspect.signature(factory)
        param_count = len(sig.parameters)

        # Create a wrapper factory if necessary
        wrapped_factory: Callable[[], T]
        if param_count == 1:
            # Factory takes a container argument
            wrapped_factory = lambda: factory(self)
        else:
            # Factory takes no arguments
            wrapped_factory = factory

        # Delegate to the parent method
        self._register_factory(
            service_type=service_type,
            factory=wrapped_factory,
            lifetime=lifetime,
            name=name,
            condition=condition,
        )

    def _register_factory(
        self,
        service_type: Type[T],
        factory: Callable[[], T],
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
        name: str = "",
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> None:
        """Internal method to register a factory function for a service.

        Args:
            service_type: The service type to register.
            factory: The factory function to create the service.
            lifetime: The lifetime of the service.
            name: The name of the service. Used for named registrations.
            condition: A condition function that decides if this registration should be used.
        """
        with self._lock:
            # Store the registration
            if service_type not in self._registrations:
                self._registrations[service_type] = []

            self._registrations[service_type].append(
                {
                    "implementation_type": None,
                    "factory": factory,
                    "instance": None,
                    "lifetime": lifetime,
                    "name": name,
                    "condition": condition,
                }
            )

            # Register with punq
            if lifetime == ServiceLifetime.SINGLETON:
                # For singletons, create a wrapper factory that caches the instance
                def singleton_factory():
                    if service_type not in self._singleton_instances:
                        self._singleton_instances[service_type] = {}

                    if name not in self._singleton_instances[service_type]:
                        self._singleton_instances[service_type][name] = factory()

                    return self._singleton_instances[service_type][name]

                if name:
                    self._container.register(
                        service_type, factory=singleton_factory, name=name
                    )
                else:
                    self._container.register(service_type, factory=singleton_factory)

            elif lifetime == ServiceLifetime.SCOPED:
                # For scoped services, create a wrapper factory that caches per scope
                def scoped_factory():
                    scope_id = id(self)

                    if scope_id not in self._scoped_instances:
                        self._scoped_instances[scope_id] = {}

                    if service_type not in self._scoped_instances[scope_id]:
                        self._scoped_instances[scope_id][service_type] = {}

                    if name not in self._scoped_instances[scope_id][service_type]:
                        self._scoped_instances[scope_id][service_type][name] = factory()

                    return self._scoped_instances[scope_id][service_type][name]

                if name:
                    self._container.register(
                        service_type, factory=scoped_factory, name=name
                    )
                else:
                    self._container.register(service_type, factory=scoped_factory)

            else:  # TRANSIENT
                # For transient services, just register the factory as-is
                if name:
                    self._container.register(service_type, factory=factory, name=name)
                else:
                    self._container.register(service_type, factory=factory)

    def register_instance(
        self,
        service_type: Type[T],
        instance: T,
        name: str = "",
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        priority: int = 0,
    ) -> None:
        """Register a specific instance for a service.

        Args:
            service_type: The service type to register.
            instance: The instance to register.
            name: The name of the service. Used for named registrations.
            condition: Optional condition function for conditional resolution.
            priority: Priority for conditional resolution (higher priorities are chosen first).
        """
        with self._lock:
            # Register with punq if not conditional
            if condition is None:
                self._register_instance_with_punq(service_type, instance, name)

            # Store registration metadata
            if service_type not in self._registrations:
                self._registrations[service_type] = []

            self._registrations[service_type].append(
                {
                    "implementation_type": type(instance),
                    "lifetime": ServiceLifetime.SINGLETON,
                    "factory": None,
                    "instance": instance,
                    "name": name,
                    "condition": condition,
                    "priority": priority,
                }
            )

            # Add to singleton instances
            if service_type not in self._singleton_instances:
                self._singleton_instances[service_type] = {}

            self._singleton_instances[service_type][name] = instance

    def resolve(self, service_type: Type[T], name: str = "") -> T:
        """Resolve a service from the container.

        Args:
            service_type: The service type to resolve.
            name: The name of the service. Used for named registrations.

        Returns:
            An instance of the service.

        Raises:
            MissingDependencyError: If the service is not registered.
        """
        with self._lock:
            # Check for conditional registrations
            registrations = self._registrations.get(service_type, [])
            conditional_registrations = [
                r for r in registrations if r.get("condition") is not None
            ]

            if conditional_registrations:
                # Find matching conditional registration
                try:
                    registration = ConditionalResolver.resolve_conditions(
                        service_type, conditional_registrations, self._context
                    )

                    # Use the registration to create an instance
                    if (
                        "instance" in registration
                        and registration["instance"] is not None
                    ):
                        return cast(T, registration["instance"])
                    elif (
                        "factory" in registration
                        and registration["factory"] is not None
                    ):
                        return cast(T, registration["factory"]())
                    else:
                        implementation_type = registration["implementation_type"]
                        if implementation_type:
                            return cast(T, self._create_instance(implementation_type))
                except ValueError:
                    # No matching conditional registration, fall back to regular resolution
                    pass

            # Try to resolve from singleton cache first
            if (
                service_type in self._singleton_instances
                and name in self._singleton_instances[service_type]
            ):
                return cast(T, self._singleton_instances[service_type][name])

            # Try to resolve from scope cache
            scope_id = id(self)
            if (
                scope_id in self._scoped_instances
                and service_type in self._scoped_instances[scope_id]
                and name in self._scoped_instances[scope_id][service_type]
            ):
                return cast(T, self._scoped_instances[scope_id][service_type][name])

            # Check if service_type is an interface or protocol
            is_interface = InterfaceResolver.is_abstract_base_class(service_type)
            is_protocol = ProtocolResolver.is_protocol(service_type)

            if is_interface or is_protocol:
                # Look for registrations that implement this interface or protocol
                for (
                    registered_type,
                    registered_implementations,
                ) in self._registrations.items():
                    for reg in registered_implementations:
                        impl_type = reg.get("implementation_type")

                        if not impl_type:
                            continue

                        reg_name = reg.get("name", "")
                        if name and reg_name != name:
                            continue

                        lifetime = reg.get("lifetime", ServiceLifetime.TRANSIENT)

                        matching = False
                        if is_interface and InterfaceResolver.is_implementation_of(
                            impl_type, service_type
                        ):
                            matching = True
                        elif is_protocol and ProtocolResolver.is_implementation_of(
                            impl_type, service_type
                        ):
                            matching = True

                        if matching:
                            # Found an implementation for the interface or protocol
                            if reg.get("instance") is not None:
                                return cast(T, reg["instance"])
                            elif reg.get("factory") is not None:
                                # Create instance from factory
                                instance = reg["factory"]()

                                # Cache instance if singleton
                                if lifetime == ServiceLifetime.SINGLETON:
                                    if service_type not in self._singleton_instances:
                                        self._singleton_instances[service_type] = {}

                                    self._singleton_instances[service_type][
                                        name
                                    ] = instance

                                # Cache instance if scoped
                                elif lifetime == ServiceLifetime.SCOPED:
                                    if scope_id not in self._scoped_instances:
                                        self._scoped_instances[scope_id] = {}

                                    if (
                                        service_type
                                        not in self._scoped_instances[scope_id]
                                    ):
                                        self._scoped_instances[scope_id][
                                            service_type
                                        ] = {}

                                    self._scoped_instances[scope_id][service_type][
                                        name
                                    ] = instance

                                return cast(T, instance)
                            else:
                                # Create instance from implementation type
                                instance = self._create_instance(impl_type)

                                # Cache instance if singleton
                                if lifetime == ServiceLifetime.SINGLETON:
                                    if service_type not in self._singleton_instances:
                                        self._singleton_instances[service_type] = {}

                                    self._singleton_instances[service_type][
                                        name
                                    ] = instance

                                # Cache instance if scoped
                                elif lifetime == ServiceLifetime.SCOPED:
                                    if scope_id not in self._scoped_instances:
                                        self._scoped_instances[scope_id] = {}

                                    if (
                                        service_type
                                        not in self._scoped_instances[scope_id]
                                    ):
                                        self._scoped_instances[scope_id][
                                            service_type
                                        ] = {}

                                    self._scoped_instances[scope_id][service_type][
                                        name
                                    ] = instance

                                return cast(T, instance)

            # Resolve from punq
            try:
                if name:
                    instance = self._container.resolve(service_type, name)
                else:
                    instance = self._container.resolve(service_type)

                # Cache singleton instances
                registration = next(
                    (
                        r
                        for r in self._registrations.get(service_type, [])
                        if r["name"] == name
                    ),
                    None,
                )
                if (
                    registration
                    and registration["lifetime"] == ServiceLifetime.SINGLETON
                ):
                    if service_type not in self._singleton_instances:
                        self._singleton_instances[service_type] = {}

                    self._singleton_instances[service_type][name] = instance

                # Cache scoped instances
                elif (
                    registration and registration["lifetime"] == ServiceLifetime.SCOPED
                ):
                    if scope_id not in self._scoped_instances:
                        self._scoped_instances[scope_id] = {}

                    if service_type not in self._scoped_instances[scope_id]:
                        self._scoped_instances[scope_id][service_type] = {}

                    self._scoped_instances[scope_id][service_type][name] = instance

                return cast(T, instance)
            except MissingDependencyError:
                raise MissingDependencyError(
                    f"No registration found for {service_type.__name__}"
                )

    def can_resolve(self, service_type: Type[T], name: str = "") -> bool:
        """Check if a service can be resolved.

        Args:
            service_type: The service type to check.
            name: The name of the service. Used for named registrations.

        Returns:
            True if the service can be resolved, False otherwise.
        """
        with self._lock:
            # Check singleton instances
            if (
                service_type in self._singleton_instances
                and name in self._singleton_instances[service_type]
            ):
                return True

            # Check scoped instances
            scope_id = id(self)
            if (
                scope_id in self._scoped_instances
                and service_type in self._scoped_instances[scope_id]
                and name in self._scoped_instances[scope_id][service_type]
            ):
                return True

            # Check conditional registrations
            registrations = self._registrations.get(service_type, [])
            conditional_registrations = [
                r for r in registrations if r.get("condition") is not None
            ]

            if conditional_registrations:
                try:
                    ConditionalResolver.resolve_conditions(
                        service_type, conditional_registrations, self._context
                    )
                    return True
                except ValueError:
                    pass

            # Check punq
            try:
                if name:
                    self._container.resolve(service_type, name)
                else:
                    self._container.resolve(service_type)
                return True
            except MissingDependencyError:
                return False

    def validate_dependencies(self) -> Dict[str, List[str]]:
        """Validate that all dependencies of registered services are also registered.

        Returns:
            Dictionary mapping service names to lists of missing dependency names.

        Raises:
            DependencyValidationError: If there are missing dependencies.
        """
        # Get all registered service types
        registered_types = set(self._registrations.keys())

        # Get all service types that are registered as implementations
        for registrations in self._registrations.values():
            for reg in registrations:
                impl_type = reg.get("implementation_type")
                if impl_type:
                    registered_types.add(impl_type)

        # Define a function to get dependencies of a service
        def get_dependencies(service_type: Type) -> List[Type]:
            """Get all dependencies of a service type.

            Args:
                service_type: The service type to get dependencies for.

            Returns:
                List of dependency types.
            """
            dependencies = []

            # Skip primitive types
            if service_type in (str, int, float, bool, list, dict, set, tuple):
                return dependencies

            # Try to get constructor signature
            try:
                if (
                    hasattr(service_type, "__init__")
                    and service_type.__init__ is not object.__init__
                ):
                    init_method = service_type.__init__
                    sig = inspect.signature(init_method)
                    type_hints = get_type_hints(init_method)

                    # Add all parameters with type annotations
                    for param_name, param in sig.parameters.items():
                        # Skip self
                        if param_name == "self":
                            continue

                        # Skip optional parameters (those with default values)
                        if param.default is not inspect.Parameter.empty:
                            continue

                        # Add type hint if available
                        if param_name in type_hints:
                            dependencies.append(type_hints[param_name])
            except (TypeError, ValueError):
                # Skip services that can't be inspected
                pass

            return dependencies

        # Validate dependencies
        missing_deps = DependencyValidator.validate_dependencies(
            self._registrations, get_dependencies, registered_types
        )

        # If there are missing dependencies, raise an error
        if missing_deps:
            missing_deps_str = "\n".join(
                f"{service}: {', '.join(deps)}"
                for service, deps in missing_deps.items()
            )
            raise DependencyValidationError(
                f"Missing dependencies:\n{missing_deps_str}"
            )

        return missing_deps

    def detect_circular_dependencies(
        self, special_case_service_names: Optional[List[str]] = None
    ) -> None:
        """Detect circular dependencies in the service registrations.

        Args:
            special_case_service_names: Optional list of service names for special case detection.

        Raises:
            CircularDependencyError: If a circular dependency is detected.
        """
        # Get all registered service types
        registered_types = set(self._registrations.keys())

        # Add all implemented types
        for registrations in self._registrations.values():
            for reg in registrations:
                impl_type = reg.get("implementation_type")
                if impl_type:
                    registered_types.add(impl_type)

        # Define a function to get dependencies of a service
        def get_dependencies(service_type: Type) -> List[Type]:
            """Get all dependencies of a service type.

            Args:
                service_type: The service type to get dependencies for.

            Returns:
                List of dependency types.
            """
            dependencies = []

            # Skip primitive types
            if service_type in (str, int, float, bool, list, dict, set, tuple):
                return dependencies

            # Try to get constructor signature
            try:
                if (
                    hasattr(service_type, "__init__")
                    and service_type.__init__ is not object.__init__
                ):
                    init_method = service_type.__init__
                    sig = inspect.signature(init_method)
                    type_hints = get_type_hints(init_method)

                    # Add all parameters with type annotations
                    for param_name, param in sig.parameters.items():
                        # Skip self
                        if param_name == "self":
                            continue

                        # Skip optional parameters (those with default values)
                        if param.default is not inspect.Parameter.empty:
                            continue

                        # Add type hint if available
                        if param_name in type_hints:
                            dependencies.append(type_hints[param_name])
            except (TypeError, ValueError):
                # Skip services that can't be inspected
                pass

            return dependencies

        # Check each service type for circular dependencies
        for service_type in registered_types:
            DependencyValidator.detect_circular_dependencies(
                service_type,
                get_dependencies,
                special_case_service_names=special_case_service_names,
            )

    def create_scope(self) -> "DIContainer":
        """Create a new scope for scoped services.

        Returns:
            A new scope container.
        """
        # Create a new container with a new container instance
        scope = DIContainer()

        # Copy registrations from parent
        with self._lock:
            for service_type, registrations in self._registrations.items():
                for reg in registrations:
                    # Copy instance registrations
                    if reg["instance"] is not None:
                        # Only add non-scoped instances
                        if reg["lifetime"] != ServiceLifetime.SCOPED:
                            scope.register_instance(
                                service_type,
                                reg["instance"],
                                reg["name"],
                                reg["condition"],
                            )
                    # Copy factory registrations
                    elif reg["factory"] is not None:
                        # If scoped, register in the new scope without lifting the lifetime
                        scope._register_factory(
                            service_type,
                            reg["factory"],
                            reg["lifetime"],
                            reg["name"],
                            reg["condition"],
                        )
                    else:
                        # Copy type registrations
                        impl_type = reg["implementation_type"]

                        if impl_type:
                            scope.register(
                                service_type,
                                impl_type,
                                reg["lifetime"],
                                reg["name"],
                                reg["condition"],
                            )

            # Copy singleton instances
            scope._singleton_instances = self._singleton_instances

        return scope

    def __enter__(self) -> "DIContainer":
        """Enter the scope context.

        Returns:
            This container.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the scope context.

        Args:
            exc_type: The exception type.
            exc_val: The exception value.
            exc_tb: The exception traceback.
        """
        # Clean up scoped instances
        scope_id = id(self)
        if scope_id in self._scoped_instances:
            del self._scoped_instances[scope_id]

    def set_context(self, key: str, value: Any) -> None:
        """Set a context value for conditional resolution.

        Args:
            key: The context key.
            value: The context value.
        """
        with self._lock:
            self._context[key] = value

    def get_context(self, key: str) -> Any:
        """Get a context value for conditional resolution.

        Args:
            key: The context key.

        Returns:
            The context value, or None if not found.
        """
        with self._lock:
            return self._context.get(key)

    def clear_context(self) -> None:
        """Clear the context for conditional resolution."""
        with self._lock:
            self._context.clear()

    def _register_with_punq(
        self,
        service_type: Type[T],
        implementation_type: Type[TImplementation],
        lifetime: ServiceLifetime,
        name: str,
    ) -> None:
        """Register a service with the punq container.

        Args:
            service_type: The service type to register.
            implementation_type: The implementation type to use.
            lifetime: The service lifetime.
            name: The name of the service.
        """
        if lifetime == ServiceLifetime.SINGLETON:
            # For singletons, register a factory that creates and caches the instance
            if name:
                self._container.register(
                    service_type,
                    factory=lambda: self._resolve_singleton(
                        service_type, implementation_type, name
                    ),
                    instance_name=name,
                )
            else:
                self._container.register(
                    service_type,
                    factory=lambda: self._resolve_singleton(
                        service_type, implementation_type, name
                    ),
                )
        elif lifetime == ServiceLifetime.SCOPED:
            # For scoped, register a factory that creates and caches the instance per scope
            if name:
                self._container.register(
                    service_type,
                    factory=lambda: self._resolve_scoped(
                        service_type, implementation_type, name
                    ),
                    instance_name=name,
                )
            else:
                self._container.register(
                    service_type,
                    factory=lambda: self._resolve_scoped(
                        service_type, implementation_type, name
                    ),
                )
        else:  # TRANSIENT
            # For transient, register a factory that creates a new instance each time
            if name:
                self._container.register(
                    service_type,
                    factory=lambda: self._create_instance(implementation_type),
                    instance_name=name,
                )
            else:
                self._container.register(
                    service_type,
                    factory=lambda: self._create_instance(implementation_type),
                )

    def _register_instance_with_punq(
        self, service_type: Type[T], instance: T, name: str
    ) -> None:
        """Register an instance with the punq container.

        Args:
            service_type: The service type to register.
            instance: The instance to register.
            name: The name of the service.
        """
        if name:
            self._container.register(
                service_type, instance=instance, instance_name=name
            )
        else:
            self._container.register(service_type, instance=instance)

    def _resolve_singleton(
        self, service_type: Type[T], implementation_type: Type[Any], name: str
    ) -> T:
        """Resolve a singleton service.

        Args:
            service_type: The service type to resolve.
            implementation_type: The implementation type to use.
            name: The name of the service.

        Returns:
            An instance of the service.
        """
        # Check if already cached
        if (
            service_type in self._singleton_instances
            and name in self._singleton_instances[service_type]
        ):
            return cast(T, self._singleton_instances[service_type][name])

        # Create new instance
        instance = self._create_instance(implementation_type)

        # Cache the instance
        if service_type not in self._singleton_instances:
            self._singleton_instances[service_type] = {}

        self._singleton_instances[service_type][name] = instance

        return instance

    def _resolve_scoped(
        self, service_type: Type[T], implementation_type: Type[Any], name: str
    ) -> T:
        """Resolve a scoped service.

        Args:
            service_type: The service type to resolve.
            implementation_type: The implementation type to use.
            name: The name of the service.

        Returns:
            An instance of the service.
        """
        # Get scope ID
        scope_id = id(self)

        # Check if already cached for this scope
        if (
            scope_id in self._scoped_instances
            and service_type in self._scoped_instances[scope_id]
            and name in self._scoped_instances[scope_id][service_type]
        ):
            return cast(T, self._scoped_instances[scope_id][service_type][name])

        # Create new instance
        instance = self._create_instance(implementation_type)

        # Cache the instance for this scope
        if scope_id not in self._scoped_instances:
            self._scoped_instances[scope_id] = {}

        if service_type not in self._scoped_instances[scope_id]:
            self._scoped_instances[scope_id][service_type] = {}

        self._scoped_instances[scope_id][service_type][name] = instance

        return instance

    def _create_instance(self, implementation_type: Type[T]) -> T:
        """Create a new instance of a service.

        Args:
            implementation_type: The implementation type to create.

        Returns:
            A new instance of the service.
        """
        # Get constructor signature
        try:
            sig = inspect.signature(implementation_type.__init__)
            type_hints = get_type_hints(implementation_type.__init__)
        except (TypeError, ValueError):
            # If we can't inspect the constructor, try to create without arguments
            return implementation_type()

        # Build constructor arguments
        kwargs = {}
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            # Check if parameter has a type hint
            if param_name in type_hints:
                param_type = type_hints[param_name]

                # Check if parameter has a default value
                if param.default is not inspect.Parameter.empty:
                    # Optional parameter, try to resolve but don't fail if not found
                    if self.can_resolve(param_type):
                        kwargs[param_name] = self.resolve(param_type)
                else:
                    # Required parameter, resolve or fail
                    kwargs[param_name] = self.resolve(param_type)

        # Create and return the instance
        return implementation_type(**kwargs)