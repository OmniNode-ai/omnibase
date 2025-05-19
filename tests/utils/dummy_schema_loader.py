# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 9cd62ac9-f640-4a3f-991a-5fd76e76f418
# name: dummy_schema_loader.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:53.235716
# last_modified_at: 2025-05-19T16:19:53.235721
# description: Stamped Python file: dummy_schema_loader.py
# state_contract: none
# lifecycle: active
# hash: c33b4b51ba0462a0ffd2071c55f4f10c311ad432041b0bf79e932ac68fd757b1
# entrypoint: {'type': 'python', 'target': 'dummy_schema_loader.py'}
# namespace: onex.stamped.dummy_schema_loader.py
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
