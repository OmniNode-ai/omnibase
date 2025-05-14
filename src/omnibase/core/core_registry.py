
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
# protocol_class: ['RegistryProtocol']
# base_class: ['RegistryProtocol']
# mock_safe: true
# === /OmniNode:Metadata ===



"""
BaseRegistry implements RegistryProtocol for all registries.
Supports register, get, list, and subscript access.
"""
from typing import Any, Optional, List, Dict
from foundation.protocol.protocol_registry import RegistryProtocol

class BaseRegistry(RegistryProtocol):
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