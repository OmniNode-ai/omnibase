# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: file_status.py
# version: 1.0.0
# uuid: 5119edd8-69ca-4b50-bb1b-94e6cd652d3e
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.164983
# last_modified_at: 2025-05-26T18:58:45.697927
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 8a23af36299cd431b232bbb282ad1a9eeb43ffe328f972331cf64799e0630c9c
# entrypoint: python@file_status.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.file_status
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
