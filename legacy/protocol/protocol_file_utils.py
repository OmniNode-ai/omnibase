# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "protocol_file_utils"
# namespace: "omninode.tools.protocol_file_utils"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:01+00:00"
# last_modified_at: "2025-05-05T12:44:01+00:00"
# entrypoint: "protocol_file_utils.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Protocol']
# base_class: ['Protocol']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from typing import Protocol, Set
from pathlib import Path

class ProtocolFileUtils(Protocol):
    def check_file_extension(self, path: Path, valid_exts: Set[str]) -> bool:
        """Return True if the file has a valid extension."""
        ...
    def file_exists(self, path: Path) -> bool:
        """Return True if the file exists and is a file."""
        ...
    def read_file(self, path: Path) -> str:
        """Read and return the contents of the file as a string."""
        ... 