# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 636b489c-1816-49a6-8a85-6cbcdff1abf8
# name: protocol_file_io.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:53.805393
# last_modified_at: 2025-05-19T16:19:53.805400
# description: Stamped Python file: protocol_file_io.py
# state_contract: none
# lifecycle: active
# hash: c543bb6d902d9f1d39537f9ffe38d65976871a624474e1207777dd1a9b182ea3
# entrypoint: {'type': 'python', 'target': 'protocol_file_io.py'}
# namespace: onex.stamped.protocol_file_io.py
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
