# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_file_io.py
# version: 1.0.0
# uuid: 64d0d493-7733-41cc-8abd-2b0be47e0e10
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.159379
# last_modified_at: 2025-05-28T17:20:04.535842
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 11ecb0d77bd627b42e2e1f636a4a7f7aae2ab95e580c0ba902c1a586f9b4107a
# entrypoint: python@protocol_file_io.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_file_io
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

    def read_text(self, path: Union[str, Path]) -> str:
        """Read plain text content from a file path."""
        ...

    def write_text(self, path: Union[str, Path], data: str) -> None:
        """Write plain text content to a file path."""
        ...

    def read_bytes(self, path: Union[str, Path]) -> bytes:
        """Read binary content from a file path."""
        ...

    def write_bytes(self, path: Union[str, Path], data: bytes) -> None:
        """Write binary content to a file path."""
        ...
