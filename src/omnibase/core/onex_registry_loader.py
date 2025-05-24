# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: onex_registry_loader.py
# version: 1.0.0
# uuid: 8b6c6b6e-4b4b-4b4b-8b6c-6b6e4b4b4b4b
# author: OmniNode Team
# created_at: 2025-05-23T10:29:04.625488
# last_modified_at: 2025-05-23T17:42:52.030520
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 8b6c6b6e4b4b4b4b8b6c6b6e4b4b4b4b8b6c6b6e4b4b4b4b8b6c6b6e4b4b4b4b
# entrypoint: python@onex_registry_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.onex_registry_loader
# meta_type: tool
# === /OmniNode:Metadata ===


"""
ONEX Registry Loader - Implements registry-based artifact discovery and loading.

This module provides the core registry loader that:
- Reads registry.yaml to discover artifacts
- Validates artifact versions using node.onex.yaml or .wip markers
- Integrates with .onextree validation
- Provides discovery and retrieval methods for all artifact types
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml
from pydantic import BaseModel, ConfigDict, Field

from omnibase.model.enum_onex_status import OnexStatus
from omnibase.protocol.protocol_registry import ProtocolRegistry

logger = logging.getLogger(__name__)


@dataclass
class ArtifactVersion:
    """Represents a single version of an artifact."""

    name: str
    version: str
    path: Path
    metadata_file: str
    status: str
    artifact_type: str
    metadata: Optional[Dict[str, Any]] = None
    is_wip: bool = False


class RegistryLoadResult(BaseModel):
    """Result of registry loading operation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    status: OnexStatus
    message: str
    artifacts: Dict[str, List[ArtifactVersion]] = Field(default_factory=dict)
    total_artifacts: int = 0
    valid_artifacts: int = 0
    invalid_artifacts: int = 0
    wip_artifacts: int = 0


