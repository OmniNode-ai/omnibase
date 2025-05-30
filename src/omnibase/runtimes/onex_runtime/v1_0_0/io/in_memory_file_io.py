# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.420216'
# description: Stamped by PythonHandler
# entrypoint: python://in_memory_file_io
# hash: 901f6b745f2e73f8935aa2156ccd319dd0e1eff60153e7958eb9f66fe02607f3
# last_modified_at: '2025-05-29T14:14:00.501698+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: in_memory_file_io.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.io.in_memory_file_io
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 86f19f0d-dda9-4c2b-8a9c-257672a8dee3
# version: 1.0.0
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

            def convert_entrypointblock(obj):
                if isinstance(obj, dict):
                    return {k: convert_entrypointblock(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_entrypointblock(v) for v in obj]
                elif (
                    hasattr(obj, "to_uri")
                    and obj.__class__.__name__ == "EntrypointBlock"
                ):
                    return obj.to_uri()
                else:
                    return obj

            data = convert_entrypointblock(data)
            self.files[key] = yaml.safe_dump(data)
        self.file_types[key] = "yaml"

    def write_json(self, path: str | Path, data: Any) -> None:
        key = str(path)
        if data is None:
            self.files[key] = None
        else:

            def convert_entrypointblock(obj):
                if isinstance(obj, dict):
                    return {k: convert_entrypointblock(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_entrypointblock(v) for v in obj]
                elif (
                    hasattr(obj, "to_uri")
                    and obj.__class__.__name__ == "EntrypointBlock"
                ):
                    return obj.to_uri()
                else:
                    return obj

            data = convert_entrypointblock(data)
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
