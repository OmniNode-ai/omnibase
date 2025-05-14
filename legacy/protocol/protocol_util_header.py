from typing import Protocol, Optional, Tuple, List, runtime_checkable

@runtime_checkable
class ProtocolUtilHeader(Protocol):
    """
    Protocol for Python header normalization utilities.
    """
    def extract_shebang(self, lines: list[str]) -> tuple[Optional[str], list[str]]:
        """Extract and remove the shebang line from the given lines, if present."""
        ...

    def extract_module_docstring(self, lines: list[str]) -> tuple[Optional[str], list[str]]:
        """Extract and remove the module docstring from the given lines, if present."""
        ...

    def extract_future_imports(self, lines: list[str]) -> tuple[list[str], list[str]]:
        """Extract and remove all contiguous 'from __future__ import ...' lines at the top of the file."""
        ...

    def normalize_python_header(self, lines: list[str]) -> tuple[list[str], list[str]]:
        """Extract shebang, docstring, and future imports, returning (header_lines, rest_lines)."""
        ...

    def update_metadata_block_hash(self, text: str, hash_value: str) -> str | None:
        ... 