"""
In-memory/mock implementation of ProtocolFileIO for protocol-first stamping tests.
Simulates a file system using a dict. No disk I/O.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml
import json
from omnibase.protocol.protocol_file_io import ProtocolFileIO

class InMemoryFileIO(ProtocolFileIO):
    """
    In-memory/mock implementation of ProtocolFileIO.
    All file operations are simulated using a dict.
    """
    def __init__(self) -> None:
        self.files: Dict[str, Any] = {}  # path -> content (str or dict)
        self.file_types: Dict[str, str] = {}  # path -> "yaml" or "json"

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
            self.files[key] = json.dumps(data, sort_keys=True)
        self.file_types[key] = "json"

    def exists(self, path: str | Path) -> bool:
        return str(path) in self.files

    def is_file(self, path: str | Path) -> bool:
        return str(path) in self.files

    def list_files(self, directory: str | Path, pattern: str | None = None) -> list[Path]:
        dir_str = str(directory)
        result = []
        for key in self.files:
            if key.startswith(dir_str):
                if pattern is None or Path(key).match(pattern):
                    result.append(Path(key))
        return result 