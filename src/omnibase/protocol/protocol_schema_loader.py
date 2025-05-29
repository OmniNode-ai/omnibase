# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.142263'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_schema_loader.py
# hash: 74ece73bf7240a41dd656f3bdb6c0e974578446fdfa2a7f5ac6583848953236b
# last_modified_at: '2025-05-29T11:50:12.184572+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_schema_loader.py
# namespace: omnibase.protocol_schema_loader
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 5563978b-75f9-4c23-bca7-70ba09837d66
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
ProtocolSchemaLoader: Protocol for all ONEX schema loader implementations.
Defines the canonical loader interface for node metadata and JSON schema files.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock

from omnibase.model.model_schema import SchemaModel


class ProtocolSchemaLoader(Protocol):
    """
    Protocol for ONEX schema loaders.
    All methods use Path objects and return strongly-typed models as appropriate.
    """

    def load_onex_yaml(self, path: Path) -> "NodeMetadataBlock": ...
    def load_json_schema(self, path: Path) -> SchemaModel: ...

    def load_schema_for_node(self, node: "NodeMetadataBlock") -> dict[str, Any]: ...
