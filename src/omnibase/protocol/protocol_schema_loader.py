# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_schema_loader.py
# version: 1.0.0
# uuid: d804440e-9245-4efb-b09e-5b3d36e98367
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167568
# last_modified_at: 2025-05-21T16:42:46.101470
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 9739d52e2208c6b3a832a36fdbb988443dd47cff94712b6bffb38fc2594a1b3f
# entrypoint: python@protocol_schema_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_schema_loader
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
