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
