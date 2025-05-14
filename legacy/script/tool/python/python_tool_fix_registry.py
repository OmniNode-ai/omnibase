# DEPRECATED: Use ToolRegistry (foundation.script.tool.tool_registry) for all new and refactored code. This FixerRegistry is legacy and will be removed after migration.
#
# WARNING: Do not register new fixers here. Use ToolRegistry for all tool/fixer registration and discovery.

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: fixer_registry
# namespace: omninode.tools.fixer_registry
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:53+00:00
# last_modified_at: 2025-04-27T18:12:53+00:00
# entrypoint: fixer_registry.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""
DEPRECATED: FixerRegistry is legacy. Use ToolRegistry (foundation.script.tool.tool_registry) for all new and refactored code.
This module will be removed after migration.
"""

from typing import Dict, Type


class FixerRegistry:
    _registry: Dict[str, Type] = {}

    @classmethod
    def register(cls, name: str, fixer_cls: Type, meta: dict = None):
        cls._registry[name] = fixer_cls
        if meta:
            fixer_cls._fixer_meta = meta

    @classmethod
    def get(cls, name: str):
        return cls._registry.get(name)

    @classmethod
    def list_metadata(cls):
        return [
            getattr(f, "_fixer_meta", {"name": n}) for n, f in cls._registry.items()
        ]


def register_fixer(
    name: str, version: str = "v1", description: str = "", languages=None
):
    def decorator(fixer_cls):
        FixerRegistry.register(
            name,
            fixer_cls,
            meta={
                "name": name,
                "version": version,
                "description": description,
                "languages": languages or ["python"],
            },
        )
        return fixer_cls

    return decorator
