# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:08.213763'
# description: Stamped by PythonHandler
# entrypoint: python://mixin_block_placement
# hash: 403e69c597a44fa3f2e2e147e5ed0d2eadf0a0e23dddaacc3ff533df836da3d0
# last_modified_at: '2025-05-29T14:14:00.583835+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: mixin_block_placement.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.mixins.mixin_block_placement
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

from omnibase.metadata.metadata_constants import get_namespace_prefix
from omnibase.model.model_block_placement_policy import BlockPlacementPolicy


class BlockPlacementMixin:
    def normalize_block_placement(
        self, content: str, policy: BlockPlacementPolicy
    ) -> str:
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
