# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: in_memory_file_io.py
# version: 1.0.0
# uuid: 73197878-eeed-497b-9db7-a414bfcbebdb
# author: OmniNode Team
# created_at: 2025-05-22T14:05:21.447882
# last_modified_at: 2025-05-22T20:50:39.714617
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 3e7e34885de626d84a51cf75ce66b6c3f8698657288eb0a6ad608938d120a83b
# entrypoint: python@in_memory_file_io.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.in_memory_file_io
# meta_type: tool
# === /OmniNode:Metadata ===


import datetime
import json
from pathlib import Path
from typing import Any, Dict

import yaml

from omnibase.runtime.protocol.protocol_file_io import ProtocolFileIO


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
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    def read_yaml(self, path: str | Path) -> Any:
        key = str(path)
        if key not in self.files:
            raise FileNotFoundError(f"YAML file not found: {path}")
        content = self.files[key]
        if content is None:
            return None
        if isinstance(content, (dict, list)):
            return content
        elif isinstance(content, str):
            try:
                parsed = yaml.safe_load(content)
            except Exception as e:
                raise ValueError(f"Malformed YAML: {e}")
            if parsed is None:
                return None
            if not isinstance(parsed, (dict, list)):
                raise ValueError("Malformed YAML: not a mapping or sequence")
            return parsed
        else:
            raise ValueError("Malformed YAML: unsupported content type")

    def read_json(self, path: str | Path) -> Any:
        key = str(path)
        if key not in self.files:
            raise FileNotFoundError(f"JSON file not found: {path}")
        content = self.files[key]
        if content is None:
            return None
        if isinstance(content, (dict, list)):
            return content
        elif isinstance(content, str):
            try:
                parsed = json.loads(content)
            except Exception as e:
                raise ValueError(f"Malformed JSON: {e}")
            if parsed is None:
                return None
            if not isinstance(parsed, (dict, list)):
                raise ValueError("Malformed JSON: not a mapping or sequence")
            return parsed
        else:
            raise ValueError("Malformed JSON: unsupported content type")

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
            raise FileNotFoundError(f"Text file not found: {path}")
        content = self.files[key]
        if isinstance(content, str):
            return content
        elif isinstance(content, bytes):
            return content.decode("utf-8")
        else:
            raise ValueError("Malformed text: unsupported content type")

    def write_text(self, path: str | Path, data: str) -> None:
        key = str(path)
        self.files[key] = data
        self.file_types[key] = "text"

    def read_bytes(self, path: str | Path) -> bytes:
        key = str(path)
        if key not in self.files:
            raise FileNotFoundError(f"Binary file not found: {path}")
        content = self.files[key]
        if isinstance(content, bytes):
            return content
        elif isinstance(content, str):
            return content.encode("utf-8")
        else:
            raise ValueError("Malformed bytes: unsupported content type")

    def write_bytes(self, path: str | Path, data: bytes) -> None:
        key = str(path)
        self.files[key] = data
        self.file_types[key] = "bytes"
