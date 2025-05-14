
# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "parent_registry"
# namespace: "omninode.tools.parent_registry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "parent_registry.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['RegistryProtocol']
# base_class: ['RegistryProtocol']
# mock_safe: true
# === /OmniNode:Metadata ===



"""
ParentRegistry aggregates sub-registries and provides unified registration, lookup, and listing.
"""
from typing import Any, Optional, List, Dict
from foundation.protocol.protocol_registry import RegistryProtocol

class ParentRegistry(RegistryProtocol):
    def __init__(self):
        self._registries: Dict[str, RegistryProtocol] = {}

    def add_registry(self, name: str, registry: RegistryProtocol):
        self._registries[name] = registry

    def register(self, registry_name: str, name: str, obj: Any) -> None:
        self._registries[registry_name].register(name, obj)

    def get(self, registry_name: str, name: str) -> Optional[Any]:
        return self._registries[registry_name].get(name)

    def list(self, registry_name: Optional[str] = None) -> List[str]:
        if registry_name:
            return self._registries[registry_name].list()
        all_items = []
        for reg in self._registries.values():
            all_items.extend(reg.list())
        return all_items

    def all_items(self) -> Dict[str, List[str]]:
        return {name: reg.list() for name, reg in self._registries.items()}

# Example usage:
# from foundation.registry.utility_registry import utility_registry
# parent_registry = ParentRegistry()
# parent_registry.add_registry('utility', utility_registry) 