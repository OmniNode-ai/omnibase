# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.537397'
# description: Stamped by PythonHandler
# entrypoint: python://dummy_schema_loader
# hash: dc96af39f49d269eae15121e4e80f582558ae2945fcd0db72d37737bf3c59d74
# last_modified_at: '2025-05-29T14:13:58.634373+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: dummy_schema_loader.py
# namespace: python://omnibase.fixtures.mocks.dummy_schema_loader
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 95106abb-21b2-49b9-93e1-bc2ccecbc600
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Canonical shared DummySchemaLoader for ProtocolSchemaLoader.
Implements all required methods as minimal stubs for use in all test fixtures.
This is the single source of truth for DummySchemaLoader - all other implementations
should be removed and imports updated to use this shared version.

Reference: docs/testing.md (fixture-injected, protocol-first testing)
"""

from pathlib import Path
from typing import Any

from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_schema import SchemaModel
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader


class DummySchemaLoader(ProtocolSchemaLoader):
    """
    Canonical dummy implementation of ProtocolSchemaLoader for use in tests and fixtures.
    Implements all required methods with minimal dummy return values.

    This implementation is designed to be protocol-compliant while providing
    predictable stub behavior for testing scenarios.
    """

    def load_json_schema(self, path: Path) -> SchemaModel:
        """Load a JSON schema from the given path. Returns empty schema model."""
        return SchemaModel.model_construct()

    def load_onex_yaml(self, path: Path) -> NodeMetadataBlock:
        """Load ONEX metadata from YAML file. Returns empty metadata block."""
        return NodeMetadataBlock.model_construct()

    def load_schema_for_node(self, node: NodeMetadataBlock) -> dict[str, Any]:
        """Load schema for a specific node. Returns empty dict."""
        return {}
