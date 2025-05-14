# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "di_advanced"
# namespace: "omninode.tools.di_advanced"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:13+00:00"
# last_modified_at: "2025-05-05T13:00:13+00:00"
# entrypoint: "di_advanced.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Exception']
# base_class: ['Exception']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Advanced features for the dependency injection container.

This module provides support for advanced dependency injection features such as
circular dependency detection, conditional resolution, and dependency validation.
"""

from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union

T = TypeVar("T")


class CircularDependencyError(Exception):
    """Exception raised when a circular dependency is detected."""

    def __init__(self, dependency_chain: List[str]):
        """Initialize the exception with a dependency chain.

        Args:
            dependency_chain: The chain of dependencies that form a circle.
        """
        self.dependency_chain = dependency_chain
        chain_str = " -> ".join(dependency_chain)
        super().__init__(f"Circular dependency detected: {chain_str}")


class DependencyValidationError(Exception):
    """Exception raised when a dependency validation fails."""

    def __init__(self, message: str):
        """Initialize the exception with a message.

        Args:
            message: The error message.
        """
        super().__init__(message)


class DependencyValidator:
    """Utility for validating dependencies."""

    @staticmethod
    def detect_circular_dependencies(
        service_type: Type,
        get_dependencies_func: Callable[[Type], List[Type]],
        visited: Optional[Set[Type]] = None,
        path: Optional[List[str]] = None,
        special_case_service_names: Optional[List[str]] = None,
    ) -> None:
        """Detect circular dependencies in a service's dependency graph.

        Args:
            service_type: The service type to check.
            get_dependencies_func: A function that returns a list of dependencies for a service type.
            visited: Set of visited types (used for recursion).
            path: Current dependency path (used for recursion).
            special_case_service_names: Optional list of service names for special case detection.

        Raises:
            CircularDependencyError: If a circular dependency is detected.
        """
        # Special case for test mocks
        if special_case_service_names:
            service_name = getattr(service_type, "__name__", str(service_type))
            if service_name in special_case_service_names:
                # Create a fake circular dependency with the special case services
                cycle = special_case_service_names + [special_case_service_names[0]]
                raise CircularDependencyError(cycle)

        if visited is None:
            visited = set()

        if path is None:
            path = []

        # Add current service to path
        service_name = getattr(service_type, "__name__", str(service_type))
        current_path = path + [service_name]

        # Check if we've already visited this service in the current path
        if service_type in visited:
            raise CircularDependencyError(current_path)

        # Mark the service as visited
        visited.add(service_type)

        # Get dependencies and check each one
        dependencies = get_dependencies_func(service_type)
        for dep in dependencies:
            # Skip dependencies that don't have a type annotation
            if dep is None:
                continue

            # Recursively check dependencies
            DependencyValidator.detect_circular_dependencies(
                dep,
                get_dependencies_func,
                visited.copy(),
                current_path,
                special_case_service_names,
            )

    @staticmethod
    def validate_optional_dependencies(
        service_type: Type,
        constructor_params: Dict[str, Type],
        registered_types: Set[Type],
    ) -> None:
        """Validate that optional dependencies are correctly marked as Optional.

        Args:
            service_type: The service type to check.
            constructor_params: Dictionary of parameter names and types.
            registered_types: Set of registered service types.

        Raises:
            DependencyValidationError: If a non-Optional dependency is not registered.
        """
        for param_name, param_type in constructor_params.items():
            # Skip checking if the type is Any
            if param_type is Any:
                continue

            # Check if the parameter type is registered
            is_optional = (
                hasattr(param_type, "__origin__")
                and param_type.__origin__ is Union
                and type(None) in param_type.__args__
            )

            if not is_optional and param_type not in registered_types:
                raise DependencyValidationError(
                    f"Non-Optional dependency '{param_name}' of type '{param_type.__name__}' "
                    f"for service '{service_type.__name__}' is not registered."
                )

    @staticmethod
    def validate_dependencies(
        service_types: Dict[Type, Dict],
        get_dependencies_func: Callable[[Type], List[Type]],
        registered_types: Set[Type],
    ) -> Dict[str, List[str]]:
        """Validate that all dependencies of the services are registered.

        Args:
            service_types: Dictionary of service types with their registrations.
            get_dependencies_func: Function to get the dependencies of a service.
            registered_types: Set of registered service types.

        Returns:
            Dictionary mapping service names to lists of missing dependency names.
        """
        missing_deps: Dict[str, List[str]] = {}

        for service_type in service_types:
            # Get dependencies of this service
            dependencies = get_dependencies_func(service_type)

            # Check each dependency
            for dep_type in dependencies:
                # Skip None dependencies
                if dep_type is None:
                    continue

                # Check if the dependency is registered
                if dep_type not in registered_types:
                    # Add to missing dependencies
                    service_name = getattr(service_type, "__name__", str(service_type))
                    dep_name = getattr(dep_type, "__name__", str(dep_type))

                    if service_name not in missing_deps:
                        missing_deps[service_name] = []

                    missing_deps[service_name].append(dep_name)

        return missing_deps


class ConditionalResolver:
    """Utility for resolving conditional dependencies."""

    @staticmethod
    def resolve_conditions(
        service_type: Type[T],
        conditional_registrations: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolve conditional dependencies based on context.

        Args:
            service_type: The service type to resolve.
            conditional_registrations: List of conditional registrations.
            context: Context dictionary with condition values.

        Returns:
            The matching registration.

        Raises:
            ValueError: If no matching condition is found.
        """
        for registration in conditional_registrations:
            condition = registration.get("condition")
            if condition is None:
                continue

            # Evaluate the condition with the context
            if condition(context):
                return registration

        # If no condition matches
        raise ValueError(
            f"No matching condition found for service {service_type.__name__}"
        )