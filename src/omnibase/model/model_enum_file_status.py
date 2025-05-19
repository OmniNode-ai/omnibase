# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: caf19996-4a74-47d6-9835-8cc909ac4ce3
# name: model_enum_file_status.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:51.936545
# last_modified_at: 2025-05-19T16:19:51.936550
# description: Stamped Python file: model_enum_file_status.py
# state_contract: none
# lifecycle: active
# hash: 876a4b79042321a9c8dd1d1661bd4e8952080805574a238753f1d96381782ce6
# entrypoint: {'type': 'python', 'target': 'model_enum_file_status.py'}
# namespace: onex.stamped.model_enum_file_status.py
# meta_type: tool
# === /OmniNode:Metadata ===

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
