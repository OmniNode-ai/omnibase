"""
ProtocolSchemaLoader: Protocol for all ONEX schema loader implementations.
Defines the canonical loader interface for node metadata and JSON schema files.
"""

from pathlib import Path
from typing import Protocol

from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_schema import SchemaModel


class ProtocolSchemaLoader(Protocol):
    """
    Protocol for ONEX schema loaders.
    All methods use Path objects and return strongly-typed models as appropriate.
    """

    def load_onex_yaml(self, path: Path) -> NodeMetadataBlock: ...
    def load_json_schema(self, path: Path) -> SchemaModel: ...
