# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "di_interfaces"
# namespace: "omninode.tools.di_interfaces"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:13+00:00"
# last_modified_at: "2025-05-05T13:00:13+00:00"
# entrypoint: "di_interfaces.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Interface and Protocol support for the dependency injection container.

This module provides helper classes to resolve dependencies based on abstract base classes
(interfaces) and protocols.
"""

import inspect
from typing import Protocol, Type, TypeVar

T = TypeVar("T")


class InterfaceResolver:
    """Helper class for resolving dependencies based on abstract base classes (interfaces)."""

    @staticmethod
    def is_abstract_base_class(cls: Type) -> bool:
        """Check if a class is an abstract base class (interface).

        Args:
            cls: The class to check.

        Returns:
            True if the class is an abstract base class, False otherwise.
        """
        return (
            inspect.isclass(cls)
            and hasattr(cls, "__abstractmethods__")
            and len(cls.__abstractmethods__) > 0
        )

    @staticmethod
    def is_implementation_of(impl_cls: Type, interface_cls: Type) -> bool:
        """Check if a class is an implementation of an interface.

        Args:
            impl_cls: The implementation class to check.
            interface_cls: The interface class to check against.

        Returns:
            True if the implementation class implements the interface, False otherwise.
        """
        if not InterfaceResolver.is_abstract_base_class(interface_cls):
            return False

        # Check if impl_cls is a subclass of interface_cls
        return issubclass(impl_cls, interface_cls)


class ProtocolResolver:
    """Helper class for resolving dependencies based on protocols."""

    @staticmethod
    def is_protocol(cls: Type) -> bool:
        """Check if a class is a Protocol.

        Args:
            cls: The class to check.

        Returns:
            True if the class is a Protocol, False otherwise.
        """
        return (
            inspect.isclass(cls)
            and issubclass(cls, Protocol)
            and getattr(cls, "_is_protocol", False)
        )

    @staticmethod
    def is_implementation_of(impl_cls: Type, protocol_cls: Type) -> bool:
        """Check if a class is an implementation of a Protocol.

        Args:
            impl_cls: The implementation class to check.
            protocol_cls: The Protocol class to check against.

        Returns:
            True if the implementation class implements the Protocol, False otherwise.
        """
        if not ProtocolResolver.is_protocol(protocol_cls):
            return False

        # Check if the protocol is runtime checkable
        if (
            hasattr(protocol_cls, "_is_runtime_protocol")
            and protocol_cls._is_runtime_protocol
        ):
            # For runtime checkable protocols, create an instance to check
            try:
                instance = impl_cls()
                return isinstance(instance, protocol_cls)
            except Exception:
                # Fall back to checking method signatures
                pass

        # Check if all required methods/properties exist in the implementation
        required_attrs = []
        for attr_name, attr in inspect.getmembers(protocol_cls):
            # Skip private attributes and dunder methods
            if attr_name.startswith("_") and attr_name != "__call__":
                continue

            required_attrs.append(attr_name)

        for attr_name in required_attrs:
            if not hasattr(impl_cls, attr_name):
                return False

            # Check if method in implementation is callable if it's callable in the protocol
            protocol_attr = getattr(protocol_cls, attr_name)
            impl_attr = getattr(impl_cls, attr_name)

            if callable(protocol_attr) and not callable(impl_attr):
                return False

        return True