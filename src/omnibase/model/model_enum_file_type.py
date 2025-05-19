# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 9637d7b5-b719-4f75-a1fc-9bab0201725b
# name: model_enum_file_type.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-18T12:37:26.099775
# last_modified_at: 2025-05-18T12:37:26.099776
# description: Stamped Python file: model_enum_file_type.py
# state_contract: none
# lifecycle: active
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# entrypoint: {'type': 'python', 'target': 'model_enum_file_type.py'}
# namespace: onex.stamped.model_enum_file_type.py
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
