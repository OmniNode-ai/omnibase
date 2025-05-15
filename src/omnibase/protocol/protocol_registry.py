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
# protocol_class: ['ProtocolRegistry']
# base_class: ['ProtocolRegistry']
# mock_safe: true
# === /OmniNode:Metadata ===

"""
ProtocolRegistry: Canonical ONEX protocol for schema and node registries.

- This protocol supersedes any prior 'RegistryProtocol' or generic 'ProtocolRegistry' definitions.
- Loader methods are classmethods (using cls), as required by ONEX canonical templates and docs.
- get_node returns a dict for M0 (see node_contracts.md and milestone 0 checklist); M1+ should migrate to returning a Pydantic model.
- See docs/nodes/protocol_definitions.md and templates_scaffolding.md for rationale and usage.
"""
from typing import Protocol, Type, TypeVar, Dict, Any

class ProtocolRegistry(Protocol):
    """
    Protocol for schema and node registries in ONEX.

    Loader methods are classmethods. For M0, get_node returns a dict; for M1+, migrate to a Pydantic model.

    Example:
        class SchemaRegistry:
            @classmethod
            def load_from_disk(cls) -> 'ProtocolRegistry':
                ...
            @classmethod
            def load_mock(cls) -> 'ProtocolRegistry':
                ...
            def get_node(self, node_id: str) -> dict:
                ...
    """
    @classmethod
    def load_from_disk(cls) -> 'ProtocolRegistry':
        ...
    @classmethod
    def load_mock(cls) -> 'ProtocolRegistry':
        ...
    def get_node(self, node_id: str) -> dict:
        ... 