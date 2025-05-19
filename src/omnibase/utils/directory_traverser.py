# === OmniNode:Metadata ===\n# metadata_version: 0.1.0\n# schema_version: 1.1.0\n# uuid: 5d77c4fa-93fd-45cd-86c3-2d4a72a6ec11\n# name: directory_traverser.py\n# version: 1.0.0\n# author: metadata-stamper\n# created_at: 2025-05-19T14:42:17.350069\n# last_modified_at: 2025-05-19T14:42:17.350072\n# description: Stamped Python file: directory_traverser.py\n# state_contract: none\n# lifecycle: active\n# hash: 0000000000000000000000000000000000000000000000000000000000000000\n# entrypoint: {'type': 'python', 'target': 'directory_traverser.py'}\n# namespace: onex.stamped.directory_traverser.py\n# meta_type: tool\n# === /OmniNode:Metadata ===\n\n# # === OmniNode:Metadata ===\n# metadata_version: 0.1.0\n# schema_version: 1.1.0\n# uuid: 6c74e7ab-19d5-4f60-b40f-4c782e32a903\n# name: directory_traverser.py\n# version: 1.0.0\n# author: metadata-stamper\n# created_at: 2025-05-19T14:40:58.744540\n# last_modified_at: 2025-05-19T14:40:58.744542\n# description: Stamped Python file: directory_traverser.py\n# state_contract: none\n# lifecycle: active\n# hash: 0000000000000000000000000000000000000000000000000000000000000000\n# entrypoint: {'type': 'python', 'target': 'directory_traverser.py'}\n# namespace: onex.stamped.directory_traverser.py\n# meta_type: tool\n# # === /OmniNode:Metadata ===\n\n# === OmniNode:Metadata ===\n# metadata_version: 0.1.0\n# schema_version: 1.1.0\n# uuid: 685faca7-7621-45f0-b1b6-770308d8d667\n# name: directory_traverser.py\n# version: 1.0.0\n# author: metadata-stamper\n# created_at: 2025-05-19T14:39:41.082488\n# last_modified_at: 2025-05-19T14:39:41.082492\n# description: Stamped Python file: directory_traverser.py\n# state_contract: none\n# lifecycle: active\n# hash: 0000000000000000000000000000000000000000000000000000000000000000\n# entrypoint: {'type': 'python', 'target': 'directory_traverser.py'}\n# namespace: onex.stamped.directory_traverser.py\n# meta_type: tool\n# === /OmniNode:Metadata ===\n\n# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 7efa41e8-b924-484e-b8dc-67cae25a9290
# name: directory_traverser.py
# version: 1.0.0
# author: metadata-stamper
# created_at: 2025-05-19T14:36:03.664826
# last_modified_at: 2025-05-19T14:36:03.664832
# description: Stamped Python file: directory_traverser.py
# state_contract: none
# lifecycle: active
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# entrypoint: {'type': 'python', 'target': 'directory_traverser.py'}
# namespace: onex.stamped.directory_traverser.py
# meta_type: tool
# === /OmniNode:Metadata ===
"""
Directory traversal utility for finding and processing files in directories.
"""

import fnmatch
import importlib
import logging
from pathlib import Path
from types import ModuleType
from typing import Callable, List, Optional, Set, TypeVar

# Try to import pathspec for better glob pattern matching
try:
    pathspec: Optional[ModuleType] = importlib.import_module("pathspec")
except ImportError:
    pathspec = None

from omnibase.model.model_enum_ignore_pattern_source import (
    IgnorePatternSourceEnum,
    TraversalModeEnum,
)
from omnibase.model.model_enum_log_level import LogLevelEnum
from omnibase.model.model_file_filter import (
    DirectoryProcessingResultModel,
    FileFilterModel,
)
from omnibase.model.model_onex_message_result import (
    OnexMessageModel,
    OnexResultModel,
    OnexStatus,
)
from omnibase.model.model_tree_sync_result import TreeSyncResultModel
from omnibase.protocol.protocol_directory_traverser import ProtocolDirectoryTraverser
from omnibase.protocol.protocol_file_discovery_source import ProtocolFileDiscoverySource

