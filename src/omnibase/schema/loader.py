# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: loader.py
# version: 1.0.0
# uuid: 88ce2529-8f6f-400b-bfe3-4609dd1fc2c9
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.168219
# last_modified_at: 2025-05-21T16:42:46.073604
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 76d3773cc68c90315bbf6948abcf5e8e9c0fc56b8a9334514c4ef98f7daff9d6
# entrypoint: {'type': 'python', 'target': 'loader.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.loader
# meta_type: tool
# === /OmniNode:Metadata ===

import json
from pathlib import Path

import yaml

from omnibase.core.errors import OmniBaseError
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_schema import SchemaModel
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader


class SchemaLoader(ProtocolSchemaLoader):
    """
    Canonical loader for ONEX node YAML and JSON schema files.
    Implements ProtocolSchemaLoader. All methods use Path objects and return strongly-typed models as appropriate.
    TODO: Support dependency injection and loader swapping in M1+.
    """

    def load_onex_yaml(self, path: Path) -> NodeMetadataBlock:
        """
        Load an ONEX node metadata YAML file and return a NodeMetadataBlock.
        Raises a ValueError if the file is missing or invalid.
        """
        try:
            with path.open("r") as f:
                data = yaml.safe_load(f)
            return NodeMetadataBlock(**data)
        except Exception as e:
            raise OmniBaseError(f"Failed to load ONEX YAML: {path}: {e}")

    def load_json_schema(self, path: Path) -> SchemaModel:
        """
        Load a JSON schema file and return a SchemaModel.
        Raises a ValueError if the file is missing or invalid.
        """
        try:
            with path.open("r") as f:
                data = json.load(f)
            return SchemaModel(**data)
        except Exception as e:
            raise OmniBaseError(f"Failed to load JSON schema: {path}: {e}")

    def discover_schemas(self, root: Path) -> list[Path]:
        """
        Recursively discover all .yaml and .json schema files under the given root directory.
        Logs discovered files. Warns and skips malformed files. M1+ will register schemas.
        """
        discovered = []
        for file in root.rglob("*"):
            if file.suffix in {".yaml", ".json"}:
                try:
                    # Try to open and parse to check for malformed files
                    if file.suffix == ".yaml":
                        with file.open("r") as f:
                            yaml.safe_load(f)
                    else:
                        with file.open("r") as f:
                            json.load(f)
                    print(f"Discovered schema: {file}")
                    discovered.append(file)
                except Exception as e:
                    print(f"Warning: Malformed schema file skipped: {file}: {e}")
        # TODO: M1+ register schemas here
        return discovered

    # TODO: Add recursive directory scanning and schema auto-registration in M1+
