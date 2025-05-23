# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: dummy_schema_loader.py
# version: 1.0.0
# uuid: 4a2c3b43-8917-4854-a319-3d81ef7609e0
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.172575
# last_modified_at: 2025-05-21T16:42:46.043643
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 9ad8d041c1e68359001001bcf661f9b64ab117c7ce25e56ca4f5a2195a8db322
# entrypoint: python@dummy_schema_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.dummy_schema_loader
# meta_type: tool
# === /OmniNode:Metadata ===


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
