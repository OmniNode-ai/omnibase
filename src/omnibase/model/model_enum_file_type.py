# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 5b678207-54fc-4d62-afb7-8489d91dc3f2
# name: model_enum_file_type.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:52.548073
# last_modified_at: 2025-05-19T16:19:52.548075
# description: Stamped Python file: model_enum_file_type.py
# state_contract: none
# lifecycle: active
# hash: 0b3293e3d91c5d7b26592e62bedca996412720e07b2d2b2462a2eeca388731be
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
