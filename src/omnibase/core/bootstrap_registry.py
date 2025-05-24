# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: bootstrap_registry.py
# version: 1.0.0
# uuid: 73581edd-17f6-414d-b780-4f8bd714037d
# author: OmniNode Team
# created_at: 2025-05-24T16:35:50.449998
# last_modified_at: 2025-05-24T21:01:08.725916
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: c17f2bd60ecb8762a0126d89add7083c173a4df9abeaf346be69eaf70ea805fe
# entrypoint: python@bootstrap_registry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.bootstrap_registry
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Bootstrap Registry - Minimal hardcoded registry for loading the registry loader node.

This bootstrap registry provides the minimal functionality needed to load
the registry loader node without depending on the full registry system.
It's designed to break the circular dependency where the registry loader
needs a registry to load itself.

Bootstrap Process:
1. Bootstrap registry loads registry loader node (hardcoded path)
2. Registry loader node loads full registry from registry.yaml
3. Full registry provides all other nodes and artifacts

This follows the canonical bootstrap → registry node → all other nodes pattern.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from omnibase.protocol.protocol_registry import ProtocolRegistry


class BootstrapRegistry(ProtocolRegistry):
    """
    Minimal bootstrap registry that can load only the registry loader node.

    This registry is hardcoded to know about the registry loader node location
    and provides just enough functionality to bootstrap the full registry system.
    """

    def __init__(self, root_path: Optional[Path] = None) -> None:
        """
        Initialize bootstrap registry.

        Args:
            root_path: Root path of the omnibase project. If None, uses current working directory.
        """
        self.root_path = root_path or Path.cwd()
        self._registry_loader_path = (
            self.root_path
            / "src"
            / "omnibase"
            / "nodes"
            / "registry_loader_node"
            / "v1_0_0"
        )

    @classmethod
    def load_from_disk(cls, root_path: Optional[Path] = None) -> "ProtocolRegistry":
        """Load bootstrap registry from disk (minimal implementation)."""
        return cls(root_path)

    @classmethod
    def load_mock(cls) -> "ProtocolRegistry":
        """Load mock bootstrap registry (minimal implementation)."""
        return cls()

    def get_node(self, node_id: str) -> Dict[str, Any]:
        """
        Get node metadata by ID. Only supports registry_loader_node.

        Args:
            node_id: The node identifier

        Returns:
            Node metadata dictionary

        Raises:
            ValueError: If node_id is not registry_loader_node
        """
        if node_id != "registry_loader_node":
            raise ValueError(
                f"Bootstrap registry only supports 'registry_loader_node', got: {node_id}"
            )

        # Return hardcoded metadata for registry loader node
        return {
            "node_id": "registry_loader_node",
            "node_type": "tool",
            "version": "1.0.0",
            "path": str(self._registry_loader_path),
            "entry_point": {"type": "python", "target": "node.py"},
            "contract_type": "io_schema",
            "contract": {
                "inputs": {
                    "root_dir": {
                        "type": "string",
                        "description": "Root directory path",
                    },
                    "onextree_path": {
                        "type": "string",
                        "description": "Path to .onextree file",
                    },
                },
                "outputs": {
                    "registry": {
                        "type": "object",
                        "description": "Loaded registry data",
                    },
                    "status": {"type": "string", "description": "Loading status"},
                },
            },
            "description": "Registry loader node for loading full registry from registry.yaml",
            "lifecycle": "active",
            "bootstrap": True,  # Marker to indicate this is bootstrap-loaded
        }

    def discover_plugins(self) -> List[Any]:
        """Discover plugins (bootstrap registry has none)."""
        return []

    def get_artifacts_by_type(self, artifact_type: str) -> List[Any]:
        """Get artifacts by type (bootstrap registry only has registry_loader_node)."""
        if artifact_type == "nodes":
            return [self.get_node("registry_loader_node")]
        return []

    def get_artifact_by_name_and_version(
        self, name: str, version: str, artifact_type: Optional[str] = None
    ) -> Optional[Any]:
        """Get specific artifact (bootstrap registry only has registry_loader_node)."""
        if name == "registry_loader_node" and version == "v1_0_0":
            return self.get_node("registry_loader_node")
        return None

    def get_all_artifacts(self) -> List[Any]:
        """Get all artifacts (bootstrap registry only has registry_loader_node)."""
        return [self.get_node("registry_loader_node")]

    def get_wip_artifacts(self) -> List[Any]:
        """Get WIP artifacts (bootstrap registry has none)."""
        return []

    def validate_against_onextree(
        self, onextree_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Validate against .onextree (bootstrap registry skips validation)."""
        return {
            "valid": True,
            "reason": "Bootstrap registry skips .onextree validation",
            "missing_artifacts": [],
            "extra_artifacts": [],
        }

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_artifacts": 1,
            "valid_artifacts": 1,
            "invalid_artifacts": 0,
            "wip_artifacts": 0,
            "bootstrap": True,
        }

    def is_bootstrap(self) -> bool:
        """Check if this is a bootstrap registry."""
        return True

    def get_registry_loader_node_path(self) -> Path:
        """Get the path to the registry loader node."""
        return self._registry_loader_path
