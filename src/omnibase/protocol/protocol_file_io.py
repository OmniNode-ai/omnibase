# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_file_io.py
# version: 1.0.0
# uuid: 33a1f4a1-0f64-4dc8-9d0f-93acd7ab1706
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167073
# last_modified_at: 2025-05-21T16:42:46.043562
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 99c29adee829c5b4ada67bf6139475daa157b45a91c7a5f3d2b920d0edf234fd
# entrypoint: {'type': 'python', 'target': 'protocol_file_io.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_file_io
# meta_type: tool
# === /OmniNode:Metadata ===

"""
Protocol for file I/O operations (read/write YAML/JSON, list files, check existence).
Enables in-memory/mock implementations for protocol-first stamping tests.
"""

from pathlib import Path
from typing import Any, List, Optional, Protocol, Union


class ProtocolFileIO(Protocol):
    """
    Protocol for file I/O operations (YAML/JSON/text) for stamping/validation tools.
    """

    def read_yaml(self, path: Union[str, Path]) -> Any:
        """Read YAML content from a file path."""
        ...

    def read_json(self, path: Union[str, Path]) -> Any:
        """Read JSON content from a file path."""
        ...

    def write_yaml(self, path: Union[str, Path], data: Any) -> None:
        """Write YAML content to a file path."""
        ...

    def write_json(self, path: Union[str, Path], data: Any) -> None:
        """Write JSON content to a file path."""
        ...

    def exists(self, path: Union[str, Path]) -> bool:
        """Check if a file exists."""
        ...

    def is_file(self, path: Union[str, Path]) -> bool:
        """Check if a path is a file."""
        ...

    def list_files(
        self, directory: Union[str, Path], pattern: Optional[str] = None
    ) -> List[Path]:
        """List files in a directory, optionally filtered by pattern."""
        ...
