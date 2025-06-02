# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:07.837430'
# description: Stamped by PythonHandler
# entrypoint: python://block_placement_mixin
# hash: 220efaf0e24ab16261a6d77138dd0a0d7aaa31c1ec019f5b2f3184f26a639ada
# last_modified_at: '2025-05-29T14:13:58.655617+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: block_placement_mixin.py
# namespace: python://omnibase.handlers.block_placement_mixin
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 62d1d95d-9a5a-4ea1-8e76-70f36611da78
# version: 1.0.0
# === /OmniNode:Metadata ===


import re
from omnibase.model.model_block_placement_policy import BlockPlacementPolicy


class BlockPlacementMixin:
    def normalize_block_placement(self, content: str, policy: BlockPlacementPolicy) -> str:
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
