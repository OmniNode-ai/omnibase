# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.213763'
# description: Stamped by PythonHandler
# entrypoint: python://mixin_block_placement.py
# hash: e3df2f75193710edce7d7f77f016e887a0810289d46bba1ad6657b3d8d506fd6
# last_modified_at: '2025-05-29T11:50:12.329447+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: mixin_block_placement.py
# namespace: omnibase.mixin_block_placement
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: a3e3df24-242b-4602-a1cf-1d747c64730a
# version: 1.0.0
# === /OmniNode:Metadata ===


import re
from typing import Any
from omnibase.metadata.metadata_constants import get_namespace_prefix


class BlockPlacementMixin:
    def normalize_block_placement(self, content: str, policy: Any) -> str:
        lines = content.splitlines(keepends=True)
        shebang = None
        start = 0
        if policy.allow_shebang and lines and lines[0].startswith("#!"):
            shebang = lines[0]
            start = 1
        open_delim = getattr(policy, "open_delim", None)
        close_delim = getattr(policy, "close_delim", None)
        block_start = None
        block_end = None
        for i, line in enumerate(lines[start:], start):
            if open_delim and line.lstrip().startswith(open_delim):
                block_start = i
                break
        if block_start is not None:
            for j in range(block_start, len(lines)):
                if close_delim and lines[j].lstrip().startswith(close_delim):
                    block_end = j
                    break
        if block_start is not None and block_end is not None:
            block_lines = lines[block_start : block_end + 1]
            after_block = lines[block_end + 1 :]
            block_lines = [re.sub(r"^[ \t]+", "", line) for line in block_lines]
            normalized = []
            if shebang:
                normalized.append(shebang)
            normalized.append("\n")
            normalized.extend(block_lines)
            after_block = list(after_block)
            while after_block and after_block[0].strip() == "":
                after_block.pop(0)
            normalized.extend(after_block)
            return "".join(normalized)
        else:
            normalized = []
            if shebang:
                normalized.append(shebang)
            normalized.append("\n")
            normalized.extend(lines[start:])
            return "".join(normalized)
