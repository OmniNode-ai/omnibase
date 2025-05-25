# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: dummy_schema_loader.py
# version: 1.0.0
# uuid: 49f11e2e-db07-4573-9be8-dacd01bd3d08
# author: OmniNode Team
# created_at: 2025-05-25T07:56:53.326152
# last_modified_at: 2025-05-25T12:33:15.581626
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 18499f6e0f18df7d507f87acf965b49d4a441c36089aca7f065c3bab0ee32380
# entrypoint: python@dummy_schema_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.dummy_schema_loader
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
