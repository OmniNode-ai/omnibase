# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.759449'
# description: Stamped by PythonHandler
# entrypoint: python://loader.py
# hash: c8d1f878dc68b60026eda655ed2fea5c1cb4dc9d1e3c682235c2574bf81271eb
# last_modified_at: '2025-05-29T11:50:12.472840+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: loader.py
# namespace: omnibase.loader
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: ccc0f8b3-0e5f-42ae-b3b3-a089092d9f96
# version: 1.0.0
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
