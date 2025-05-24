# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: core_registry.py
# version: 1.0.0
# uuid: f62f7393-2440-486d-8b80-81d8af8f032b
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.163499
# last_modified_at: 2025-05-21T16:42:46.069610
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: f8011b18d84557fb846a6d84a76c38d6f50e0c45723315acd0b93e4df900a7eb
# entrypoint: python@core_registry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.core_registry
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Core Registry Classes.

BaseRegistry implements ProtocolRegistry for all registries.
Supports register, get, list, and subscript access.

Migration Status:
- ✅ Registry loading logic migrated to registry_loader_node
- ✅ SchemaRegistry removed (replaced by RegistryBridge)
- ✅ FileTypeRegistry removed (moved to runtime/handlers)
- ✅ OnexRegistryLoader removed (replaced by registry loader node)

See: src/omnibase/nodes/registry_loader_node/v1_0_0/README.md for migration details.
"""

from typing import Any, List, Optional

from omnibase.protocol.protocol_registry import ProtocolRegistry


class BaseRegistry(ProtocolRegistry):
    """
    Base registry implementation that provides basic registry functionality.

    Supports register, get, list, and subscript access patterns.
    """

    def __init__(self) -> None:
        self._registry: dict[str, Any] = {}

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
