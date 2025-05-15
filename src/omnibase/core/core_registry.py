# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "base_registry"
# namespace: "omninode.tools.base_registry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "base_registry.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolRegistry']
# base_class: ['ProtocolRegistry']
# mock_safe: true
# === /OmniNode:Metadata ===



"""
BaseRegistry implements ProtocolRegistry for all registries.
Supports register, get, list, and subscript access.
"""
from typing import Any, Optional, List, Dict
from omnibase.protocol.protocol_registry import ProtocolRegistry

# M0 milestone: This file will be replaced by SchemaRegistry stub implementing ProtocolRegistry with loader methods and get_node.
# Remove legacy/unused methods and prepare for SchemaRegistry implementation as per milestone 0 checklist.

class BaseRegistry(ProtocolRegistry):
    def __init__(self):
        self._registry: Dict[str, Any] = {}

    def register(self, name: str, obj: Any) -> None:
        self._registry[name] = obj

    def get(self, name: str) -> Optional[Any]:
        return self._registry.get(name)

    def list(self) -> List[str]:
        return list(self._registry.keys())

    def __getitem__(self, name: str) -> Any:
        return self._registry[name]

    def __contains__(self, name: str) -> bool:
        return name in self._registry 

class SchemaRegistry(ProtocolRegistry):
    """
    M0 stub implementation of ProtocolRegistry for schema/node registries.
    Implements loader methods and get_node as per milestone 0 checklist and canonical template.
    """
    def __init__(self):
        self._schemas = {}  # Placeholder for schema storage

    @classmethod
    def load_from_disk(cls) -> 'ProtocolRegistry':
        # Stub: Placeholder for M1 schema loading logic
        print("Stub: Loading schemas from disk")
        instance = cls()
        # In M0, load the minimal onex_node.yaml and state_contract.json stubs
        # In M1+, load all schemas and register them
        return instance

    @classmethod
    def load_mock(cls) -> 'ProtocolRegistry':
        # Stub: Placeholder for M1 mock schema loading logic
        print("Stub: Loading mock schemas")
        instance = cls()
        # In M0, add minimal stub data or loaded stub schemas
        return instance

    def get_node(self, node_id: str) -> dict:
        # Stub: Placeholder for M1 node lookup logic
        print(f"Stub: Getting node {node_id}")
        # In M0, return a minimal stub dict that allows tests to pass basic assertions
        # Include placeholders for key fields the validator stub will read
        return {
            "name": node_id,
            "stub": True,
            "schema_version": "0.1.0",  # Include key fields from the spec
            "uuid": "stub-uuid-123",
            "meta_type": "tool",
            "entrypoint": {"type": "python", "target": "stub.py"},
            "state_contract": "stub://contract.json",
            "dependencies": [],
            "base_class": [],
            # Include placeholders for optional/future fields the validator stub expects
            "reducer": None,
            "cache": None,
            "performance": None,
            "trust": None,
            "x-extensions": {},
            "protocols_supported": [],
            "environment": [],
            "license": "stub",
        } 