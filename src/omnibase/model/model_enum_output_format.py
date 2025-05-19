# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: efe9a6ba-b798-4cad-b8b2-e20a07293b02
# name: model_enum_output_format.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:01.699435
# last_modified_at: 2025-05-19T16:20:01.699436
# description: Stamped Python file: model_enum_output_format.py
# state_contract: none
# lifecycle: active
# hash: 6511bf52cbc3b3e17e0b6c617f933941e5df2ce72ef24f4b6d3ec10590ae659a
# entrypoint: {'type': 'python', 'target': 'model_enum_output_format.py'}
# namespace: onex.stamped.model_enum_output_format.py
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
