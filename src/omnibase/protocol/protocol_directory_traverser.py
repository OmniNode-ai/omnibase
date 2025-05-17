"""
Protocol for directory traversal operations.
Defines a standardized interface for discovering and filtering files in directories.
"""

from pathlib import Path
from typing import Callable, List, Optional, Protocol, Set, TypeVar, Union

from omnibase.model.model_onex_message_result import OnexResultModel

T = TypeVar("T")  # Generic type variable for processor result

# === OmniNode:Metadata ===
metadata_version = "0.1"
name = "protocol_directory_traverser"
namespace = "foundation.protocol"
version = "0.1.0"
type = "protocol"
entrypoint = "protocol_directory_traverser.py"
owner = "foundation-team"
# === /OmniNode:Metadata ===


class ProtocolDirectoryTraverser(Protocol):
    """
    Protocol for directory traversal with filtering capabilities.

    This protocol defines a standard interface for directory traversal operations,
    including file discovery, filtering, and processing. It is designed to be
    reusable across multiple tools that need to walk directory trees.

    Example implementation:
    ```python
    class DirectoryTraverser:
        def find_files(self, directory: Path, include_patterns: List[str],
                      exclude_patterns: List[str], recursive: bool) -> Set[Path]:
            # Implementation
            ...
    ```
    """

    def find_files(
        self,
        directory: Path,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        recursive: bool = True,
        ignore_file: Optional[Path] = None,
    ) -> Set[Path]:
        """
        Find all files matching the given patterns in the directory.

        Args:
            directory: Directory to search
            include_patterns: List of glob patterns to include (e.g., ['**/*.yaml'])
            exclude_patterns: List of glob patterns to exclude (e.g., ['**/.git/**'])
            recursive: Whether to recursively traverse subdirectories
            ignore_file: Path to ignore file (e.g., .stamperignore)

        Returns:
            Set of Path objects for matching files
        """
        ...

    def load_ignore_patterns(self, ignore_file: Optional[Path] = None) -> List[str]:
        """
        Load ignore patterns from a file.

        Args:
            ignore_file: Path to ignore file. If None, will try to find in standard locations.

        Returns:
            List of ignore patterns as strings
        """
        ...

    def should_ignore(self, path: Path, ignore_patterns: List[str]) -> bool:
        """
        Check if a file should be ignored based on patterns.

        Args:
            path: Path to check
            ignore_patterns: List of ignore patterns

        Returns:
            True if the file should be ignored, False otherwise
        """
        ...

    def process_directory(
        self,
        directory: Path,
        processor: Callable[[Path], T],
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        recursive: bool = True,
        ignore_file: Optional[Path] = None,
        dry_run: bool = False,
        max_file_size: Optional[int] = None,
    ) -> Union[OnexResultModel, List[T]]:
        """
        Process all eligible files in a directory using the provided processor function.

        Args:
            directory: Directory to process
            processor: Callable that processes each file and returns a result
            include_patterns: List of glob patterns to include
            exclude_patterns: List of glob patterns to exclude
            recursive: Whether to recursively traverse subdirectories
            ignore_file: Path to ignore file
            dry_run: Whether to perform a dry run (don't modify files)
            max_file_size: Maximum file size in bytes to process

        Returns:
            OnexResultModel with aggregate results or list of processor results
        """
        ...
