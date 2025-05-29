# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.752321'
# description: Stamped by PythonHandler
# entrypoint: python://file_type.py
# hash: 45f7a643fef24535383a4ffa126e3d8ca780a66c007878005cf428120802e0ef
# last_modified_at: '2025-05-29T11:50:10.748671+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: file_type.py
# namespace: omnibase.file_type
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 7d4d495f-6e13-4d42-9af5-801983ee1c00
# version: 1.0.0
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
