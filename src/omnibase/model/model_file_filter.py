# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_file_filter.py
# version: 1.0.0
# uuid: 35407669-e632-44e1-a557-9e50bafadb82
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165486
# last_modified_at: 2025-05-21T16:42:46.076573
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: e1e3f0c2b89f7aca190917a6ad45329b10dcd39ea738666307351cf2ae86d34c
# entrypoint: {'type': 'python', 'target': 'model_file_filter.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_file_filter
# meta_type: tool
# === /OmniNode:Metadata ===

"""
Models for file filtering and directory traversal configuration.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set

from pydantic import BaseModel, ConfigDict, Field

from omnibase.model.model_enum_ignore_pattern_source import (
    IgnorePatternSourceEnum,
    TraversalModeEnum,
)


class FileFilterModel(BaseModel):
    """
    Configuration model for filtering files during directory traversal.

    This model defines all parameters needed for file filtering operations,
    including patterns, traversal mode, and ignore sources.
    """

    # Traversal configuration
    traversal_mode: TraversalModeEnum = Field(
        default=TraversalModeEnum.RECURSIVE,
        description="Mode for traversing directories",
    )

    # Pattern configuration
    include_patterns: List[str] = Field(
        default_factory=list,
        description="Glob patterns to include (e.g., ['**/*.yaml', '**/*.json'])",
    )
    exclude_patterns: List[str] = Field(
        default_factory=list,
        description="Glob patterns to exclude (e.g., ['**/.git/**'])",
    )
    ignore_file: Optional[Path] = Field(
        None, description="Path to ignore file (e.g., .stamperignore)"
    )

    # Ignore pattern sources
    ignore_pattern_sources: List[IgnorePatternSourceEnum] = Field(
        default_factory=lambda: [
            IgnorePatternSourceEnum.FILE,
            IgnorePatternSourceEnum.DEFAULT,
        ],
        description="Sources to look for ignore patterns",
    )

    # Size and limit configuration
    max_file_size: int = Field(
        5 * 1024 * 1024, description="Maximum file size in bytes to process"
    )
    max_files: Optional[int] = Field(
        None, description="Maximum number of files to process"
    )

    # Processing flags
    follow_symlinks: bool = Field(False, description="Whether to follow symbolic links")
    case_sensitive: bool = Field(
        True, description="Whether pattern matching is case sensitive"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


class DirectoryProcessingResultModel(BaseModel):
    """
    Results model for directory processing operations.

    This model captures the outcome of a directory processing operation,
    including counts of processed, failed, and skipped files.
    """

    # File statistics
    processed_count: int = Field(0, description="Number of files processed")
    failed_count: int = Field(0, description="Number of files that failed processing")
    skipped_count: int = Field(0, description="Number of files skipped")

    # File sets
    processed_files: Set[Path] = Field(
        default_factory=set, description="Set of processed files"
    )
    failed_files: Set[Path] = Field(
        default_factory=set, description="Set of files that failed processing"
    )
    skipped_files: Set[Path] = Field(
        default_factory=set, description="Set of files skipped"
    )

    # Processing metadata
    total_size_bytes: int = Field(
        0, description="Total size of processed files in bytes"
    )
    directory: Optional[Path] = Field(None, description="Directory that was processed")
    filter_config: Optional[FileFilterModel] = Field(
        None, description="Filter configuration used"
    )

    skipped_file_reasons: Dict[Path, str] = Field(
        default_factory=dict, description="Map of skipped files to reason for skip"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)
