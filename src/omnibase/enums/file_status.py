# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.740068'
# description: Stamped by PythonHandler
# entrypoint: python://file_status.py
# hash: e438e33d82f5344e34f6bc7ff88368d4c5a06304ce853e2fbe14d548ce3d2ada
# last_modified_at: '2025-05-29T11:50:10.743038+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: file_status.py
# namespace: omnibase.file_status
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: d7aa1be6-3755-48d3-87d2-973f3d9ea174
# version: 1.0.0
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
