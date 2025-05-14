# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "util_chunk_metrics"
# namespace: "omninode.tools.util_chunk_metrics"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T17:01:20+00:00"
# last_modified_at: "2025-05-05T17:01:20+00:00"
# entrypoint: "util_chunk_metrics.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ChunkMetricsProtocol', 'Protocol']
# base_class: ['ChunkMetricsProtocol', 'Protocol']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from typing import Protocol, Optional, Any

class ChunkMetricsProtocol(Protocol):
    def count_lines(self, file_path: str) -> int:
        ...
    def count_tokens(self, content: str, tokenizer: Optional[Any] = None) -> int:
        ...
    def read_file(self, file_path: str) -> str:
        ...

class UtilChunkMetrics(ChunkMetricsProtocol):
    @staticmethod
    def count_lines(file_path: str) -> int:
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)

    @staticmethod
    def count_tokens(content: str, tokenizer: Optional[Any] = None) -> int:
        if tokenizer:
            return len(tokenizer.encode(content))
        return len(content) // 4

    @staticmethod
    def read_file(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read() 