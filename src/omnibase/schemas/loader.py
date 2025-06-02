# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.759449'
# description: Stamped by PythonHandler
# entrypoint: python://loader
# hash: 601d7effb87d86db53dbcb78e18ed7115c3f0054ebca856e11bb26a29d1f4f4b
# last_modified_at: '2025-05-29T14:14:00.929849+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: loader.py
# namespace: python://omnibase.schemas.loader
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
from omnibase.enums import LogLevel
from omnibase.exceptions import OmniBaseError
from omnibase.model.model_node_metadata import NodeMetadataBlock, EntrypointBlock
from omnibase.model.model_schema import SchemaModel
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader
from omnibase.model.model_log_entry import LogContextModel


class SchemaLoader(ProtocolSchemaLoader):
    """
    Canonical loader for ONEX node YAML and JSON schema files.
    Implements ProtocolSchemaLoader. All methods use Path objects and return strongly-typed models as appropriate.
    TODO: Support dependency injection and loader swapping in M1+.
    """

    def __init__(self, event_bus=None):
        self._event_bus = event_bus

    def load_onex_yaml(self, path: Path) -> NodeMetadataBlock:
        """
        Load an ONEX node metadata YAML file and return a NodeMetadataBlock.
        Raises an OnexError if the file is missing or invalid.
        """
        try:
            with path.open("r") as f:
                data = yaml.safe_load(f)
            # Patch: Convert entrypoint dict to EntrypointBlock if needed
            if "entrypoint" in data and isinstance(data["entrypoint"], dict):
                data["entrypoint"] = EntrypointBlock(**data["entrypoint"])
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
        emit_log_event(
            LogLevel.DEBUG,
            f"Schema loading for node {node.name} not yet implemented",
            context=LogContextModel(calling_module=__name__, calling_function='load_schema_for_node', calling_line=__import__('inspect').currentframe().f_lineno, timestamp='auto', node_id='schema_loader'),
            node_id="schema_loader",
            event_bus=self._event_bus,
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
                        LogLevel.INFO,
                        f"Discovered schema: {file}",
                        context=LogContextModel(calling_module=__name__, calling_function='discover_schemas', calling_line=__import__('inspect').currentframe().f_lineno, timestamp='auto', node_id='schema_loader'),
                        node_id="schema_loader",
                        event_bus=self._event_bus,
                    )
                    discovered.append(file)
                except Exception as e:
                    emit_log_event(
                        LogLevel.WARNING,
                        f"Warning: Malformed schema file skipped: {file}: {e}",
                        context=LogContextModel(calling_module=__name__, calling_function='discover_schemas', calling_line=__import__('inspect').currentframe().f_lineno, timestamp='auto', node_id='schema_loader'),
                        node_id="schema_loader",
                        event_bus=self._event_bus,
                    )
        # TODO: M1+ register schemas here
        return discovered

    # TODO: Add recursive directory scanning and schema auto-registration in M1+
