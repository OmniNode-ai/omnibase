# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: real_file_io.py
# version: 1.0.0
# uuid: b7f9a712-78be-4167-9c68-95cb87a52c67
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.169651
# last_modified_at: 2025-05-21T16:42:46.101403
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 38ed99d73adfc388242a2c9dfca4309a8b95928bf059535f8a560a8ca0eec59e
# entrypoint: {'type': 'python', 'target': 'real_file_io.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.real_file_io
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
