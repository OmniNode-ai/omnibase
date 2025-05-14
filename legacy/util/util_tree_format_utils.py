# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "util_tree_format_utils"
# namespace: "omninode.tools.util_tree_format_utils"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:30+00:00"
# last_modified_at: "2025-05-05T13:00:30+00:00"
# entrypoint: "util_tree_format_utils.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Protocol', 'TreeFormatUtilsProtocol']
# base_class: ['Protocol', 'TreeFormatUtilsProtocol']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from typing import Protocol, Any, List

class TreeFormatUtilsProtocol(Protocol):
    def tree_to_text(self, node: Any, prefix: str = "") -> str:
        ...
    def tree_to_flat(self, node: Any, base: str = "") -> List[str]:
        ...

class UtilTreeFormatUtils(TreeFormatUtilsProtocol):
    @staticmethod
    def tree_to_text(node: Any, prefix: str = "") -> str:
        lines = []
        lines.append(f"{prefix}{node.name}/" if getattr(node, 'type', None) == "directory" else f"{prefix}{node.name}")
        if getattr(node, 'children', None):
            for child in node.children:
                lines.append(UtilTreeFormatUtils.tree_to_text(child, prefix + "  "))
        return "\n".join(lines)

    @staticmethod
    def tree_to_flat(node: Any, base: str = "") -> List[str]:
        import os
        paths = []
        path = os.path.join(base, node.name)
        if getattr(node, 'type', None) == "file":
            paths.append(path)
        elif getattr(node, 'children', None):
            for child in node.children:
                paths.extend(UtilTreeFormatUtils.tree_to_flat(child, path))
        return paths 