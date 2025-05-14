
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
from typing import Protocol, Any, Optional, List

class RegistryProtocol(Protocol):
    def register(self, name: str, obj: Any) -> None:
        ...
    def get(self, name: str) -> Optional[Any]:
        ...
    def list(self) -> List[str]:
        ... 