# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: dummy_schema_loader.py
# version: 1.0.0
# uuid: 95106abb-21b2-49b9-93e1-bc2ccecbc600
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.537397
# last_modified_at: 2025-05-28T17:20:04.410132
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: c3edc215f0a836a796ed384bce8117a9f33234015383399f1cb2b93a58e44b85
# entrypoint: python@dummy_schema_loader.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.dummy_schema_loader
# meta_type: tool
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
