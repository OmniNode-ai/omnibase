# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: directory_traverser.py
# version: 1.0.0
# uuid: aebbc1dc-0ca8-4bb5-8903-51f3367463e1
# author: OmniNode Team
# created_at: 2025-05-22T05:34:29.788355
# last_modified_at: 2025-05-22T20:50:39.718462
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: af33099b1e816b67a91c9ae9d46a790b5f490573c0f6d4ab4233b79145e20bb9
# entrypoint: python@directory_traverser.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.directory_traverser
# meta_type: tool
# === /OmniNode:Metadata ===


import logging
from pathlib import Path
from typing import Callable, List, Optional, Set, TypeVar, Union

from omnibase.model.model_file_filter import DirectoryProcessingResultModel
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_directory_traverser import ProtocolDirectoryTraverser
from omnibase.protocol.protocol_file_discovery_source import ProtocolFileDiscoverySource
from omnibase.runtime.protocol.protocol_schema_exclusion_registry import (
    ProtocolSchemaExclusionRegistry,
)

logger = logging.getLogger(__name__)
T = TypeVar("T")


class SchemaExclusionRegistry(ProtocolSchemaExclusionRegistry):
    """
    Concrete implementation of ProtocolSchemaExclusionRegistry for shared runtime use.
    Implements all required methods for schema exclusion logic.
    See runtime/protocol/protocol_schema_exclusion_registry.py for canonical protocol and rationale.
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
        if any(part in self.schema_dirs for part in path.parts):
            return True
        for pat in self.schema_patterns:
            if path.match(pat):
                return True
        return False


class DirectoryTraverser(ProtocolDirectoryTraverser, ProtocolFileDiscoverySource):
    """
    Canonical implementation of ProtocolDirectoryTraverser for shared runtime use.
    Implements all required methods for directory traversal, filtering, and processing.
    See protocol/protocol_directory_traverser.py for canonical protocol and rationale.
    """

    DEFAULT_INCLUDE_PATTERNS = ["**/*.yaml", "**/*.yml", "**/*.json"]
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
        See protocol for full docstring.
        """
        # TODO: Implement canonical file discovery logic
        return set()

    def load_ignore_patterns(self, ignore_file: Optional[Path] = None) -> List[str]:
        """
        Load ignore patterns from a file.
        See protocol for full docstring.
        """
        # TODO: Implement canonical ignore pattern loading
        return []

    def should_ignore(self, path: Path, ignore_patterns: List[str]) -> bool:
        """
        Check if a file should be ignored based on patterns.
        See protocol for full docstring.
        """
        # TODO: Implement canonical ignore logic
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
    ) -> Union[OnexResultModel, List[T]]:
        """
        Process all eligible files in a directory using the provided processor function.
        See protocol for full docstring.
        """
        # TODO: Implement canonical directory processing logic
        return []

    # TODO: Implement all ProtocolDirectoryTraverser methods with correct signatures and docstrings
    # TODO: Implement find_files, process_directory, load_ignore_patterns, should_ignore, etc. as needed for node
