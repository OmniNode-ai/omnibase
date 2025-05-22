# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: mixin_block_placement.py
# version: 1.0.0
# uuid: 7984c1b7-9ff8-4c80-aa40-c12bb86bcac7
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.163791
# last_modified_at: 2025-05-21T16:42:46.073852
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: d91a403ae5369fc7a46adf0df3f5c30606bd23f60289f07946e402cce4e26ca7
# entrypoint: python@mixin_block_placement.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.mixin_block_placement
# meta_type: tool
# === /OmniNode:Metadata ===


import re
from typing import Any


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
