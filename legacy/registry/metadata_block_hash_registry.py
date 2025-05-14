"""
RegistryMetadataBlockHash: Registry for mapping file paths to metadata block hashes.
Implements ProtocolRegistryMetadataBlockHash for registry-driven metadata validation.
"""
from typing import Optional, Dict
import yaml
from pathlib import Path
from foundation.protocol.protocol_metadata_block_hash import ProtocolRegistryMetadataBlockHash

class RegistryMetadataBlockHash(ProtocolRegistryMetadataBlockHash):
    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or Path.cwd() / ".metadata_block_hash_registry.yaml"
        self._data: Dict[str, Dict] = {}
        self.load()

    def load(self) -> None:
        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as f:
                self._data = yaml.safe_load(f) or {}
        else:
            self._data = {}

    def save(self) -> None:
        with open(self.registry_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self._data, f, sort_keys=True)

    def update(self, file_path: str, hash_value: str, **meta) -> None:
        self._data[file_path] = {"hash": hash_value, **meta}
        self.save()

    def get(self, file_path: str) -> Optional[str]:
        entry = self._data.get(file_path)
        if entry:
            return entry.get("hash")
        return None

    def validate(self, file_path: str, hash_value: str) -> bool:
        return self.get(file_path) == hash_value

    def all(self) -> Dict[str, str]:
        return {k: v["hash"] for k, v in self._data.items() if "hash" in v} 