# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 88ea27ee-c22a-42e6-9eb7-81b279639753
# name: protocol_registry.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:55.748188
# last_modified_at: 2025-05-19T16:19:55.748190
# description: Stamped Python file: protocol_registry.py
# state_contract: none
# lifecycle: active
# hash: 1de4c8aaa4f8a2860e0b6933721c62e46c08709f9a88bb16e6f37a4f7ac24a0c
# entrypoint: {'type': 'python', 'target': 'protocol_registry.py'}
# namespace: onex.stamped.protocol_registry.py
# meta_type: tool
# === /OmniNode:Metadata ===

"""
ProtocolRegistry: Canonical ONEX protocol for schema and node registries.

- This protocol supersedes any prior 'RegistryProtocol' or generic 'ProtocolRegistry' definitions.
- Loader methods are classmethods (using cls), as required by ONEX canonical templates and docs.
- get_node returns a dict for M0 (see node_contracts.md and milestone 0 checklist); M1+ should migrate to returning a Pydantic model.
- See docs/nodes/protocol_definitions.md and templates_scaffolding.md for rationale and usage.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Protocol

if TYPE_CHECKING:
    from omnibase.model.model_node_metadata import NodeMetadataBlock


class ProtocolRegistry(Protocol):
    """
    Protocol for schema and node registries in ONEX.

    Loader methods are classmethods. For M0, get_node returns a dict; for M1+, migrate to a Pydantic model.

    Example:
        class SchemaRegistry:
            @classmethod
            def load_from_disk(cls) -> 'ProtocolRegistry':
                ...
            @classmethod
            def load_mock(cls) -> 'ProtocolRegistry':
                ...
            def get_node(self, node_id: str) -> dict:
                ...
    """

    @classmethod
    def load_from_disk(cls) -> "ProtocolRegistry": ...
    @classmethod
    def load_mock(cls) -> "ProtocolRegistry": ...
    def get_node(self, node_id: str) -> Dict[str, Any]: ...
    def discover_plugins(self) -> List["NodeMetadataBlock"]:
        """
        Returns a list of plugin metadata blocks associated with this registry.
        Supports ONEX plugin discovery, contract introspection, and version tracking.
        This is a stub interface; implementers must comply with ONEX sandboxing/versioning rules.
        See ONEX protocol spec and Cursor Rule for required fields and extension policy.
        """
        ...
