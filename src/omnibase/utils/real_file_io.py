from pathlib import Path
from omnibase.protocol.protocol_file_io import ProtocolFileIO
import builtins
import yaml
import json

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
    def list_files(self, directory: str | Path, pattern: str | None = None) -> list[Path]:
        p = Path(directory)
        if pattern:
            return list(p.glob(pattern))
        return list(p.iterdir()) 