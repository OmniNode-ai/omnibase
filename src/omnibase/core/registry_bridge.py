# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: registry_bridge.py
# version: 1.0.0
# uuid: 9c1472b3-f0f6-48eb-8803-9332010acf1d
# author: OmniNode Team
# created_at: 2025-05-24T16:36:30.928744
# last_modified_at: 2025-05-24T21:01:08.725946
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: e3b84228e6e47672126353c022208332142b55f3e72a672d55bc1d2125c306b5
# entrypoint: python@registry_bridge.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.registry_bridge
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Registry Bridge - Adapter between old ProtocolRegistry interface and new registry loader node.

This bridge allows existing code to continue using the ProtocolRegistry interface
while internally using the new registry loader node implementation.

Migration Strategy:
1. Bridge maintains old interface for backward compatibility
2. Internally uses new registry loader node for actual functionality  
3. Gradual migration of calling code to use registry loader node directly
4. Eventually remove bridge and old interface

This enables a smooth transition without breaking existing tests and code.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the registry loader node to the path for importing
sys.path.insert(
    0, str(Path(__file__).parent.parent / "nodes" / "registry_loader_node" / "v1_0_0")
)


from omnibase.protocol.protocol_registry import ProtocolRegistry


class RegistryBridge(ProtocolRegistry):
    """
    Bridge adapter that uses the new registry loader node while maintaining
    the old ProtocolRegistry interface for backward compatibility.
    """

    def __init__(
        self,
        root_path: Optional[Path] = None,
        onextree_path: Optional[Path] = None,
        mock_mode: bool = False,
    ) -> None:
        """
        Initialize registry bridge.

        Args:
            root_path: Root directory path for registry loading
            onextree_path: Path to .onextree file (optional)
            mock_mode: If True, skip loading and use mock data
        """
        self.root_path = root_path or Path.cwd() / "src" / "omnibase"
        self.onextree_path = onextree_path or Path.cwd() / ".onextree"
        self.registry_path: Optional[Path] = None  # For test compatibility
        self.mock_mode = mock_mode
        self._output_state: Optional[Any] = None

        if not mock_mode:
            self._load_registry()

    def _load_registry(self) -> None:
        """Load the registry using the registry loader node."""
        try:
            from omnibase.nodes.registry_loader_node.v1_0_0.models.state import (
                RegistryLoaderInputState,
            )
            from omnibase.nodes.registry_loader_node.v1_0_0.node import (
                run_registry_loader_node,
            )

            # Use configured paths for testing or defaults for normal operation
            root_dir = str(self.root_path)
            onextree_path = str(self.onextree_path)

            # Create input state for registry loader node
            input_state = RegistryLoaderInputState(
                version="1.0.0",
                root_directory=root_dir,
                onextree_path=onextree_path,
                include_wip=True,  # Include WIP artifacts for compatibility
                artifact_types=None,
            )

            # Call the registry loader node
            output_state = run_registry_loader_node(input_state)

            # Convert to old format for compatibility
            artifacts_by_type = {}
            for artifact in output_state.artifacts:
                artifact_type = artifact.artifact_type.value
                if artifact_type not in artifacts_by_type:
                    artifacts_by_type[artifact_type] = {}

                if artifact.name not in artifacts_by_type[artifact_type]:
                    artifacts_by_type[artifact_type][artifact.name] = {}

                artifacts_by_type[artifact_type][artifact.name][artifact.version] = {
                    "path": artifact.path,
                    "metadata": artifact.metadata,
                    "is_wip": artifact.is_wip,
                    "lifecycle": "wip" if artifact.is_wip else "active",
                    **artifact.metadata,  # Include metadata fields
                }

            # Create compatible output state
            # For backward compatibility, convert WARNING to SUCCESS if artifacts were loaded
            compatible_status = output_state.status.value
            if (
                output_state.status.value == "warning"
                and output_state.artifact_count > 0
            ):
                compatible_status = "success"

            self._output_state = type(
                "CompatibleOutput",
                (),
                {
                    "status": compatible_status,
                    "message": output_state.message,
                    "total_artifacts": output_state.artifact_count,
                    "valid_artifacts": output_state.valid_artifact_count,
                    "invalid_artifacts": output_state.invalid_artifact_count,
                    "wip_artifacts": output_state.wip_artifact_count,
                    "artifacts_by_type": artifacts_by_type,
                    "registry_stats": {
                        "total": output_state.artifact_count,
                        "valid": output_state.valid_artifact_count,
                        "invalid": output_state.invalid_artifact_count,
                        "wip": output_state.wip_artifact_count,
                    },
                    "onextree_validation": {
                        "valid": len(output_state.errors) == 0,
                        "reason": (
                            "No errors"
                            if len(output_state.errors) == 0
                            else f"{len(output_state.errors)} errors found"
                        ),
                        "missing_artifacts": [],  # Add missing fields for compatibility
                        "extra_artifacts": [],
                    },
                },
            )()

        except Exception as e:
            # Create error state for compatibility
            from omnibase.core.errors import OmniBaseError

            raise OmniBaseError(f"Failed to load registry: {str(e)}")

    def reload_registry(self) -> None:
        """Reload the registry (useful for testing)."""
        if not self.mock_mode:
            self._load_registry()

    @classmethod
    def load_from_disk(cls, root_path: Optional[Path] = None) -> "ProtocolRegistry":
        """Load registry from disk."""
        return cls(root_path=root_path, mock_mode=False)

    @classmethod
    def load_mock(cls) -> "ProtocolRegistry":
        """Load mock registry for testing."""
        instance = cls(mock_mode=True)

        # Import here to avoid circular imports
        from omnibase.model.model_enum_metadata import NodeMetadataField

        # Create mock node data with all required and optional fields
        mock_node_data = {
            "path": "/mock/path",
            "metadata": {
                "name": "example_node_id",
                "version": "v1_0_0",
                "description": "Mock node for testing",
            },
            "is_wip": False,
            "lifecycle": "active",
            "stub": True,  # Required by test
        }

        # Add all required fields
        for field in NodeMetadataField.required():
            if field.value not in mock_node_data:
                if field == NodeMetadataField.NODE_ID:
                    mock_node_data[field.value] = "example_node_id"
                elif field == NodeMetadataField.NODE_TYPE:
                    mock_node_data[field.value] = "tool"
                elif field == NodeMetadataField.VERSION_HASH:
                    mock_node_data[field.value] = "mock-hash-123"
                elif field == NodeMetadataField.ENTRY_POINT:
                    mock_node_data[field.value] = {
                        "type": "python",
                        "target": "mock.py",
                    }
                elif field == NodeMetadataField.CONTRACT_TYPE:
                    mock_node_data[field.value] = "io_schema"
                elif field == NodeMetadataField.CONTRACT:
                    mock_node_data[field.value] = {"inputs": {}, "outputs": {}}
                elif field == NodeMetadataField.HASH:
                    mock_node_data[field.value] = "mock-hash-456"
                elif field == NodeMetadataField.LAST_MODIFIED_AT:
                    mock_node_data[field.value] = "2024-01-01T00:00:00Z"

        # Add all optional fields
        for field in NodeMetadataField.optional():
            if field.value not in mock_node_data:
                if field == NodeMetadataField.STATE_CONTRACT:
                    mock_node_data[field.value] = None
                elif field == NodeMetadataField.TRUST_SCORE:
                    mock_node_data[field.value] = None
                elif field == NodeMetadataField.TAGS:
                    mock_node_data[field.value] = []
                elif field == NodeMetadataField.DESCRIPTION:
                    mock_node_data[field.value] = "Mock node for testing"
                elif field == NodeMetadataField.SANDBOX_SIGNATURE:
                    mock_node_data[field.value] = None
                elif field == NodeMetadataField.DEPENDENCIES:
                    mock_node_data[field.value] = []
                elif field == NodeMetadataField.CAPABILITIES:
                    mock_node_data[field.value] = []
                elif field == NodeMetadataField.X_EXTENSIONS:
                    mock_node_data[field.value] = {}

        # Create mock stamper node data with correct node_id
        mock_stamper_data = {
            "node_id": "stamper_node",
            "node_type": "tool",
            "version": "v1_0_0",
            "path": "/mock/path/stamper_node",
            "entry_point": {"type": "python", "target": "mock.py"},
            "contract_type": "io_schema",
            "contract": {"inputs": {}, "outputs": {}},
            "description": "Mock stamper node for testing",
            "lifecycle": "active",
            "metadata": {
                "name": "stamper_node",
                "version": "v1_0_0",
                "description": "Mock stamper node for testing",
            },
            "is_wip": False,
            "stub": True,  # Required by test
        }

        # Add all required and optional fields
        for field in NodeMetadataField.required() + NodeMetadataField.optional():
            if field.value not in mock_stamper_data:
                if field == NodeMetadataField.VERSION_HASH:
                    mock_stamper_data[field.value] = "mock-hash-123"
                elif field == NodeMetadataField.HASH:
                    mock_stamper_data[field.value] = "mock-hash-456"
                elif field == NodeMetadataField.LAST_MODIFIED_AT:
                    mock_stamper_data[field.value] = "2024-01-01T00:00:00Z"
                elif field == NodeMetadataField.STATE_CONTRACT:
                    mock_stamper_data[field.value] = None
                elif field == NodeMetadataField.TRUST_SCORE:
                    mock_stamper_data[field.value] = None
                elif field == NodeMetadataField.TAGS:
                    mock_stamper_data[field.value] = []
                elif field == NodeMetadataField.SANDBOX_SIGNATURE:
                    mock_stamper_data[field.value] = None
                elif field == NodeMetadataField.DEPENDENCIES:
                    mock_stamper_data[field.value] = []
                elif field == NodeMetadataField.CAPABILITIES:
                    mock_stamper_data[field.value] = []
                elif field == NodeMetadataField.X_EXTENSIONS:
                    mock_stamper_data[field.value] = {}

        # Set mock data that includes both example_node_id and stamper_node for compatibility
        instance._output_state = type(
            "MockOutput",
            (),
            {
                "status": "success",
                "message": "Mock registry loaded",
                "total_artifacts": 2,
                "valid_artifacts": 2,
                "invalid_artifacts": 0,
                "wip_artifacts": 0,
                "artifacts_by_type": {
                    "nodes": {
                        "example_node_id": {"v1_0_0": mock_node_data},
                        "stamper_node": {"v1_0_0": mock_stamper_data},
                    }
                },
                "registry_stats": {"total": 2, "valid": 2},
                "onextree_validation": {
                    "valid": True,
                    "reason": "Mock validation",
                    "missing_artifacts": [],
                    "extra_artifacts": [],
                },
            },
        )()
        return instance

    def get_node(self, node_id: str) -> Dict[str, Any]:
        """
        Get node metadata by ID.

        Args:
            node_id: The node identifier

        Returns:
            Node metadata dictionary

        Raises:
            OmniBaseError: If node not found or registry not loaded
        """
        if not self._output_state or self._output_state.status == "error":
            from omnibase.core.errors import OmniBaseError

            raise OmniBaseError("Registry not loaded or in error state")

        # Search for node in artifacts_by_type
        nodes = self._output_state.artifacts_by_type.get("nodes", {})
        for node_name, versions in nodes.items():
            if node_name == node_id:
                # Return the latest version or first available
                if versions:
                    latest_version = max(versions.keys())
                    node_data = versions[latest_version]
                    # Add standard fields expected by old interface
                    return {
                        "node_id": node_id,
                        "node_type": "tool",  # Default type
                        "version": latest_version,
                        "path": node_data.get("path", ""),
                        "entry_point": node_data.get("entry_point", {}),
                        "contract_type": node_data.get("contract_type", "io_schema"),
                        "contract": node_data.get("contract", {}),
                        "description": node_data.get("description", ""),
                        "lifecycle": node_data.get("lifecycle", "active"),
                        **node_data,  # Include any additional fields
                    }

        from omnibase.core.errors import OmniBaseError

        raise OmniBaseError(f"Node not found: {node_id}")

    def discover_plugins(self) -> List[Any]:
        """Discover plugins from loaded registry."""
        if not self._output_state or self._output_state.status == "error":
            return []

        # Return all nodes as plugins for compatibility
        plugins = []
        nodes = self._output_state.artifacts_by_type.get("nodes", {})
        for node_name, versions in nodes.items():
            for version, node_data in versions.items():
                plugins.append({"node_id": node_name, "version": version, **node_data})
        return plugins

    def get_artifacts_by_type(self, artifact_type: str) -> List[Any]:
        """Get artifacts by type."""
        if not self._output_state or self._output_state.status == "error":
            return []

        artifacts = []
        type_data = self._output_state.artifacts_by_type.get(artifact_type, {})
        for name, versions in type_data.items():
            for version, data in versions.items():
                # Create artifact object with metadata attribute for compatibility
                artifact = type(
                    "Artifact",
                    (),
                    {
                        "name": name,
                        "version": version,
                        "type": artifact_type,
                        "metadata": data.get("metadata", {}),
                        "is_wip": data.get("is_wip", False),
                        "path": data.get("path", ""),
                        "lifecycle": data.get("lifecycle", "active"),
                        **data,
                    },
                )()
                artifacts.append(artifact)
        return artifacts

    def get_artifact_by_name_and_version(
        self, name: str, version: str, artifact_type: Optional[str] = None
    ) -> Optional[Any]:
        """Get specific artifact by name and version."""
        if not self._output_state or self._output_state.status == "error":
            return None

        # Search in specified type or all types
        if artifact_type:
            types_to_search = [artifact_type]
        else:
            types_to_search = list(self._output_state.artifacts_by_type.keys())

        for atype in types_to_search:
            type_data = self._output_state.artifacts_by_type.get(atype, {})
            if name in type_data and version in type_data[name]:
                data = type_data[name][version]
                return {"name": name, "version": version, "type": atype, **data}
        return None

    def get_all_artifacts(self) -> Dict[str, Any]:
        """Get all artifacts."""
        if not self._output_state or self._output_state.status == "error":
            return {}

        return self._output_state.artifacts_by_type

    def get_wip_artifacts(self) -> List[Any]:
        """Get WIP artifacts."""
        if not self._output_state or self._output_state.status == "error":
            return []

        # Filter artifacts marked as WIP
        wip_artifacts = []
        for artifact_type, type_data in self._output_state.artifacts_by_type.items():
            for name, versions in type_data.items():
                for version, data in versions.items():
                    if data.get("is_wip", False) or data.get("lifecycle") == "wip":
                        # Create artifact object for compatibility
                        artifact = type(
                            "Artifact",
                            (),
                            {
                                "name": name,
                                "version": version,
                                "type": artifact_type,
                                "is_wip": True,
                                "metadata": data.get("metadata", {}),
                                **data,
                            },
                        )()
                        wip_artifacts.append(artifact)
        return wip_artifacts

    def validate_against_onextree(
        self, onextree_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Validate against .onextree file."""
        if not self._output_state:
            return {
                "valid": False,
                "reason": "Registry not loaded",
                "missing_artifacts": [],
                "extra_artifacts": [],
            }

        return self._output_state.onextree_validation

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        if not self._output_state:
            return {
                "total_artifacts": 0,
                "valid_artifacts": 0,
                "invalid_artifacts": 0,
                "wip_artifacts": 0,
            }

        return {
            "total_artifacts": self._output_state.total_artifacts,
            "valid_artifacts": self._output_state.valid_artifacts,
            "invalid_artifacts": self._output_state.invalid_artifacts,
            "wip_artifacts": self._output_state.wip_artifacts,
            **self._output_state.registry_stats,
        }

    def get_load_result(self) -> Any:
        """Get the raw load result (for compatibility with old tests)."""
        return self._output_state

    def _load_registry_data(self) -> Any:
        """Internal method for compatibility with old tests."""
        # Reload the registry when called (for test compatibility)
        if not self.mock_mode:
            self.reload_registry()
        return self._output_state
