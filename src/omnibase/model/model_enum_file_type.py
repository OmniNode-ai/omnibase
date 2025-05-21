# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_enum_file_type.py
# version: 1.0.0
# uuid: 6078bbab-5965-44b7-98ef-956b12c466d0
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165057
# last_modified_at: 2025-05-21T16:42:46.062144
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 6464fcad5c6582c0c235640b0fe8bbd0086264bcd05b4791a8c7881dc3db3983
# entrypoint: {'type': 'python', 'target': 'model_enum_file_type.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_enum_file_type
# meta_type: tool
# === /OmniNode:Metadata ===

from enum import Enum


class FileTypeEnum(str, Enum):
    PYTHON = "python"
    YAML = "yaml"
    MARKDOWN = "markdown"
    JSON = "json"
    IGNORE = "ignore"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return self.value