# === OmniNode:Metadata ===
metadata_version = "0.1"
name = "directory_traverser"
namespace = "foundation.utils"
version = "0.1.0"
meta_type = "utility"
entrypoint = "directory_traverser.py"
owner = "foundation-team"
# === /OmniNode:Metadata ===

logger = logging.getLogger(__name__)
T = TypeVar("T")  # Generic type variable for processor result


class SchemaExclusionRegistry:
    """
    Registry for schema exclusion logic. Supports DI and extension.
    By default, excludes files in 'schemas/' directories or with known schema filenames.
    """

    DEFAULT_SCHEMA_DIRS = ["schemas", "schema"]
    DEFAULT_SCHEMA_PATTERNS = [
        "*_schema.yaml",
        "*_schema.yml",
        "*_schema.json",
        "onex_node.yaml",
        "onex_node.json",
        "state_contract.yaml",
        "state_contract.json",
        "tree_format.yaml",
        "tree_format.json",
        "execution_result.yaml",
        "execution_result.json",
    ]

    def __init__(
        self,
        extra_dirs: Optional[list[str]] = None,
        extra_patterns: Optional[list[str]] = None,
    ) -> None:
        self.schema_dirs = set(self.DEFAULT_SCHEMA_DIRS)
        if extra_dirs:
            self.schema_dirs.update(extra_dirs)
        self.schema_patterns = set(self.DEFAULT_SCHEMA_PATTERNS)
        if extra_patterns:
            self.schema_patterns.update(extra_patterns)

    def is_schema_file(self, path: Path) -> bool:
        # Exclude if in a schema directory
        if any(part in self.schema_dirs for part in path.parts):
            return True
        # Exclude if matches known schema filename patterns
        for pat in self.schema_patterns:
            if path.match(pat):
                return True
        return False


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
        ".git",
        ".github",
        "__pycache__",
        ".ruff_cache",
        ".pytest_cache",
        ".venv",
        "venv",
        "node_modules",
    ]

    def __init__(
        self, schema_exclusion_registry: Optional[SchemaExclusionRegistry] = None
    ) -> None:
        """Initialize the directory traverser."""
        # Provide all required fields for DirectoryProcessingResultModel
        self.result = DirectoryProcessingResultModel(
            processed_count=0,
            failed_count=0,
            skipped_count=0,
            total_size_bytes=0,
            directory=None,
            filter_config=None,
        )
        self.schema_exclusion_registry = (
            schema_exclusion_registry or SchemaExclusionRegistry()
        )

    def reset_counters(self) -> None:
        """Reset file counters."""
        self.result = DirectoryProcessingResultModel(
            processed_count=0,
            failed_count=0,
            skipped_count=0,
            total_size_bytes=0,
            directory=self.directory if hasattr(self, "directory") else None,
            filter_config=(
                self.filter_config if hasattr(self, "filter_config") else None
            ),
        )

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
            traversal_mode=(
                TraversalModeEnum.RECURSIVE if recursive else TraversalModeEnum.FLAT
            ),
            include_patterns=include_patterns or self.DEFAULT_INCLUDE_PATTERNS,
            exclude_patterns=exclude_patterns or [],
            ignore_file=ignore_file,
            ignore_pattern_sources=[
                IgnorePatternSourceEnum.FILE,
                IgnorePatternSourceEnum.DEFAULT,
            ],
            max_file_size=5 * 1024 * 1024,  # Always provide an int
            max_files=None,
            follow_symlinks=False,
            case_sensitive=False,
        )
        return self._find_files_with_config(directory, filter_config)

    def _find_files_with_config(
        self, directory: Path, filter_config: FileFilterModel
    ) -> Set[Path]:
        """
        Find all files matching filter criteria in the directory.

        Args:
            directory: Directory to search
            filter_config: Configuration for filtering files

        Returns:
            Set of Path objects for matching files
        """
        logger.debug(f"[_find_files_with_config] directory={directory}")
        logger.debug(
            f"[_find_files_with_config] filter_config.include_patterns={filter_config.include_patterns}"
        )
        logger.debug(
            f"[_find_files_with_config] filter_config.exclude_patterns={filter_config.exclude_patterns}"
        )
        if not directory.exists() or not directory.is_dir():
            return set()

        # Reset counters for a new operation
        self.reset_counters()
        self.result.directory = directory
        self.result.filter_config = filter_config

        # Determine if operation is recursive
        recursive = filter_config.traversal_mode in [
            TraversalModeEnum.RECURSIVE,
            TraversalModeEnum.SHALLOW,
        ]
        logger.debug(
            f"[_find_files_with_config] recursive={recursive} (traversal_mode={filter_config.traversal_mode})"
        )

        # Load ignore patterns from all configured sources
        ignore_patterns = self._load_ignore_patterns_from_sources(
            filter_config.ignore_pattern_sources, filter_config.ignore_file
        )

        # Add exclude patterns to ignore patterns
        if filter_config.exclude_patterns:
            ignore_patterns.extend(filter_config.exclude_patterns)

        # Get all files matching the include patterns
        all_files: Set[Path] = set()
        for pattern in filter_config.include_patterns:
            orig_pattern = pattern
            if recursive:
                # If pattern starts with '**/' or '**', use as-is
                if pattern.startswith("**/") or pattern.startswith("**"):
                    pass  # use as-is
                # If pattern starts with '*.', convert to '**/*.ext'
                elif pattern.startswith("*."):
                    pattern = f"**/{pattern}"
                # Otherwise, use as-is
                # (could add more logic for other cases if needed)
                logger.debug(
                    f"[glob] Recursive mode: original pattern: {orig_pattern}, final pattern: {pattern}"
                )
                matched = list(directory.glob(pattern))
                logger.debug(f"[glob] Pattern: {pattern}, Matched: {matched}")
                all_files.update(matched)
            else:
                # Non-recursive: match only in the current directory
                if pattern.startswith("**/"):
                    pattern = pattern.replace("**/", "")
                logger.debug(
                    f"[glob] Non-recursive mode: original pattern: {orig_pattern}, final pattern: {pattern}"
                )
                matched = list(directory.glob(pattern))
                logger.debug(f"[glob] Pattern: {pattern}, Matched: {matched}")
                all_files.update(matched)

        # Filter out ignored files
        eligible_files: Set[Path] = set()
        for file_path in all_files:
            if not file_path.is_file():
                continue

            # Skip files not in the specified directory when in FLAT mode
            if (
                filter_config.traversal_mode == TraversalModeEnum.FLAT
                and file_path.parent != directory
            ):
                self.result.skipped_count += 1
                self.result.skipped_files.add(file_path)
                continue

            # Skip files in non-immediate subdirectories in SHALLOW mode
            if (
                filter_config.traversal_mode == TraversalModeEnum.SHALLOW
                and file_path.parent != directory
                and file_path.parent.parent != directory
            ):
                self.result.skipped_count += 1
                self.result.skipped_files.add(file_path)
                continue

            # Skip files matching ignore patterns
            if self.should_ignore(file_path, ignore_patterns, root_dir=directory):
                logger.debug(
                    f"File {file_path} is ignored by patterns: {ignore_patterns}"
                )
                self.result.skipped_count += 1
                self.result.skipped_files.add(file_path)
                continue

            # Skip files identified as schema definitions
            if self.schema_exclusion_registry.is_schema_file(file_path):
                logger.debug(f"File {file_path} is excluded as a schema definition.")
                self.result.skipped_count += 1
                self.result.skipped_files.add(file_path)
                continue

            # Skip files exceeding max size
            if filter_config.max_file_size > 0:
                try:
                    file_size = file_path.stat().st_size
                    if file_size > filter_config.max_file_size:
                        logger.debug(
                            f"Skipping file exceeding size limit: {file_path} ({file_size} bytes)"
                        )
                        self.result.skipped_count += 1
                        self.result.skipped_files.add(file_path)
                        continue
                except OSError as e:
                    logger.warning(f"Error checking file size: {file_path}: {e}")
                    self.result.skipped_count += 1
                    self.result.skipped_files.add(file_path)
                    continue

            # Apply max_files limit if specified
            if (
                filter_config.max_files is not None
                and len(eligible_files) >= filter_config.max_files
            ):
                logger.debug(f"Reached maximum file limit: {filter_config.max_files}")
                self.result.skipped_count += 1
                self.result.skipped_files.add(file_path)
                continue

            eligible_files.add(file_path)

        logger.debug(f"[process_directory] eligible_files={list(eligible_files)}")
        return eligible_files

    def _load_ignore_patterns_from_sources(
        self, sources: List[IgnorePatternSourceEnum], ignore_file: Optional[Path] = None
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
        if (
            IgnorePatternSourceEnum.DEFAULT in sources
            or IgnorePatternSourceEnum.DIRECTORY in sources
        ):
            patterns.extend([f"{d}/" for d in self.DEFAULT_IGNORE_DIRS])

        return patterns

    def load_ignore_patterns(self, ignore_file: Optional[Path] = None) -> List[str]:
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
        self, path: Path, ignore_patterns: List[str], root_dir: Optional[Path] = None
    ) -> bool:
        """
        Check if a file should be ignored based on patterns.

        Args:
            path: Path to check
            ignore_patterns: List of ignore patterns
            root_dir: Root directory for relative matching (default: cwd)

        Returns:
            True if the file should be ignored, False otherwise
        """
        if not ignore_patterns:
            return False

        if root_dir is None:
            root_dir = Path.cwd()
        try:
            rel_path = str(path.relative_to(root_dir).as_posix())
        except ValueError:
            rel_path = str(path.as_posix())
        # Ensure rel_path never has a leading slash for pathspec
        rel_path = rel_path.lstrip("/")

        # Use pathspec if available for robust gitignore-style matching
        if pathspec:
            logger.debug(
                f"Using pathspec for ignore pattern matching on {rel_path} with patterns: {ignore_patterns}"
            )
            spec = pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns)
            matched = spec.match_file(rel_path)
            logger.debug(
                f"should_ignore: rel_path={rel_path}, patterns={ignore_patterns}, matched={matched}"
            )
            if matched:
                logger.debug(f"File {rel_path} is ignored by pathspec pattern.")
            return bool(matched)
        else:
            # Fallback: manual directory pattern matching (for environments without pathspec)
            for pattern in ignore_patterns:
                if pattern.endswith("/"):
                    dir_name = pattern.rstrip("/")
                    parts = rel_path.split("/")
                    if dir_name in parts[:-1]:
                        logger.debug(
                            f"Ignoring {rel_path} due to directory pattern {pattern}"
                        )
                        return True
                    for parent in path.parents:
                        if parent.name == dir_name:
                            logger.debug(
                                f"Ignoring {rel_path} due to parent directory {parent} matching {dir_name}"
                            )
                            return True
                    if rel_path.startswith(dir_name + "/"):
                        logger.debug(
                            f"Ignoring {rel_path} due to rel_path starting with {dir_name}/"
                        )
                        return True
                if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(
                    path.name, pattern
                ):
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
        logger.debug(f"[process_directory] directory={directory}")
        logger.debug(f"[process_directory] include_patterns={include_patterns}")
        logger.debug(f"[process_directory] exclude_patterns={exclude_patterns}")
        if not directory.exists():
            return OnexResultModel(
                status=OnexStatus.error,
                target=str(directory),
                messages=[
                    OnexMessageModel(
                        summary=f"Directory does not exist: {directory}",
                        level=LogLevelEnum.ERROR,
                        file=None,
                        line=None,
                        details=None,
                        code=None,
                        context=None,
                        timestamp=None,
                        type=None,
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
                        level=LogLevelEnum.ERROR,
                        file=None,
                        line=None,
                        details=None,
                        code=None,
                        context=None,
                        timestamp=None,
                        type=None,
                    )
                ],
            )
        filter_config = FileFilterModel(
            traversal_mode=(
                TraversalModeEnum.RECURSIVE if recursive else TraversalModeEnum.FLAT
            ),
            include_patterns=include_patterns or self.DEFAULT_INCLUDE_PATTERNS,
            exclude_patterns=exclude_patterns or [],
            ignore_file=ignore_file,
            max_file_size=max_file_size or (5 * 1024 * 1024),
            max_files=None,
            follow_symlinks=False,
            case_sensitive=False,
            ignore_pattern_sources=[
                IgnorePatternSourceEnum.FILE,
                IgnorePatternSourceEnum.DEFAULT,
            ],
        )
        eligible_files: Set[Path] = self._find_files_with_config(
            directory, filter_config
        )
        logger.debug(f"[process_directory] eligible_files={list(eligible_files)}")
        results: List[OnexResultModel] = []
        for file_path in eligible_files:
            try:
                if dry_run:
                    logger.info(f"[DRY RUN] Would process: {file_path}")
                    self.result.processed_count += 1
                    self.result.processed_files.add(file_path)
                else:
                    result = processor(file_path)
                    if isinstance(result, OnexResultModel):
                        results.append(result)
                    else:
                        # If processor returns something else, wrap in OnexResultModel
                        results.append(
                            OnexResultModel(
                                status=OnexStatus.success,
                                target=str(file_path),
                                messages=[],
                            )
                        )
                    self.result.processed_count += 1
                    self.result.processed_files.add(file_path)
                    try:
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
                                level=LogLevelEnum.ERROR,
                                file=None,
                                line=None,
                                details=None,
                                code=None,
                                context=None,
                                timestamp=None,
                                type=None,
                            )
                        ],
                    )
                )
        if not eligible_files:
            return OnexResultModel(
                status=OnexStatus.warning,
                target=str(directory),
                messages=[
                    OnexMessageModel(
                        summary=f"No eligible files found in {directory}",
                        level=LogLevelEnum.WARNING,
                        file=None,
                        line=None,
                        details=None,
                        code=None,
                        context=None,
                        timestamp=None,
                        type=None,
                    )
                ],
                metadata={
                    "processed": self.result.processed_count,
                    "failed": self.result.failed_count,
                    "skipped": self.result.skipped_count,
                },
            )
        status = OnexStatus.success
        if self.result.failed_count > 0:
            status = OnexStatus.error
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
                    level=(
                        LogLevelEnum.INFO
                        if status == OnexStatus.success
                        else (
                            LogLevelEnum.WARNING
                            if status == OnexStatus.warning
                            else LogLevelEnum.ERROR
                        )
                    ),
                    file=None,
                    line=None,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
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
    ) -> TreeSyncResultModel:
        """
        ProtocolFileDiscoverySource compliance: validate .tree sync (not supported in filesystem mode).
        This is a protocol stub; always raises NotImplementedError.
        """
        raise NotImplementedError(
            "validate_tree_sync is not supported in filesystem mode."
        )

    def get_canonical_files_from_tree(
        self,
        tree_file: Path,
    ) -> Set[Path]:
        """
        ProtocolFileDiscoverySource compliance: get canonical files from .tree (not supported in filesystem mode).
        This is a protocol stub; always raises NotImplementedError.
        """
        raise NotImplementedError(
            "get_canonical_files_from_tree is not supported in filesystem mode."
        )

    def discover_files(
        self,
        directory: Path,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        ignore_file: Optional[Path] = None,
    ) -> Set[Path]:
        """
        ProtocolFileDiscoverySource compliance: discover files in directory.
        """
        return self.find_files(
            directory, include_patterns, exclude_patterns, True, ignore_file
        )
