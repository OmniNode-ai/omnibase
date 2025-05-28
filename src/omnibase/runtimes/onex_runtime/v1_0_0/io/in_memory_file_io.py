# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: in_memory_file_io.py
# version: 1.0.0
# uuid: 86f19f0d-dda9-4c2b-8a9c-257672a8dee3
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.420216
# last_modified_at: 2025-05-28T17:20:06.118802
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 3db42827c01d9a2df2d312c8dd0eb75f691c676f4412a6f635df0d2e19a38dd9
# entrypoint: python@in_memory_file_io.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.in_memory_file_io
# meta_type: tool
# === /OmniNode:Metadata ===


import datetime
import json
from pathlib import Path
from typing import Any, Dict

import yaml

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.protocol.protocol_file_io import ProtocolFileIO


class InMemoryFileIO(ProtocolFileIO):
    """
    In-memory/mock implementation of ProtocolFileIO for protocol-first stamping tests.
    Simulates a file system using a dict. No disk I/O.
    """

    def __init__(self) -> None:
        self.files: Dict[str, Any] = {}
        self.file_types: Dict[str, str] = {}

    def _json_default(self, obj: object) -> str:
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        raise OnexError(
            f"Object of type {type(obj).__name__} is not JSON serializable",
            CoreErrorCode.PARAMETER_TYPE_MISMATCH,
        )

    def read_yaml(self, path: str | Path) -> Any:
        key = str(path)
        if key not in self.files:
            raise OnexError(
                f"YAML file not found: {path}", CoreErrorCode.FILE_NOT_FOUND
            )
        content = self.files[key]
        if content is None:
            return None
        if isinstance(content, (dict, list)):
            return content
        elif isinstance(content, str):
            try:
                parsed = yaml.safe_load(content)
            except Exception as e:
                raise OnexError(f"Malformed YAML: {e}", CoreErrorCode.VALIDATION_FAILED)
            if parsed is None:
                return None
            if not isinstance(parsed, (dict, list)):
                raise OnexError(
                    "Malformed YAML: not a mapping or sequence",
                    CoreErrorCode.VALIDATION_FAILED,
                )
            return parsed
        else:
            raise OnexError(
                "Malformed YAML: unsupported content type",
                CoreErrorCode.VALIDATION_FAILED,
            )

    def read_json(self, path: str | Path) -> Any:
        key = str(path)
        if key not in self.files:
            raise OnexError(
                f"JSON file not found: {path}", CoreErrorCode.FILE_NOT_FOUND
            )
        content = self.files[key]
        if content is None:
            return None
        if isinstance(content, (dict, list)):
            return content
        elif isinstance(content, str):
            try:
                parsed = json.loads(content)
            except Exception as e:
                raise OnexError(f"Malformed JSON: {e}", CoreErrorCode.VALIDATION_FAILED)
            if parsed is None:
                return None
            if not isinstance(parsed, (dict, list)):
                raise OnexError(
                    "Malformed JSON: not a mapping or sequence",
                    CoreErrorCode.VALIDATION_FAILED,
                )
            return parsed
        else:
            raise OnexError(
                "Malformed JSON: unsupported content type",
                CoreErrorCode.VALIDATION_FAILED,
            )

    def write_yaml(self, path: str | Path, data: Any) -> None:
        key = str(path)
        if data is None:
            self.files[key] = None
        else:
            self.files[key] = yaml.safe_dump(data)
        self.file_types[key] = "yaml"

    def write_json(self, path: str | Path, data: Any) -> None:
        key = str(path)
        if data is None:
            self.files[key] = None
        else:
            self.files[key] = json.dumps(
                data, sort_keys=True, default=self._json_default
            )
        self.file_types[key] = "json"

    def exists(self, path: str | Path) -> bool:
        return str(path) in self.files

    def is_file(self, path: str | Path) -> bool:
        return str(path) in self.files

    def list_files(
        self, directory: str | Path, pattern: str | None = None
    ) -> list[Path]:
        dir_str = str(directory)
        result = []
        for key in self.files:
            if key.startswith(dir_str):
                if pattern is None or Path(key).match(pattern):
                    result.append(Path(key))
        return result

    def read_text(self, path: str | Path) -> str:
        key = str(path)
        if key not in self.files:
            raise OnexError(
                f"Text file not found: {path}", CoreErrorCode.FILE_NOT_FOUND
            )
        content = self.files[key]
        if isinstance(content, str):
            return content
        elif isinstance(content, bytes):
            return content.decode("utf-8")
        else:
            raise OnexError(
                "Malformed text: unsupported content type",
                CoreErrorCode.VALIDATION_FAILED,
            )

    def write_text(self, path: str | Path, data: str) -> None:
        key = str(path)
        self.files[key] = data
        self.file_types[key] = "text"

    def read_bytes(self, path: str | Path) -> bytes:
        key = str(path)
        if key not in self.files:
            raise OnexError(
                f"Binary file not found: {path}", CoreErrorCode.FILE_NOT_FOUND
            )
        content = self.files[key]
        if isinstance(content, bytes):
            return content
        elif isinstance(content, str):
            return content.encode("utf-8")
        else:
            raise OnexError(
                "Malformed bytes: unsupported content type",
                CoreErrorCode.VALIDATION_FAILED,
            )

    def write_bytes(self, path: str | Path, data: bytes) -> None:
        key = str(path)
        self.files[key] = data
        self.file_types[key] = "bytes"
