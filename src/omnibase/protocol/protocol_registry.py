# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "protocol_registry"
# namespace: "omninode.tools.protocol_registry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "protocol_registry.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Protocol']
# base_class: ['Protocol']
# mock_safe: true
# === /OmniNode:Metadata ===





"""
Protocol for all registries (utility, fixture, validator, tool, etc.).
Defines standard methods: register, get, list.
"""
from typing import Protocol, TypeVar, Generic, List, Optional
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class RegistryProtocol(Generic[T], Protocol):
    def register(self, name: str, obj: T) -> None:
        ...
    def get(self, name: str) -> Optional[T]:
        ...
    def list(self) -> List[str]:
        ...

class ProtocolRegistry(Protocol):
    """
    Protocol for schema and node registries in ONEX.

    Example:
        class MyRegistry:
            def load_from_disk(self) -> 'ProtocolRegistry':
                ...
            def load_mock(self) -> 'ProtocolRegistry':
                ...
            def get_node(self, node_id: str) -> BaseModel:
                ...
    """
    def load_from_disk(self) -> 'ProtocolRegistry':
        ...
    def load_mock(self) -> 'ProtocolRegistry':
        ...
    def get_node(self, node_id: str) -> BaseModel:
        ... 