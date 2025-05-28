# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: real_file_io.py
# version: 1.0.0
# uuid: 8645b6ef-583f-4f0f-8bc4-b3a7b9fe8366
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.803241
# last_modified_at: 2025-05-28T17:20:03.998607
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 6b22227feb1a7ba32693b0a602094d95833c475d4f06335065fbb63e0d486af4
# entrypoint: python@real_file_io.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.real_file_io
# meta_type: tool
# === /OmniNode:Metadata ===


import builtins
import json
from pathlib import Path

import yaml

from omnibase.protocol.protocol_file_io import ProtocolFileIO


class RealFileIO(ProtocolFileIO):
    def read_yaml(self, path: str | Path) -> object:
        with builtins.open(path, "r") as f:
            return yaml.safe_load(f)

    def read_json(self, path: str | Path) -> object:
        with builtins.open(path, "r") as f:
            return json.load(f)

    def write_yaml(self, path: str | Path, data: object) -> None:
        with builtins.open(path, "w") as f:
            yaml.safe_dump(data, f)

    def write_json(self, path: str | Path, data: object) -> None:
        with builtins.open(path, "w") as f:
            json.dump(data, f, sort_keys=True)

    def exists(self, path: str | Path) -> bool:
        return Path(path).exists()

    def is_file(self, path: str | Path) -> bool:
        return Path(path).is_file()

    def list_files(
        self, directory: str | Path, pattern: str | None = None
    ) -> list[Path]:
        p = Path(directory)
        if pattern:
            return list(p.glob(pattern))
        return list(p.iterdir())

    def read_text(self, path: str | Path) -> str:
        """Read plain text content from a file path."""
        with builtins.open(path, "r", encoding="utf-8") as f:
            return f.read()

    def write_text(self, path: str | Path, data: str) -> None:
        """Write plain text content to a file path."""
        with builtins.open(path, "w", encoding="utf-8") as f:
            f.write(data)

    def read_bytes(self, path: str | Path) -> bytes:
        """Read binary content from a file path."""
        with builtins.open(path, "rb") as f:
            return f.read()

    def write_bytes(self, path: str | Path, data: bytes) -> None:
        """Write binary content to a file path."""
        with builtins.open(path, "wb") as f:
            f.write(data)
