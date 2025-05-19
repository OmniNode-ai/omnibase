# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 2526b5e5-71da-4e11-ac5c-f937184da89a
# name: protocol_schema_loader.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:59.470069
# last_modified_at: 2025-05-19T16:19:59.470072
# description: Stamped Python file: protocol_schema_loader.py
# state_contract: none
# lifecycle: active
# hash: 7e1ea4ef4f2c5a321a087ba28a5796ef3c64b0fcbcdf7b6b53e242978a6449d8
# entrypoint: {'type': 'python', 'target': 'protocol_schema_loader.py'}
# namespace: onex.stamped.protocol_schema_loader.py
# meta_type: tool
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
