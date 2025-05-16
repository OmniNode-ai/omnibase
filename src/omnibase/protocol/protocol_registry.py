"""
ProtocolRegistry: Canonical ONEX protocol for schema and node registries.

- This protocol supersedes any prior 'RegistryProtocol' or generic 'ProtocolRegistry' definitions.
- Loader methods are classmethods (using cls), as required by ONEX canonical templates and docs.
- get_node returns a dict for M0 (see node_contracts.md and milestone 0 checklist); M1+ should migrate to returning a Pydantic model.
- See docs/nodes/protocol_definitions.md and templates_scaffolding.md for rationale and usage.
"""

from typing import List, Protocol

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
    def get_node(self, node_id: str) -> dict: ...
    def discover_plugins(self) -> List[NodeMetadataBlock]:
        """
        Returns a list of plugin metadata blocks associated with this registry.
        Supports ONEX plugin discovery, contract introspection, and version tracking.
        This is a stub interface; implementers must comply with ONEX sandboxing/versioning rules.
        See ONEX protocol spec and Cursor Rule for required fields and extension policy.
        """
        ...
