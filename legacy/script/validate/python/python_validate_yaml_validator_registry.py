#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: yaml_validate_registry
# namespace: omninode.tools.yaml_validate_registry
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:04+00:00
# last_modified_at: 2025-04-27T18:13:04+00:00
# entrypoint: yaml_validate_registry.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""yaml_validate_registry.py containers.foundation.src.foundation.script.vali
dation.yaml_validate_registry.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

SCHEMA_DIR = Path(__file__).parent / "schemas"


class YamlValidatorRegistry:
    """Discovers and loads all YAML validator schemas in the schemas/
    directory.

    Exposes APIs for listing and retrieving schemas by metadata fields.
    """

    def __init__(self, schema_dir: Optional[Path] = None):
        self.schema_dir = schema_dir or SCHEMA_DIR
        self.schemas: List[Dict[str, Any]] = []
        self._load_schemas()

    def _load_schemas(self):
        self.schemas = []
        for file in self.schema_dir.glob("*.yml"):
            self._load_schema_file(file)
        for file in self.schema_dir.glob("*.yaml"):
            self._load_schema_file(file)

    def _load_schema_file(self, file_path: Path):
        try:
            with open(file_path, "r") as f:
                schema = yaml.safe_load(f)
            # Basic metadata validation stub
            if not self._validate_metadata(schema, file_path):
                print(f"[WARN] Metadata block missing or invalid in {file_path}")
                return
            schema["__file__"] = str(file_path)
            self.schemas.append(schema)
        except Exception as e:
            print(f"[ERROR] Failed to load schema {file_path}: {e}")

    def _validate_metadata(self, schema: Dict[str, Any], file_path: Path) -> bool:
        # Minimal check for required metadata fields
        required = [
            "metadata_version",
            "name",
            "namespace",
            "version",
            "entrypoint",
            "protocols_supported",
            "owner",
        ]
        if not isinstance(schema, dict):
            return False
        for key in required:
            if key not in schema:
                print(f"[WARN] Missing metadata field '{key}' in {file_path}")
                return False
        return True

    def list_schemas(self) -> List[Dict[str, Any]]:
        """Return all loaded schemas."""
        return self.schemas

    def get_schema_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Return the first schema with the given name, or None if not
        found."""
        for schema in self.schemas:
            if schema.get("name") == name:
                return schema
        return None

    def list_metadata(self) -> List[Dict[str, Any]]:
        """Return metadata for all schemas."""
        return [
            {
                k: v
                for k, v in schema.items()
                if k != "__file__" and not isinstance(v, dict)
            }
            for schema in self.schemas
        ]


if __name__ == "__main__":
    registry = YamlValidatorRegistry()
    print("Discovered YAML validator schemas:")
    for meta in registry.list_metadata():
        print(meta)
