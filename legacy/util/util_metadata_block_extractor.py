# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "util_metadata_block_extractor"
# namespace: "omninode.tools.util_metadata_block_extractor"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T22:11:58+00:00"
# last_modified_at: "2025-05-05T22:11:58+00:00"
# entrypoint: "util_metadata_block_extractor.py"
# protocols_supported:
#   - "["O.N.E. v0.1"]"
# protocol_class:
#   - '['Protocol', 'ProtocolMetadataBlockExtractor']'
# base_class:
#   - '['Protocol', 'ProtocolMetadataBlockExtractor']'
# mock_safe: true
# === /OmniNode:Metadata ===

OMNINODE_METADATA_START = "=== OmniNode:Metadata ==="
OMNINODE_METADATA_END = "=== /OmniNode:Metadata ==="

from typing import Protocol, List, Optional
import re

class ProtocolMetadataBlockExtractor(Protocol):
    def extract_block(self, lines: List[str]) -> Optional[str]:
        ...

class MetadataBlockExtractor(ProtocolMetadataBlockExtractor):
    def __init__(self, start_pattern: str, end_pattern: str, line_prefix: Optional[str] = None):
        self.start_re = re.compile(start_pattern)
        self.end_re = re.compile(end_pattern)
        self.line_prefix = line_prefix

    def extract_block(self, lines: List[str]) -> Optional[str]:
        in_block = False
        block_lines = []
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if self.start_re.match(stripped):
                in_block = True
                continue
            if self.end_re.match(stripped) and in_block:
                break
            if in_block:
                if self.line_prefix and line.startswith(self.line_prefix):
                    block_lines.append(line[len(self.line_prefix):].rstrip("\n"))
                else:
                    block_lines.append(line.rstrip("\n"))
        if not block_lines:
            return None
        block = "\n".join(block_lines)
        return block