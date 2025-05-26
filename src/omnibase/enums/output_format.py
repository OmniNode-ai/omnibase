# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: output_format.py
# version: 1.0.0
# uuid: 024a3d2d-02d8-4d5d-bcab-9f704d87b237
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165346
# last_modified_at: 2025-05-26T18:58:45.710640
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 2bad7c577d5d6d1903eebf38406db48a4e279105398a787e60abcf6c62d82731
# entrypoint: python@output_format.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.output_format
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Enums for output formats of CLI tools.
"""

from enum import Enum


class OutputFormatEnum(str, Enum):
    """
    Canonical output formats for CLI tools.
    """

    TEXT = "text"  # Human-readable text format
    JSON = "json"  # JSON format for machine consumption
    YAML = "yaml"  # YAML format for machine consumption
    MARKDOWN = "markdown"  # Markdown format for documentation
    TABLE = "table"  # Tabular format for terminal display
