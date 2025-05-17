"""
Enums for file traversal and ignore pattern handling.
"""

from enum import Enum

# === OmniNode:Metadata ===
metadata_version = "0.1"
name = "model_enum_ignore_pattern_source"
namespace = "foundation.model"
version = "0.1.0"
type = "model"
entrypoint = "model_enum_ignore_pattern_source.py"
owner = "foundation-team"
# === /OmniNode:Metadata ===


class IgnorePatternSourceEnum(str, Enum):
    """
    Canonical sources for ignore patterns when traversing directories.

    This enum defines the possible sources for ignore patterns when
    filtering files during directory traversal operations.
    """

    FILE = "file"  # Patterns from an ignore file (e.g., .stamperignore)
    DIRECTORY = "directory"  # Default directory patterns to ignore (e.g., .git)
    USER = "user"  # User-provided patterns via CLI or API
    DEFAULT = "default"  # Built-in default patterns from the application
    NONE = "none"  # No ignore patterns (process all files)


class TraversalModeEnum(str, Enum):
    """
    Canonical modes for directory traversal.

    This enum defines the possible modes for traversing directories when
    processing files.
    """

    RECURSIVE = "recursive"  # Recursively traverse all subdirectories
    FLAT = "flat"  # Only process files in the specified directory
    SHALLOW = "shallow"  # Process files in the specified directory and immediate subdirectories
    CUSTOM = "custom"  # Custom traversal based on specific rules
