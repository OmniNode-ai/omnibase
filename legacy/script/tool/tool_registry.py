# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "tool_registry"
# namespace: "omninode.tools.tool_registry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:01+00:00"
# last_modified_at: "2025-05-05T12:44:01+00:00"
# entrypoint: "tool_registry.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Metadata ===

"""
Central registry for all OmniNode tools (fixers, stampers, etc.).
Follows the ValidatorRegistry pattern for registration and discovery.
"""
from threading import RLock
from typing import Any, Dict, List, Optional, Type
from foundation.template.metadata.metadata_template_registry import MetadataRegistryTemplate
from foundation.registry.utility_registry import get_util

class ToolRegistry:
    """
    Registry for tool classes. Provides registration, lookup, and metadata listing.
    """
    def __init__(self):
        self._tools = {}  # type: Dict[str, Dict[str, type]]
        self._metadata = {}  # type: Dict[str, Dict[str, dict]]

    def register(self, name: str, tool_cls: type, meta: dict) -> None:
        version = meta.get("version", "v1")
        if name not in self._tools:
            self._tools[name] = {}
            self._metadata[name] = {}
        self._tools[name][version] = tool_cls
        self._metadata[name][version] = meta

    def get_tool(self, name: str) -> Optional[type]:
        if name not in self._tools:
            return None
        versions = list(self._tools[name].keys())
        if not versions:
            return None
        latest = max(versions)
        return self._tools[name][latest]

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def get_all_metadata(self) -> Dict[str, dict]:
        result = {}
        for name, versions in self._metadata.items():
            latest_version = max(versions.keys())
            meta = versions[latest_version]
            result[name] = meta
        return result


def populate_tool_registry(registry: ToolRegistry, template_registry: MetadataRegistryTemplate):
    """Register all known tools with the provided registry instance."""
    try:
        from foundation.script.metadata.metadata_stamper import MetadataStamper
        from foundation.registry.registry_metadata_block_hash import RegistryMetadataBlockHash
        registry.register(
            name="metadata_stamper",
            tool_cls=lambda logger, **kwargs: MetadataStamper(logger, template_registry, RegistryMetadataBlockHash(), header_util=kwargs.get('header_util', get_util('header'))),
            meta={
                "name": "metadata_stamper",
                "version": "0.1.0",
                "description": "OmniNode Metadata Stamper Tool (inserts/repairs metadata blocks in source files)",
                "entrypoint": "foundation.script.metadata.metadata_stamper",
                "type": "tool",
                "namespace": "omninode.tools.metadata_stamper",
                "protocols_supported": ["O.N.E. v0.1"],
                "author": "OmniNode Team",
                "owner": "jonah@omninode.ai",
            },
        )
        assert registry.get_tool("metadata_stamper") is not None, "MetadataStamper not registered in tool_registry!"
    except ImportError:
        pass

    try:
        from foundation.script.tool.struct.struct_index import StructIndex
        registry.register(
            name="struct_index",
            tool_cls=StructIndex,
            meta={
                "name": "struct_index",
                "version": "0.1.0",
                "description": "Canonical directory tree indexer for OmniNode. Generates .tree, .tree.yaml, and .tree.flat files with ignore support.",
                "entrypoint": "foundation.script.tool.struct.struct_index",
                "type": "tool",
                "namespace": "omninode.tools.struct_index",
                "protocols_supported": ["O.N.E. v0.1"],
                "author": "OmniNode Team",
                "owner": "jonah@omninode.ai",
            },
        )
        assert registry.get_tool("struct_index") is not None, "StructIndex not registered in tool_registry!"
    except ImportError:
        pass 