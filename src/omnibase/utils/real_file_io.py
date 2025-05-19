# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 7cb99260-2129-4969-a682-ca945ab9c676
# name: real_file_io.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:56.137963
# last_modified_at: 2025-05-19T16:19:56.137965
# description: Stamped Python file: real_file_io.py
# state_contract: none
# lifecycle: active
# hash: 565d357bb5687854145beb86fcf3770ecd510fa10b2888cdd487258368611bc7
# entrypoint: {'type': 'python', 'target': 'real_file_io.py'}
# namespace: onex.stamped.real_file_io.py
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
