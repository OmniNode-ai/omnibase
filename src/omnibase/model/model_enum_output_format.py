# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_enum_output_format.py
# version: 1.0.0
# uuid: 024a3d2d-02d8-4d5d-bcab-9f704d87b237
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165346
# last_modified_at: 2025-05-21T16:42:46.064249
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: b6e4fbd047e2ef7edd6e309d6d016efabc13ecd54eeb6d56496f5a41a1b46236
# entrypoint: python@model_enum_output_format.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_enum_output_format
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
