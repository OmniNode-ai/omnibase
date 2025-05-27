# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: loader.py
# version: 1.0.0
# uuid: 91f96b85-cc03-42d5-91b8-1ac68ef977fa
# author: OmniNode Team
# created_at: 2025-05-22T14:03:21.905336
# last_modified_at: 2025-05-22T20:50:39.723060
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 3429e4aa7270d64ab3c7df34186ed2abbcf32e196e548605f751551dd5b48a45
# entrypoint: python@loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.loader
# meta_type: tool
# === /OmniNode:Metadata ===


import json
from pathlib import Path
from typing import Any

import yaml

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum
from omnibase.exceptions import OmniBaseError
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
        Raises an OnexError if the file is missing or invalid.
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
        Raises an OnexError if the file is missing or invalid.
        """
        try:
            with path.open("r") as f:
                data = json.load(f)
            return SchemaModel(**data)
        except Exception as e:
            raise OmniBaseError(f"Failed to load JSON schema: {path}: {e}")

    def load_schema_for_node(self, node: NodeMetadataBlock) -> dict[str, Any]:
        """
        Load schema for a specific node.
        TODO: Implement proper schema loading logic in M1+.
        """
        # Placeholder implementation - return empty dict for now
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"Schema loading for node {node.name} not yet implemented",
            node_id="schema_loader",
        )
        return {}

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
                    emit_log_event(
                        LogLevelEnum.INFO,
                        f"Discovered schema: {file}",
                        node_id="schema_loader",
                    )
                    discovered.append(file)
                except Exception as e:
                    emit_log_event(
                        LogLevelEnum.WARNING,
                        f"Warning: Malformed schema file skipped: {file}: {e}",
                        node_id="schema_loader",
                    )
        # TODO: M1+ register schemas here
        return discovered

    # TODO: Add recursive directory scanning and schema auto-registration in M1+
