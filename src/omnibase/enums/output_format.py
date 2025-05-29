# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.803420'
# description: Stamped by PythonHandler
# entrypoint: python://output_format.py
# hash: 1abde1148d95bc8e832bd9b5bcbf84f70645a01b38335cdfee51ed5e16bbe7fd
# last_modified_at: '2025-05-29T11:50:10.776292+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: output_format.py
# namespace: omnibase.output_format
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 6315dd94-5965-431a-b63e-d3a3764fa72c
# version: 1.0.0
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
    CSV = "csv"  # CSV format for tabular data
