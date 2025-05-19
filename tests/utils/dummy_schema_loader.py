"""
Canonical protocol-complete DummySchemaLoader for ProtocolSchemaLoader.
Implements all required methods as minimal stubs for use in all test fixtures.
Reference: docs/testing.md (fixture-injected, protocol-first testing)
"""

from pathlib import Path

from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_schema import SchemaModel
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader


class DummySchemaLoader(ProtocolSchemaLoader):
    def load_schema_for_node(self, block: NodeMetadataBlock) -> dict:
        return {}

    def load_json_schema(self, path: Path) -> SchemaModel:
        return SchemaModel.model_construct()

    def load_onex_yaml(self, path: Path) -> NodeMetadataBlock:
        return NodeMetadataBlock.model_construct()
