# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: dummy_schema_loader.py
# version: 1.0.0
# uuid: be282627-fbea-40ba-ae91-036972e7380f
# author: OmniNode Team
# created_at: 2025-05-23T07:02:42.302672
# last_modified_at: 2025-05-23T11:04:27.637844
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: b2f6d520a1e50c1349bcda4316674384557e93d30ceb7f83fd67d7f7e021be19
# entrypoint: python@dummy_schema_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.dummy_schema_loader
# meta_type: tool
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Any

from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_schema import SchemaModel
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader


class DummySchemaLoader(ProtocolSchemaLoader):
    """
    Canonical dummy implementation of ProtocolSchemaLoader for use in tests and fixtures.
    Implements all required methods with minimal dummy return values.
    """

    def load_json_schema(self, path: Path) -> SchemaModel:
        return SchemaModel.model_construct()

    def load_onex_yaml(self, path: Path) -> NodeMetadataBlock:
        return NodeMetadataBlock.model_construct()

    def load_schema_for_node(self, node: NodeMetadataBlock) -> dict[str, Any]:
        return {}
