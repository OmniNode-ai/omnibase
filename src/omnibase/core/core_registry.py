# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "base_registry"
# namespace: "omninode.tools.base_registry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "base_registry.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolRegistry']
# base_class: ['ProtocolRegistry']
# mock_safe: true
# === /OmniNode:Metadata ===


"""
BaseRegistry implements ProtocolRegistry for all registries.
Supports register, get, list, and subscript access.
"""
from typing import Any, Dict, List, Optional

from omnibase.core.errors import OmniBaseError
from omnibase.model.model_enum_metadata import NodeMetadataField
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.protocol.protocol_registry import ProtocolRegistry

# M0 milestone: This file will be replaced by SchemaRegistry stub implementing ProtocolRegistry with loader methods and get_node.
# Remove legacy/unused methods and prepare for SchemaRegistry implementation as per milestone 0 checklist.


class BaseRegistry(ProtocolRegistry):
    def __init__(self):
        self._registry: Dict[str, Any] = {}

    def register(self, name: str, obj: Any) -> None:
        self._registry[name] = obj

    def get(self, name: str) -> Optional[Any]:
        return self._registry.get(name)

    def list(self) -> List[str]:
        return list(self._registry.keys())

    def __getitem__(self, name: str) -> Any:
        return self._registry[name]

    def __contains__(self, name: str) -> bool:
        return name in self._registry


class SchemaRegistry(ProtocolRegistry):
    """
    M0 stub implementation of ProtocolRegistry for schema/node registries.
    Implements loader methods and get_node as per milestone 0 checklist and canonical template.
    """

    def __init__(self):
        self._schemas = {}  # Placeholder for schema storage

    @classmethod
    def load_from_disk(cls) -> "ProtocolRegistry":
        # Stub: Placeholder for M1 schema loading logic
        print("Stub: Loading schemas from disk")
        instance = cls()
        # In M0, load the minimal onex_node.yaml and state_contract.json stubs
        # In M1+, load all schemas and register them
        return instance

    @classmethod
    def load_mock(cls) -> "ProtocolRegistry":
        # Stub: Placeholder for M1 mock schema loading logic
        print("Stub: Loading mock schemas")
        instance = cls()
        # In M0, add minimal stub data or loaded stub schemas
        return instance

    def get_node(self, node_id: str) -> dict:
        print(f"Stub: Getting node {node_id}")
        # For M0, only 'example_node_id' is considered present
        if node_id != "example_node_id":
            raise OmniBaseError(f"Node not found: {node_id}")
        # Build stub node with all required fields from NodeMetadataField
        node = {
            field.value: self._stub_value_for_field(field, node_id)
            for field in NodeMetadataField.required()
        }
        # Add a stub marker for test assertions
        node["stub"] = True
        # Optionally add optional fields as None/empty if needed
        for field in NodeMetadataField.optional():
            node[field.value] = self._stub_value_for_field(
                field, node_id, optional=True
            )
        return node

    @staticmethod
    def _stub_value_for_field(field, node_id, optional=False):
        # Provide dummy values for each field
        if field == NodeMetadataField.NODE_ID:
            return node_id
        elif field == NodeMetadataField.NODE_TYPE:
            return "tool"
        elif field == NodeMetadataField.VERSION_HASH:
            return "stub-version-hash"
        elif field == NodeMetadataField.ENTRY_POINT:
            return {"type": "python", "path": "stub.py"}
        elif field == NodeMetadataField.CONTRACT_TYPE:
            return "io_schema"
        elif field == NodeMetadataField.CONTRACT:
            return {"inputs": {}, "outputs": {}}
        # Optional fields: return None or empty as appropriate
        elif field == NodeMetadataField.STATE_CONTRACT:
            return None
        elif field == NodeMetadataField.TRUST_SCORE:
            return None
        elif field == NodeMetadataField.TAGS:
            return []
        elif field == NodeMetadataField.DESCRIPTION:
            return "Stub node for testing."
        elif field == NodeMetadataField.SANDBOX_SIGNATURE:
            return None
        elif field == NodeMetadataField.DEPENDENCIES:
            return []
        elif field == NodeMetadataField.CAPABILITIES:
            return []
        elif field == NodeMetadataField.X_EXTENSIONS:
            return {}
        return None

    def discover_plugins(self) -> list[NodeMetadataBlock]:
        """
        Returns a list of plugin metadata blocks associated with this registry.
        Supports ONEX plugin discovery, contract introspection, and version tracking.
        This is a stub interface; implementers must comply with ONEX sandboxing/versioning rules.
        See ONEX protocol spec and Cursor Rule for required fields and extension policy.
        """
        # M0: Return a stub node metadata block for demonstration
        stub_node = NodeMetadataBlock(
            node_id="stub_plugin",
            node_type="plugin",
            version_hash="v0.0.1-stub",
            entry_point=None,  # Should be EntrypointBlock, update as needed
            contract_type="custom",
            contract={},
        )
        return [stub_node]