class OnexRegistryLoader(ProtocolRegistry):
    """
    Registry loader that implements the documented ONEX registry behavior.

    Key behaviors:
    - Reads registry.yaml to discover artifacts
    - Validates versions by checking for node.onex.yaml or .wip markers
    - Loads and parses metadata files
    - Provides discovery and retrieval methods
    - Integrates with .onextree validation
    """

    def __init__(
        self, registry_path: Optional[Path] = None, root_path: Optional[Path] = None
    ) -> None:
        """
        Initialize the registry loader.

        Args:
            registry_path: Path to registry.yaml file (default: src/omnibase/registry/registry.yaml)
            root_path: Root path for resolving relative paths (default: current working directory)
        """
        self.root_path = root_path or Path.cwd()
        self.registry_path = (
            registry_path or self.root_path / "src/omnibase/registry/registry.yaml"
        )
        self.artifacts: Dict[str, List[ArtifactVersion]] = {}
        self.registry_data: Optional[Dict[str, Any]] = None
        self._loaded = False

    @classmethod
    def load_from_disk(cls) -> "ProtocolRegistry":
        """
        Load the registry from disk and validate all artifacts.

        Returns:
            ProtocolRegistry instance with loaded artifacts
        """
        instance = cls()
        instance._load_registry_data()
        return instance

    @classmethod
    def load_mock(cls) -> "ProtocolRegistry":
        """
        Load a mock registry for testing.

        Returns:
            ProtocolRegistry instance with mock data
        """
        instance = cls()
        instance._loaded = True
        return instance

    def get_node(self, node_id: str) -> Dict[str, Any]:
        """
        Get a node by ID.

        Args:
            node_id: The node identifier

        Returns:
            Dict containing node information
        """
        if not self._loaded:
            self._load_registry_data()

        # Search for the node in artifacts
        for artifact_list in self.artifacts.values():
            for artifact in artifact_list:
                if artifact.name == node_id:
                    return {
                        "name": artifact.name,
                        "version": artifact.version,
                        "path": str(artifact.path),
                        "metadata_file": artifact.metadata_file,
                        "status": artifact.status,
                        "artifact_type": artifact.artifact_type,
                        "metadata": artifact.metadata,
                        "is_wip": artifact.is_wip,
                    }

        return {}

    def discover_plugins(self) -> List[Any]:
        """
        Discover plugins associated with this registry.

        Returns:
            List of plugin metadata blocks
        """
        # For now, return empty list - this can be implemented later
        return []

    def _load_registry_data(self) -> RegistryLoadResult:
        """
        Internal method to load the registry from disk and validate all artifacts.

        Returns:
            RegistryLoadResult with loaded artifacts and statistics
        """
        try:
            # Load registry.yaml
            if not self.registry_path.exists():
                return RegistryLoadResult(
                    status=OnexStatus.ERROR,
                    message=f"Registry file not found: {self.registry_path}",
                    artifacts={},
                    total_artifacts=0,
                    valid_artifacts=0,
                    invalid_artifacts=0,
                    wip_artifacts=0,
                )

            with open(self.registry_path, "r") as f:
                self.registry_data = yaml.safe_load(f)

            # Process all artifact types
            self.artifacts = {}
            total_artifacts = 0
            valid_artifacts = 0
            invalid_artifacts = 0
            wip_artifacts = 0

            artifact_types = [
                "nodes",
                "cli_tools",
                "runtimes",
                "adapters",
                "contracts",
                "packages",
            ]

            for artifact_type in artifact_types:
                if (
                    self.registry_data is None
                    or artifact_type not in self.registry_data
                ):
                    continue

                self.artifacts[artifact_type] = []

                for artifact in self.registry_data[artifact_type]:
                    artifact_name = artifact["name"]

                    for version_info in artifact["versions"]:
                        total_artifacts += 1
                        version_path = self.root_path / version_info["path"]

                        # Create artifact version object
                        artifact_version = ArtifactVersion(
                            name=artifact_name,
                            version=version_info["version"],
                            path=version_path,
                            metadata_file=version_info["metadata_file"],
                            status=version_info["status"],
                            artifact_type=artifact_type,
                        )

                        # Validate the artifact version
                        validation_result = self._validate_artifact_version(
                            artifact_version
                        )

                        if validation_result["valid"]:
                            valid_artifacts += 1
                            if validation_result["is_wip"]:
                                wip_artifacts += 1
                                artifact_version.is_wip = True

                            # Load metadata if available
                            if validation_result["metadata"]:
                                artifact_version.metadata = validation_result[
                                    "metadata"
                                ]

                            self.artifacts[artifact_type].append(artifact_version)
                        else:
                            invalid_artifacts += 1
                            logger.warning(
                                f"Invalid artifact {artifact_name} v{version_info['version']}: "
                                f"{validation_result['reason']}"
                            )

            self._loaded = True

            return RegistryLoadResult(
                status=OnexStatus.SUCCESS,
                message=f"Successfully loaded {valid_artifacts}/{total_artifacts} artifacts",
                artifacts=self.artifacts,
                total_artifacts=total_artifacts,
                valid_artifacts=valid_artifacts,
                invalid_artifacts=invalid_artifacts,
                wip_artifacts=wip_artifacts,
            )

        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return RegistryLoadResult(
                status=OnexStatus.ERROR,
                message=f"Registry loading failed: {e}",
                artifacts={},
                total_artifacts=0,
                valid_artifacts=0,
                invalid_artifacts=0,
                wip_artifacts=0,
            )

    def _validate_artifact_version(
        self, artifact_version: ArtifactVersion
    ) -> Dict[str, Any]:
        """
        Validate an artifact version according to ONEX rules.

        Rules:
        1. Must have either metadata file (node.onex.yaml, etc.) OR .wip marker
        2. If metadata file exists, it must be valid YAML
        3. .wip marker takes precedence (allows incomplete artifacts)

        Args:
            artifact_version: The artifact version to validate

        Returns:
            Dict with validation results
        """
        result: Dict[str, Any] = {
            "valid": False,
            "is_wip": False,
            "metadata": None,
            "reason": "",
        }

        # Check for .wip marker first (takes precedence)
        wip_marker_path = artifact_version.path / ".wip"
        if wip_marker_path.exists():
            result["valid"] = True
            result["is_wip"] = True
            result["reason"] = "WIP marker present"
            logger.debug(
                f"Found .wip marker for {artifact_version.name} v{artifact_version.version}"
            )
            return result

        # Check for metadata file
        metadata_path = artifact_version.path / artifact_version.metadata_file
        if not metadata_path.exists():
            result["reason"] = (
                f"Missing metadata file: {artifact_version.metadata_file}"
            )
            return result

        # Try to load and parse metadata
        try:
            with open(metadata_path, "r") as f:
                metadata = yaml.safe_load(f)

            # Basic validation of metadata structure
            if not isinstance(metadata, dict):
                result["reason"] = "Metadata file is not a valid YAML dictionary"
                return result

            # Check for required fields (basic validation)
            required_fields = ["name", "version", "schema_version"]
            missing_fields = [
                field for field in required_fields if field not in metadata
            ]

            if missing_fields:
                result["reason"] = f"Missing required metadata fields: {missing_fields}"
                return result

            result["valid"] = True
            result["metadata"] = metadata
            result["reason"] = "Valid metadata file"

        except yaml.YAMLError as e:
            result["reason"] = f"Invalid YAML in metadata file: {e}"
        except Exception as e:
            result["reason"] = f"Error reading metadata file: {e}"

        return result

    def get_artifacts_by_type(self, artifact_type: str) -> List[ArtifactVersion]:
        """Get all artifacts of a specific type."""
        if not self._loaded:
            self._load_registry_data()

        return self.artifacts.get(artifact_type, [])

    def get_artifact_by_name_and_version(
        self, name: str, version: str, artifact_type: Optional[str] = None
    ) -> Optional[ArtifactVersion]:
        """Get a specific artifact by name and version."""
        if not self._loaded:
            self._load_registry_data()

        search_types = [artifact_type] if artifact_type else self.artifacts.keys()

        for atype in search_types:
            for artifact in self.artifacts.get(atype, []):
                if artifact.name == name and artifact.version == version:
                    return artifact

        return None

    def get_all_artifacts(self) -> Dict[str, List[ArtifactVersion]]:
        """Get all loaded artifacts."""
        if not self._loaded:
            self._load_registry_data()

        return self.artifacts.copy()

    def get_wip_artifacts(self) -> List[ArtifactVersion]:
        """Get all artifacts marked as WIP."""
        if not self._loaded:
            self._load_registry_data()

        wip_artifacts = []
        for artifact_list in self.artifacts.values():
            wip_artifacts.extend([a for a in artifact_list if a.is_wip])

        return wip_artifacts

    def validate_against_onextree(
        self, onextree_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Validate that all registry artifacts are present in the .onextree file.

        Args:
            onextree_path: Path to .onextree file (default: .onextree in root)

        Returns:
            Dict with validation results
        """
        if not self._loaded:
            self._load_registry_data()

        onextree_path = onextree_path or self.root_path / ".onextree"

        if not onextree_path.exists():
            return {
                "valid": False,
                "reason": f".onextree file not found: {onextree_path}",
                "missing_artifacts": [],
                "extra_artifacts": [],
            }

        try:
            # Load .onextree file
            with open(onextree_path, "r") as f:
                onextree_data = yaml.safe_load(f)

            # Extract all file paths from .onextree
            onextree_paths: Set[str] = set()
            self._extract_paths_from_onextree(onextree_data, onextree_paths)

            # Get all artifact paths from registry
            registry_paths = set()
            for artifact_list in self.artifacts.values():
                for artifact in artifact_list:
                    # Add the artifact directory path
                    relative_path = artifact.path.relative_to(self.root_path)
                    registry_paths.add(str(relative_path))

                    # Add the metadata file path
                    metadata_path = artifact.path / artifact.metadata_file
                    relative_metadata_path = metadata_path.relative_to(self.root_path)
                    registry_paths.add(str(relative_metadata_path))

            # Find missing and extra artifacts
            missing_artifacts = registry_paths - onextree_paths
            extra_artifacts = onextree_paths - registry_paths

            # Filter out non-artifact paths from extra_artifacts
            # (only consider paths that look like artifact paths)
            filtered_extra = []
            for path in extra_artifacts:
                if any(
                    artifact_type in path
                    for artifact_type in [
                        "nodes/",
                        "cli_tools/",
                        "runtimes/",
                        "adapters/",
                        "contracts/",
                        "packages/",
                    ]
                ):
                    filtered_extra.append(path)

            is_valid = len(missing_artifacts) == 0

            return {
                "valid": is_valid,
                "reason": (
                    "Registry and .onextree are synchronized"
                    if is_valid
                    else "Registry and .onextree are out of sync"
                ),
                "missing_artifacts": list(missing_artifacts),
                "extra_artifacts": filtered_extra,
            }

        except Exception as e:
            return {
                "valid": False,
                "reason": f"Error validating against .onextree: {e}",
                "missing_artifacts": [],
                "extra_artifacts": [],
            }

    def _extract_paths_from_onextree(
        self, node: Dict[str, Any], paths: Set[str], current_path: str = ""
    ) -> None:
        """Recursively extract all file paths from .onextree data."""
        if not isinstance(node, dict):
            return

        node_name = node.get("name", "")
        node_type = node.get("type", "")

        if current_path:
            full_path = f"{current_path}/{node_name}"
        else:
            full_path = node_name

        if node_type == "file":
            paths.add(full_path)
        elif node_type == "directory":
            paths.add(full_path)

            # Process children
            children = node.get("children", [])
            for child in children:
                self._extract_paths_from_onextree(child, paths, full_path)

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get statistics about the loaded registry."""
        if not self._loaded:
            self._load_registry_data()

        stats: Dict[str, Any] = {
            "total_artifacts": 0,
            "by_type": {},
            "wip_count": 0,
            "valid_count": 0,
        }

        for artifact_type, artifact_list in self.artifacts.items():
            count = len(artifact_list)
            wip_count = len([a for a in artifact_list if a.is_wip])

            stats["by_type"][artifact_type] = {
                "total": count,
                "wip": wip_count,
                "stable": count - wip_count,
            }

            stats["total_artifacts"] += count
            stats["wip_count"] += wip_count
            stats["valid_count"] += count

        return stats
