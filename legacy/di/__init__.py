# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "__init__"
# namespace: "omninode.tools.__init__"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:13+00:00"
# last_modified_at: "2025-05-05T13:00:13+00:00"
# entrypoint: "__init__.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
Dependency Injection module for the foundation service.

This module provides a comprehensive dependency injection system based on the Punq library,
with additional features such as interface registration, protocol support, service lifetime management,
conditional resolution, and more.
"""

from foundation.di.di_advanced import (
    CircularDependencyError,
    ConditionalResolver,
    DependencyValidationError,
    DependencyValidator,
)
from foundation.di.di_container import DIContainer, ServiceLifetime
from foundation.di.di_interfaces import InterfaceResolver, ProtocolResolver
from foundation.di.di_management import (
    AsyncScopedContainer,
    ChildContainer,
    ContainerMiddleware,
    ContainerSnapshot,
    DIContainerFactory,
    ScopedContainer,
)

__all__ = [
    "DIContainer",
    "ServiceLifetime",
    "CircularDependencyError",
    "ConditionalResolver",
    "DependencyValidationError",
    "DependencyValidator",
    "InterfaceResolver",
    "ProtocolResolver",
    "ScopedContainer",
    "AsyncScopedContainer",
    "ChildContainer",
    "ContainerSnapshot",
    "ContainerMiddleware",
    "DIContainerFactory",
]