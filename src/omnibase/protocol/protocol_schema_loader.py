"""
ProtocolSchemaLoader: Protocol for all ONEX schema loader implementations.
Defines the canonical loader interface for node metadata and JSON schema files.
"""
from typing import Protocol
from pathlib import Path
from omnibase.model.model_metadata import MetadataBlockModel
from omnibase.model.model_schema import SchemaModel

class ProtocolSchemaLoader(Protocol):
    """
    Protocol for ONEX schema loaders.
    All methods use Path objects and return strongly-typed models as appropriate.
    """
    def load_onex_yaml(self, path: Path) -> MetadataBlockModel:
        ...
    def load_json_schema(self, path: Path) -> SchemaModel:
        ... 