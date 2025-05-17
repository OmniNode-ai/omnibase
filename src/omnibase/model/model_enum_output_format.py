"""
Enums for output formats of CLI tools.
"""

from enum import Enum

# === OmniNode:Metadata ===
metadata_version = "0.1"
name = "model_enum_output_format"
namespace = "foundation.model"
version = "0.1.0"
type = "model"
entrypoint = "model_enum_output_format.py"
owner = "foundation-team"
# === /OmniNode:Metadata ===


class OutputFormatEnum(str, Enum):
    """
    Canonical output formats for CLI tools.
    """

    TEXT = "text"  # Human-readable text format
    JSON = "json"  # JSON format for machine consumption
    YAML = "yaml"  # YAML format for machine consumption
    MARKDOWN = "markdown"  # Markdown format for documentation
    TABLE = "table"  # Tabular format for terminal display
