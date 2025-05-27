# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: registry_adapter.py
# version: 1.0.0
# uuid: 2add3061-3b35-415e-bd55-9115cb65b207
# author: OmniNode Team
# created_at: 2025-05-25T08:26:26.647933
# last_modified_at: 2025-05-25T12:26:36.150719
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 61ef119e977962cacfc7be862347e067749a49aded58a21fe7e046bff1c2cd0e
# entrypoint: python@registry_adapter.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.registry_adapter
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Registry Adapter.

Implements the shared ProtocolRegistry interface by wrapping the registry loader node
functionality. This adapter provides a clean abstraction that hides node-specific
implementation details while enabling cross-cutting registry access.
"""

import sys
from pathlib import Path
from typing import List, Optional

# Add registry loader node to path for importing
sys.path.insert(
    0, str(Path(__file__).parent.parent / "nodes" / "registry_loader_node" / "v1_0_0")
)

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import OnexStatus

# Import registry loader node components (node-specific, only used internally)
from omnibase.nodes.registry_loader_node.v1_0_0.models.state import (
    ArtifactTypeEnum,
    RegistryArtifact,
    RegistryLoaderInputState,
    RegistryLoaderOutputState,
)
from omnibase.nodes.registry_loader_node.v1_0_0.node import run_registry_loader_node
from omnibase.protocol.protocol_registry import (
    RegistryArtifactInfo,
    RegistryArtifactType,
    RegistryStatus,
)


class RegistryAdapter:
    """
    Registry adapter implementing ProtocolRegistry interface.

    This adapter wraps the registry loader node functionality and provides
    a clean interface that hides node-specific implementation details.
    """

    def __init__(self, root_path: Optional[Path] = None, include_wip: bool = True):
        """
        Initialize registry adapter.

        Args:
            root_path: Root directory to scan for artifacts
            include_wip: Whether to include work-in-progress artifacts
        """
        self.root_path = root_path or Path.cwd() / "src" / "omnibase"
        self.include_wip = include_wip
        self._output_state: Optional[RegistryLoaderOutputState] = None
        self._load_registry()

    def _load_registry(self) -> None:
        """Load registry using registry loader node."""
        input_state = RegistryLoaderInputState(
            version="1.0.0",
            root_directory=str(self.root_path),
            include_wip=self.include_wip,
        )
        self._output_state = run_registry_loader_node(input_state)

    def _convert_artifact_type(
        self, node_type: ArtifactTypeEnum
    ) -> RegistryArtifactType:
        """Convert node-specific artifact type to shared type."""
        return RegistryArtifactType(node_type.value)

    def _convert_artifact(
        self, node_artifact: RegistryArtifact
    ) -> RegistryArtifactInfo:
        """Convert node-specific artifact to shared artifact info."""
        return RegistryArtifactInfo(
            name=node_artifact.name,
            version=node_artifact.version,
            artifact_type=self._convert_artifact_type(node_artifact.artifact_type),
            path=node_artifact.path,
            metadata=node_artifact.metadata,
            is_wip=node_artifact.is_wip,
        )

    def get_status(self) -> RegistryStatus:
        """Get registry loading status and statistics."""
        assert self._output_state is not None, "Registry not loaded"

        return RegistryStatus(
            status=self._output_state.status,
            message=self._output_state.message,
            artifact_count=self._output_state.artifact_count,
            valid_artifact_count=self._output_state.valid_artifact_count,
            invalid_artifact_count=self._output_state.invalid_artifact_count,
            wip_artifact_count=self._output_state.wip_artifact_count,
            artifact_types_found=[
                self._convert_artifact_type(t)
                for t in self._output_state.artifact_types_found
            ],
        )

    def get_artifacts(self) -> List[RegistryArtifactInfo]:
        """Get all artifacts in the registry."""
        assert self._output_state is not None, "Registry not loaded"
        return [self._convert_artifact(a) for a in self._output_state.artifacts]

    def get_artifacts_by_type(
        self, artifact_type: RegistryArtifactType
    ) -> List[RegistryArtifactInfo]:
        """Get artifacts filtered by type."""
        assert self._output_state is not None, "Registry not loaded"

        # Convert shared type to node-specific type for filtering
        node_type = ArtifactTypeEnum(artifact_type.value)

        filtered_artifacts = [
            a for a in self._output_state.artifacts if a.artifact_type == node_type
        ]
        return [self._convert_artifact(a) for a in filtered_artifacts]

    def get_artifact_by_name(
        self, name: str, artifact_type: Optional[RegistryArtifactType] = None
    ) -> RegistryArtifactInfo:
        """
        Get a specific artifact by name.

        Args:
            name: Artifact name to search for
            artifact_type: Optional type filter

        Returns:
            RegistryArtifactInfo: The found artifact

        Raises:
            OnexError: If artifact is not found
        """
        assert self._output_state is not None, "Registry not loaded"

        for artifact in self._output_state.artifacts:
            if artifact.name == name:
                if (
                    artifact_type is None
                    or artifact.artifact_type.value == artifact_type.value
                ):
                    return self._convert_artifact(artifact)

        type_filter = f" of type {artifact_type.value}" if artifact_type else ""
        raise OnexError(
            f"Artifact not found: {name}{type_filter}", CoreErrorCode.RESOURCE_NOT_FOUND
        )

    def has_artifact(
        self, name: str, artifact_type: Optional[RegistryArtifactType] = None
    ) -> bool:
        """Check if an artifact exists in the registry."""
        try:
            self.get_artifact_by_name(name, artifact_type)
            return True
        except OnexError:
            return False


class MockRegistryAdapter:
    """
    Mock registry adapter for testing.

    Provides a mock implementation of the ProtocolRegistry interface
    without requiring actual filesystem scanning.
    """

    def __init__(self) -> None:
        """Initialize the mock registry adapter."""
        self._mock_artifacts: List[RegistryArtifactInfo] = [
            RegistryArtifactInfo(
                name="stamper_node",
                version="v1_0_0",
                artifact_type=RegistryArtifactType.NODES,
                path="/mock/path/stamper_node",
                metadata={
                    "name": "stamper_node",
                    "version": "v1_0_0",
                    "description": "Mock stamper node for testing",
                },
                is_wip=False,
            ),
            RegistryArtifactInfo(
                name="tree_generator_node",
                version="v1_0_0",
                artifact_type=RegistryArtifactType.NODES,
                path="/mock/path/tree_generator_node",
                metadata={
                    "name": "tree_generator_node",
                    "version": "v1_0_0",
                    "description": "Mock tree generator node for testing",
                },
                is_wip=False,
            ),
            RegistryArtifactInfo(
                name="registry_loader_node",
                version="v1_0_0",
                artifact_type=RegistryArtifactType.NODES,
                path="/mock/path/registry_loader_node",
                metadata={
                    "name": "registry_loader_node",
                    "version": "v1_0_0",
                    "description": "Mock registry loader node for testing",
                },
                is_wip=False,
            ),
        ]

    def get_status(self) -> RegistryStatus:
        """Get mock registry status."""
        return RegistryStatus(
            status=OnexStatus.SUCCESS,
            message="Mock registry loaded successfully",
            artifact_count=len(self._mock_artifacts),
            valid_artifact_count=len(self._mock_artifacts),
            invalid_artifact_count=0,
            wip_artifact_count=0,
            artifact_types_found=[RegistryArtifactType.NODES],
        )

    def get_artifacts(self) -> List[RegistryArtifactInfo]:
        """Get all mock artifacts."""
        return self._mock_artifacts.copy()

    def get_artifacts_by_type(
        self, artifact_type: RegistryArtifactType
    ) -> List[RegistryArtifactInfo]:
        """Get mock artifacts filtered by type."""
        return [a for a in self._mock_artifacts if a.artifact_type == artifact_type]

    def get_artifact_by_name(
        self, name: str, artifact_type: Optional[RegistryArtifactType] = None
    ) -> RegistryArtifactInfo:
        """Get a specific mock artifact by name."""
        for artifact in self._mock_artifacts:
            if artifact.name == name:
                if artifact_type is None or artifact.artifact_type == artifact_type:
                    return artifact

        type_filter = f" of type {artifact_type.value}" if artifact_type else ""
        raise OnexError(
            f"Artifact not found: {name}{type_filter}", CoreErrorCode.RESOURCE_NOT_FOUND
        )

    def has_artifact(
        self, name: str, artifact_type: Optional[RegistryArtifactType] = None
    ) -> bool:
        """Check if a mock artifact exists."""
        try:
            self.get_artifact_by_name(name, artifact_type)
            return True
        except OnexError:
            return False
