# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: core_registry.py
# version: 1.0.0
# uuid: f62f7393-2440-486d-8b80-81d8af8f032b
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.163499
# last_modified_at: 2025-05-21T16:42:46.069610
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: f8011b18d84557fb846a6d84a76c38d6f50e0c45723315acd0b93e4df900a7eb
# entrypoint: {'type': 'python', 'target': 'core_registry.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.core_registry
# meta_type: tool
# === /OmniNode:Metadata ===

"""
BaseRegistry implements ProtocolRegistry for all registries.
Supports register, get, list, and subscript access.
"""

from typing import Any, List, Optional

from omnibase.core.errors import OmniBaseError
from omnibase.model.model_enum_metadata import NodeMetadataField
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaType,
    NodeMetadataBlock,
)
from omnibase.protocol.protocol_registry import ProtocolRegistry

# M0 milestone: This file will be replaced by SchemaRegistry stub implementing ProtocolRegistry with loader methods and get_node.
# Remove legacy/unused methods and prepare for SchemaRegistry implementation as per milestone 0 checklist.


class BaseRegistry(ProtocolRegistry):
    def __init__(self) -> None:
        self._registry: dict[str, Any] = {}

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

    def __init__(self) -> None:
        self._schemas: dict[str, Any] = {}  # Placeholder for schema storage

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

    def get_node(self, node_id: str) -> dict[str, Any]:
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
        # Fix: entrypoint must be EntrypointBlock, not dict
        if "entry_point" in node and isinstance(node["entry_point"], dict):
            node["entry_point"] = EntrypointBlock(
                type=EntrypointType.PYTHON, target="src/omnibase/tools/stub.py"
            )
        return node

    @staticmethod
    def _stub_value_for_field(
        field: NodeMetadataField, node_id: str, optional: bool = False
    ) -> Any:
        # Provide dummy values for each field
        if field == NodeMetadataField.NODE_ID:
            return node_id
        elif field == NodeMetadataField.NODE_TYPE:
            return "tool"
        elif field == NodeMetadataField.VERSION_HASH:
            return "stub-version-hash"
        elif field == NodeMetadataField.ENTRY_POINT:
            return {"type": "python", "target": "stub.py"}
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
            metadata_version="0.0.1",
            protocol_version="0.0.1",
            owner="OmniNode Team",
            copyright="Copyright OmniNode",
            schema_version="0.0.1",
            name="Stub Plugin",
            version="0.0.1",
            uuid="00000000-0000-0000-0000-000000000000",
            author="OmniNode Team",
            created_at="2024-01-01T00:00:00Z",
            last_modified_at="2024-01-01T00:00:00Z",
            description="Stub plugin for demonstration",
            state_contract="stub://contract",
            lifecycle=Lifecycle.DRAFT,
            hash="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            entrypoint=EntrypointBlock(
                type=EntrypointType.PYTHON, target="src/omnibase/tools/stub.py"
            ),
            namespace="omninode.stub",
            meta_type=MetaType.PLUGIN,
        )
        return [stub_node]


class FileTypeRegistry:
    """
    Registry for eligible file types for stamping. Supports DI and extension.
    """

    def __init__(self) -> None:
        self._registry: dict[str, list[str]] = {}
        # Register default eligible file extensions
        self.register("python", [".py"])
        self.register("markdown", [".md"])
        self.register("yaml", [".yaml", ".yml"])
        self.register("json", [".json"])

    def get_all_extensions(self) -> list[str]:
        """Return a flat list of all registered file extensions."""
        exts = []
        for ext_list in self._registry.values():
            exts.extend(ext_list)
        return exts

    def add_file_type(self, name: str, extensions: list[str]) -> None:
        """Register a new file type with its extensions."""
        self.register(name, extensions)

    def register(self, name: str, extensions: list[str]) -> None:
        self._registry[name] = extensions
