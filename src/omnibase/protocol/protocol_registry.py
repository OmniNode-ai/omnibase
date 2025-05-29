# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.276226'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_registry
# hash: a08694d4a43c239f7653f23bcaf0645dcc77cc1b8afeeaec3f1bceecfafc579b
# last_modified_at: '2025-05-29T14:14:00.324643+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_registry.py
# namespace: python://omnibase.protocol.protocol_registry
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 8664087b-f756-490a-914c-4bb9c21cac98
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Shared Registry Protocol.

Provides a cross-cutting interface for registry functionality without exposing
node-specific implementation details. This protocol abstracts registry operations
to enable testing and cross-node registry access while maintaining proper
architectural boundaries.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Protocol

from omnibase.enums import OnexStatus


class RegistryArtifactType(str, Enum):
    """Shared enumeration of registry artifact types."""

    NODES = "nodes"
    CLI_TOOLS = "cli_tools"
    RUNTIMES = "runtimes"
    ADAPTERS = "adapters"
    CONTRACTS = "contracts"
    PACKAGES = "packages"


class RegistryArtifactInfo:
    """
    Shared artifact information model.

    Provides essential artifact information without exposing node-specific
    implementation details.
    """

    def __init__(
        self,
        name: str,
        version: str,
        artifact_type: RegistryArtifactType,
        path: str,
        metadata: Dict[str, Any],
        is_wip: bool = False,
    ):
        self.name = name
        self.version = version
        self.artifact_type = artifact_type
        self.path = path
        self.metadata = metadata
        self.is_wip = is_wip


class RegistryStatus:
    """
    Shared registry status information.

    Provides registry loading status without exposing node-specific models.
    """

    def __init__(
        self,
        status: OnexStatus,
        message: str,
        artifact_count: int,
        valid_artifact_count: int,
        invalid_artifact_count: int,
        wip_artifact_count: int,
        artifact_types_found: List[RegistryArtifactType],
    ):
        self.status = status
        self.message = message
        self.artifact_count = artifact_count
        self.valid_artifact_count = valid_artifact_count
        self.invalid_artifact_count = invalid_artifact_count
        self.wip_artifact_count = wip_artifact_count
        self.artifact_types_found = artifact_types_found


class ProtocolRegistry(Protocol):
    """
    Cross-cutting registry protocol.

    Provides an interface for registry operations that can be implemented
    by different registry backends (registry loader node, mock registries, etc.)
    without exposing implementation-specific details.
    """

    def get_status(self) -> RegistryStatus:
        """Get registry loading status and statistics."""
        ...

    def get_artifacts(self) -> List[RegistryArtifactInfo]:
        """Get all artifacts in the registry."""
        ...

    def get_artifacts_by_type(
        self, artifact_type: RegistryArtifactType
    ) -> List[RegistryArtifactInfo]:
        """Get artifacts filtered by type."""
        ...

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
        ...

    def has_artifact(
        self, name: str, artifact_type: Optional[RegistryArtifactType] = None
    ) -> bool:
        """Check if an artifact exists in the registry."""
        ...
