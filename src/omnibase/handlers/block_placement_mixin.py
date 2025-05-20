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
