"""
Directory traversal utility for finding and processing files in directories.
"""

import fnmatch
import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, TypeVar, Union

# Try to import pathspec for better glob pattern matching
try:
    import pathspec
except ImportError:
    pathspec = None

from omnibase.model.model_enum_ignore_pattern_source import (
    IgnorePatternSourceEnum,
    TraversalModeEnum,
)
from omnibase.model.model_file_filter import (
    DirectoryProcessingResultModel,
    FileFilterModel,
)
from omnibase.model.model_onex_message_result import (
    OnexMessageModel,
    OnexResultModel,
    OnexStatus,
)
from omnibase.protocol.protocol_directory_traverser import ProtocolDirectoryTraverser
from omnibase.protocol.protocol_file_discovery_source import ProtocolFileDiscoverySource

# === OmniNode:Metadata ===
metadata_version = "0.1"
name = "directory_traverser"
namespace = "foundation.utils"
version = "0.1.0"
type = "utility"
entrypoint = "directory_traverser.py"
owner = "foundation-team"
# === /OmniNode:Metadata ===

logger = logging.getLogger(__name__)
T = TypeVar("T")  # Generic type variable for processor result


class DirectoryTraverser(ProtocolDirectoryTraverser, ProtocolFileDiscoverySource):
    """
    Generic directory traversal implementation with filtering capabilities.
    
    This class implements the ProtocolDirectoryTraverser interface for finding,
    filtering, and processing files in directories. It provides flexible
    pattern matching and error handling.
    """

    # Default file patterns to match when traversing directories
    DEFAULT_INCLUDE_PATTERNS = ["**/*.yaml", "**/*.yml", "**/*.json"]
    
    # Default directories to ignore when traversing
    DEFAULT_IGNORE_DIRS = [
        ".git", ".github", "__pycache__", 
        ".ruff_cache", ".pytest_cache", 
        ".venv", "venv", "node_modules"
    ]

    def __init__(self):
        """Initialize the directory traverser."""
        self.result = DirectoryProcessingResultModel()

    def reset_counters(self):
        """Reset file counters."""
        self.result = DirectoryProcessingResultModel()

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
        filter_config = FileFilterModel(
            traversal_mode=TraversalModeEnum.RECURSIVE if recursive else TraversalModeEnum.FLAT,
            include_patterns=include_patterns or self.DEFAULT_INCLUDE_PATTERNS,
            exclude_patterns=exclude_patterns or [],
            ignore_file=ignore_file,
            ignore_pattern_sources=[IgnorePatternSourceEnum.FILE, IgnorePatternSourceEnum.DEFAULT],
        )
        
        return self._find_files_with_config(directory, filter_config)

    def _find_files_with_config(
        self, 
        directory: Path, 
        filter_config: FileFilterModel
    ) -> Set[Path]:
        """
        Find all files matching filter criteria in the directory.
        
        Args:
            directory: Directory to search
            filter_config: Configuration for filtering files
            
        Returns:
            Set of Path objects for matching files
        """
        if not directory.exists() or not directory.is_dir():
            return set()
            
        # Reset counters for a new operation
        self.reset_counters()
        self.result.directory = directory
        self.result.filter_config = filter_config
            
        # Determine if operation is recursive
        recursive = filter_config.traversal_mode in [
            TraversalModeEnum.RECURSIVE, 
            TraversalModeEnum.SHALLOW
        ]
        
        # Load ignore patterns from all configured sources
        ignore_patterns = self._load_ignore_patterns_from_sources(
            filter_config.ignore_pattern_sources,
            filter_config.ignore_file
        )
        
        # Add exclude patterns to ignore patterns
        if filter_config.exclude_patterns:
            ignore_patterns.extend(filter_config.exclude_patterns)
            
        # Get all files matching the include patterns
        all_files: Set[Path] = set()
        for pattern in filter_config.include_patterns:
            # Handle both glob patterns and explicit extensions
            if pattern.startswith("*."):
                # It's an extension pattern
                ext = pattern[1:]  # Remove the *
                if recursive:
                    all_files.update(directory.glob(f"**/*{ext}"))
                else:
                    all_files.update(directory.glob(f"*{ext}"))
            elif "**" in pattern and recursive:
                # It's a recursive glob pattern and recursive is enabled
                all_files.update(directory.glob(pattern))
            elif "*" in pattern:
                # It's a non-recursive glob pattern or recursive is disabled
                # Convert **/ to */ if needed for non-recursive mode
                if not recursive and "**/" in pattern:
                    pattern = pattern.replace("**/", "*/")
                all_files.update(directory.glob(pattern))
            else:
                # It's a literal path
                path = directory / pattern
                if path.exists():
                    all_files.add(path)
        
        # Filter out ignored files
        eligible_files = set()
        for file_path in all_files:
            if not file_path.is_file():
                continue
                
            # Skip files not in the specified directory when in FLAT mode
            if filter_config.traversal_mode == TraversalModeEnum.FLAT and file_path.parent != directory:
                self.result.skipped_count += 1
                self.result.skipped_files.add(file_path)
                continue
                
            # Skip files in non-immediate subdirectories in SHALLOW mode
            if (filter_config.traversal_mode == TraversalModeEnum.SHALLOW and 
                file_path.parent != directory and 
                file_path.parent.parent != directory):
                self.result.skipped_count += 1
                self.result.skipped_files.add(file_path)
                continue
                
            # Skip files matching ignore patterns
            if self.should_ignore(file_path, ignore_patterns):
                self.result.skipped_count += 1
                self.result.skipped_files.add(file_path)
                continue
            
            # Skip files exceeding max size
            if filter_config.max_file_size > 0:
                try:
                    file_size = file_path.stat().st_size
                    if file_size > filter_config.max_file_size:
                        logger.debug(f"Skipping file exceeding size limit: {file_path} ({file_size} bytes)")
                        self.result.skipped_count += 1
                        self.result.skipped_files.add(file_path)
                        continue
                except OSError as e:
                    logger.warning(f"Error checking file size: {file_path}: {e}")
                    self.result.skipped_count += 1
                    self.result.skipped_files.add(file_path)
                    continue
            
            # Apply max_files limit if specified
            if (filter_config.max_files is not None and 
                len(eligible_files) >= filter_config.max_files):
                logger.debug(f"Reached maximum file limit: {filter_config.max_files}")
                self.result.skipped_count += 1
                self.result.skipped_files.add(file_path)
                continue
                
            eligible_files.add(file_path)
            
        return eligible_files

    def _load_ignore_patterns_from_sources(
        self,
        sources: List[IgnorePatternSourceEnum],
        ignore_file: Optional[Path] = None
    ) -> List[str]:
        """
        Load ignore patterns from multiple sources.
        
        Args:
            sources: List of sources to check for ignore patterns
            ignore_file: Path to specific ignore file
            
        Returns:
            List of ignore patterns
        """
        patterns = []
        
        # Load from file if specified
        if IgnorePatternSourceEnum.FILE in sources:
            patterns.extend(self.load_ignore_patterns(ignore_file))
            
        # Load default directory patterns
        if IgnorePatternSourceEnum.DEFAULT in sources or IgnorePatternSourceEnum.DIRECTORY in sources:
            patterns.extend([f"{d}/" for d in self.DEFAULT_IGNORE_DIRS])
            
        return patterns

    def load_ignore_patterns(
        self, 
        ignore_file: Optional[Path] = None
    ) -> List[str]:
        """
        Load ignore patterns from a file.
        
        Args:
            ignore_file: Path to ignore file. If None, will try to find in standard locations.
            
        Returns:
            List of ignore patterns as strings
        """
        if ignore_file is None:
            # Try to find .stamperignore in current directory
            ignore_file = Path(".stamperignore")
            if not ignore_file.exists():
                # Try repository root
                repo_root = Path.cwd()
                while repo_root != repo_root.parent:
                    candidate = repo_root / ".stamperignore"
                    if candidate.exists():
                        ignore_file = candidate
                        break
                    if (repo_root / ".git").exists():
                        break
                    repo_root = repo_root.parent
        
        if ignore_file and ignore_file.exists():
            logger.info(f"Loading ignore patterns from {ignore_file}")
            with open(ignore_file, "r") as f:
                patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith("#")
                ]
            return patterns
        
        # Return empty list if no ignore file is found
        return []

    def should_ignore(
        self, 
        path: Path, 
        ignore_patterns: List[str]
    ) -> bool:
        """
        Check if a file should be ignored based on patterns.
        
        Args:
            path: Path to check
            ignore_patterns: List of ignore patterns
            
        Returns:
            True if the file should be ignored, False otherwise
        """
        if not ignore_patterns:
            return False
        
        rel_path = str(path.absolute().as_posix())
        
        # Default implementation: simple pattern matching
        if pathspec:
            # Use pathspec for git-like .ignore functionality
            spec = pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns)
            return spec.match_file(rel_path)
        else:
            # Fallback to simple matching if pathspec is not available
            for pattern in ignore_patterns:
                if pattern.endswith("/") and (
                    rel_path.startswith(pattern) or 
                    ("/" + pattern) in rel_path
                ):
                    return True
                if pattern in rel_path or fnmatch.fnmatch(rel_path, pattern):
                    return True
                
        return False

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
    ) -> OnexResultModel:
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
            OnexResultModel with aggregate results
        """
        if not directory.exists():
            return OnexResultModel(
                status=OnexStatus.error,
                target=str(directory),
                messages=[
                    OnexMessageModel(
                        summary=f"Directory does not exist: {directory}", 
                        level="error"
                    )
                ],
            )
            
        if not directory.is_dir():
            return OnexResultModel(
                status=OnexStatus.error,
                target=str(directory),
                messages=[
                    OnexMessageModel(
                        summary=f"Path is not a directory: {directory}", 
                        level="error"
                    )
                ],
            )
            
        # Create filter config
        filter_config = FileFilterModel(
            traversal_mode=TraversalModeEnum.RECURSIVE if recursive else TraversalModeEnum.FLAT,
            include_patterns=include_patterns or self.DEFAULT_INCLUDE_PATTERNS,
            exclude_patterns=exclude_patterns or [],
            ignore_file=ignore_file,
            max_file_size=max_file_size or (5 * 1024 * 1024), # Default 5MB
        )
            
        # Find eligible files
        eligible_files = self._find_files_with_config(directory, filter_config)
            
        # Process each file
        results = []
        for file_path in eligible_files:
            try:
                if dry_run:
                    # In dry run mode, just log the file
                    logger.info(f"[DRY RUN] Would process: {file_path}")
                    self.result.processed_count += 1
                    self.result.processed_files.add(file_path)
                else:
                    # Process the file
                    result = processor(file_path)
                    results.append(result)
                    self.result.processed_count += 1
                    self.result.processed_files.add(file_path)
                    try:
                        # Update total size if possible
                        self.result.total_size_bytes += file_path.stat().st_size
                    except OSError:
                        pass
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                self.result.failed_count += 1
                self.result.failed_files.add(file_path)
                results.append(
                    OnexResultModel(
                        status=OnexStatus.error,
                        target=str(file_path),
                        messages=[
                            OnexMessageModel(
                                summary=f"Error processing file: {str(e)}", 
                                level="error"
                            )
                        ],
                    )
                )
        
        # Create aggregate result
        if not eligible_files:
            return OnexResultModel(
                status=OnexStatus.warning,
                target=str(directory),
                messages=[
                    OnexMessageModel(
                        summary=f"No eligible files found in {directory}",
                        level="warning",
                    )
                ],
                metadata={
                    "processed": self.result.processed_count,
                    "failed": self.result.failed_count,
                    "skipped": self.result.skipped_count,
                },
            )
            
        # Determine aggregate status
        status = OnexStatus.success
        if self.result.failed_count > 0:
            status = OnexStatus.error
        # If all processed files are warnings (e.g., empty), treat as success for aggregate
        # Only set warning if no files processed at all
        elif self.result.processed_count == 0:
            status = OnexStatus.warning
            
        return OnexResultModel(
            status=status,
            target=str(directory),
            messages=[
                OnexMessageModel(
                    summary=f"Processed {self.result.processed_count} files, "
                           f"{self.result.failed_count} failed, "
                           f"{self.result.skipped_count} skipped",
                    level="info" if status == OnexStatus.success else 
                          "warning" if status == OnexStatus.warning else "error",
                )
            ],
            metadata={
                "processed": self.result.processed_count,
                "failed": self.result.failed_count,
                "skipped": self.result.skipped_count,
                "size_bytes": self.result.total_size_bytes,
            },
        )

    def validate_tree_sync(
        self,
        directory: Path,
        tree_file: Path,
    ):
        """
        Filesystem mode does not support .tree sync validation.
        """
        raise NotImplementedError("validate_tree_sync is not supported in filesystem mode.")

    def get_canonical_files_from_tree(
        self,
        tree_file: Path,
    ):
        """
        Filesystem mode does not support .tree file discovery.
        """
        raise NotImplementedError("get_canonical_files_from_tree is not supported in filesystem mode.") 