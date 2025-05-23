# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_registry.py
# version: 1.0.0
# uuid: 4d692b35-6840-4a2c-a4f4-dc82659721f7
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167506
# last_modified_at: 2025-05-21T16:42:46.081275
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 5e0104f5bd03e86526f2307ecd75c68fe57ef07e7af6299604924e6bf92b3c7e
# entrypoint: python@protocol_registry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_registry
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
