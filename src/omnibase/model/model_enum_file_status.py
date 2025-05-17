"""
Enum for file status values used in metadata blocks.
"""

from enum import Enum


class FileStatusEnum(str, Enum):
    empty = "empty"  # File has no content
    unvalidated = "unvalidated"  # Not schema-validated
    validated = "validated"  # Schema-validated
    deprecated = "deprecated"  # Marked for removal
    incomplete = "incomplete"  # Missing required fields
    synthetic = "synthetic"  # Generated, not user-authored
    # Add more statuses as protocol evolves
