# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: core_node_cli_adapter_registry.py
# version: 1.0.0
# uuid: ea176fc1-4c87-4902-b984-a9f344277974
# author: OmniNode Team
# created_at: 2025-05-23T10:29:04.625488
# last_modified_at: 2025-05-23T17:42:52.030520
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 5c4d563ac73d9ac760e4d5b2ad2a3e4688657dd957eecf910380255f00d98a38
# entrypoint: python@core_node_cli_adapter_registry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.core_node_cli_adapter_registry
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Any, Dict


class NodeCliAdapterRegistry:
    """
    Registry for ONEX node CLI adapters. Allows registration and retrieval by node name.
    """

    def __init__(self) -> None:
        self._adapters: Dict[str, Any] = {}

    def register(self, node_name: str, adapter: Any) -> None:
        self._adapters[node_name] = adapter

    def get(self, node_name: str) -> Any:
        return self._adapters.get(node_name)

    def list(self) -> list[str]:
        return list(self._adapters.keys())
