# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: registry_engine.py
# version: 1.0.0
# uuid: 88b43b31-d73c-454b-a7cd-8f51ce78e7f1
# author: OmniNode Team
# created_at: 2025-05-24T15:44:23.157711
# last_modified_at: 2025-05-24T20:17:56.135195
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: be9819d9c37ee53feb31a7ed10c1bf6a5077e1b3ea0ce507dad60ac796c12c8c
# entrypoint: python@registry_engine.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.registry_engine
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Registry Engine - Core registry loading logic for the registry loader node.

This module contains the core logic for loading and parsing the ONEX registry
from filesystem structure. It's designed to work with the registry loader node's
state models and provide clean separation between the node interface and the
registry loading implementation.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.model.enum_onex_status import OnexStatus

# Handle relative imports for both module and direct execution
try:
    from ..models.state import (
        ArtifactTypeEnum,
        RegistryArtifact,
        RegistryLoaderInputState,
        RegistryLoaderOutputState,
        RegistryLoadingError,
        RegistryLoadingErrorTypeEnum,
    )
except ImportError:
    # Direct execution - use absolute imports
    import sys
    from pathlib import Path

    # Add the parent directory to path to find models
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    sys.path.insert(0, str(parent_dir))

    from models.state import (  # type: ignore
        ArtifactTypeEnum,
        RegistryArtifact,
        RegistryLoaderInputState,
        RegistryLoaderOutputState,
        RegistryLoadingError,
        RegistryLoadingErrorTypeEnum,
    )

logger = logging.getLogger(__name__)


class RegistryEngine:
    """
    Core registry loading engine.

    Handles the actual filesystem scanning, metadata parsing, and artifact discovery
    for the registry loader node.
    """

    def __init__(
        self, handler_registry: Optional[FileTypeHandlerRegistry] = None
    ) -> None:
        """
        Initialize the registry engine.

        Args:
            handler_registry: Optional FileTypeHandlerRegistry for custom file processing
        """
        self.errors: List[RegistryLoadingError] = []
        self.handler_registry = handler_registry
        if self.handler_registry:
            # Register canonical handlers if not already done
            self.handler_registry.register_all_handlers()
            logger.debug("Registry engine initialized with custom handler registry")

    def load_registry(
        self, input_state: RegistryLoaderInputState
    ) -> RegistryLoaderOutputState:
        """
        Load the complete registry based on input parameters.

        Args:
            input_state: Registry loader input parameters

        Returns:
            RegistryLoaderOutputState with loaded artifacts and metadata
        """
        start_time = time.time()
        self.errors = []

        try:
            # Resolve paths
            root_path = Path(input_state.root_directory).resolve()
            onextree_path = self._resolve_onextree_path(
                root_path, input_state.onextree_path
            )

            # Load registry.yaml
            registry_path = root_path / "registry" / "registry.yaml"
            registry_data = self._load_registry_yaml(registry_path)

            if not registry_data:
                return RegistryLoaderOutputState(
                    version=input_state.version,
                    status=OnexStatus.ERROR,
                    message=f"Failed to load registry.yaml from {registry_path}",
                    root_directory=str(root_path),
                    onextree_path=str(onextree_path) if onextree_path else None,
                    scan_duration_ms=(time.time() - start_time) * 1000,
                )

            # Load artifacts
            artifacts = self._load_artifacts(
                registry_data,
                root_path,
                input_state.artifact_types,
                input_state.include_wip,
            )

            # Calculate statistics
            artifact_types_found = list(
                set(artifact.artifact_type for artifact in artifacts)
            )
            scan_duration = (time.time() - start_time) * 1000

            # Calculate artifact statistics
            valid_artifacts = [
                a for a in artifacts if a.metadata.get("_is_valid", True)
            ]
            invalid_artifacts = [
                a for a in artifacts if not a.metadata.get("_is_valid", True)
            ]
            wip_artifacts = [a for a in artifacts if a.is_wip]

            valid_count = len(valid_artifacts)
            invalid_count = len(invalid_artifacts)
            wip_count = len(wip_artifacts)
            total_count = len(artifacts)

            # Determine status
            status = OnexStatus.SUCCESS
            message = f"Successfully loaded {total_count} artifacts"

            if self.errors:
                non_fatal_errors = [e for e in self.errors if not e.is_fatal]
                fatal_errors = [e for e in self.errors if e.is_fatal]

                if fatal_errors:
                    status = OnexStatus.ERROR
                    message = (
                        f"Failed to load registry: {len(fatal_errors)} fatal errors"
                    )
                elif non_fatal_errors:
                    status = OnexStatus.WARNING
                    message = f"Loaded {total_count} artifacts with {len(non_fatal_errors)} warnings"

            # Add more detail to the message
            if total_count > 0:
                details = []
                if valid_count > 0:
                    details.append(f"{valid_count} valid")
                if invalid_count > 0:
                    details.append(f"{invalid_count} invalid")
                if wip_count > 0:
                    details.append(f"{wip_count} WIP")

                if details:
                    message += f" ({', '.join(details)})"

            return RegistryLoaderOutputState(
                version=input_state.version,
                status=status,
                message=message,
                artifacts=artifacts,
                artifact_count=total_count,
                valid_artifact_count=valid_count,
                invalid_artifact_count=invalid_count,
                wip_artifact_count=wip_count,
                artifact_types_found=artifact_types_found,
                root_directory=str(root_path),
                onextree_path=str(onextree_path) if onextree_path else None,
                scan_duration_ms=scan_duration,
                errors=self.errors,
            )

        except Exception as e:
            logger.exception(f"Registry loading failed: {e}")
            return RegistryLoaderOutputState(
                version=input_state.version,
                status=OnexStatus.ERROR,
                message=f"Registry loading failed: {str(e)}",
                root_directory=input_state.root_directory,
                scan_duration_ms=(time.time() - start_time) * 1000,
            )

    def _resolve_onextree_path(
        self, root_path: Path, onextree_path: Optional[str]
    ) -> Optional[Path]:
        """
        Resolve the .onextree file path.

        Args:
            root_path: Root directory being scanned
            onextree_path: Explicit .onextree path or None

        Returns:
            Resolved .onextree path or None if not found
        """
        if onextree_path:
            path = Path(onextree_path)
            if path.is_absolute():
                return path if path.exists() else None
            else:
                return root_path / path if (root_path / path).exists() else None

        # Look for .onextree in parent directory of root_path
        parent_onextree = root_path.parent / ".onextree"
        return parent_onextree if parent_onextree.exists() else None

    def _load_registry_yaml(self, registry_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load and parse the registry.yaml file.

        Args:
            registry_path: Path to registry.yaml

        Returns:
            Parsed registry data or None if failed
        """
        try:
            if not registry_path.exists():
                self.errors.append(
                    RegistryLoadingError(
                        path=str(registry_path),
                        error_type=RegistryLoadingErrorTypeEnum.MISSING_FILE,
                        error_message=f"Registry file not found: {registry_path}",
                        is_fatal=True,
                    )
                )
                return None

            with open(registry_path, "r") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                self.errors.append(
                    RegistryLoadingError(
                        path=str(registry_path),
                        error_type=RegistryLoadingErrorTypeEnum.PARSE_ERROR,
                        error_message="Registry file is not a valid YAML dictionary",
                        is_fatal=True,
                    )
                )
                return None

            return data

        except Exception as e:
            self.errors.append(
                RegistryLoadingError(
                    path=str(registry_path),
                    error_type=RegistryLoadingErrorTypeEnum.PARSE_ERROR,
                    error_message=f"Failed to parse registry.yaml: {str(e)}",
                    is_fatal=True,
                )
            )
            return None

    def _load_artifacts(
        self,
        registry_data: Dict[str, Any],
        root_path: Path,
        artifact_types_filter: Optional[List[ArtifactTypeEnum]],
        include_wip: bool,
    ) -> List[RegistryArtifact]:
        """
        Load all artifacts from the registry data.

        Args:
            registry_data: Parsed registry.yaml data
            root_path: Root path for resolving relative paths
            artifact_types_filter: Filter to specific artifact types or None for all
            include_wip: Whether to include WIP artifacts

        Returns:
            List of loaded registry artifacts
        """
        artifacts = []

        # Define all possible artifact types
        all_artifact_types = [
            ArtifactTypeEnum.NODES,
            ArtifactTypeEnum.CLI_TOOLS,
            ArtifactTypeEnum.RUNTIMES,
            ArtifactTypeEnum.ADAPTERS,
            ArtifactTypeEnum.CONTRACTS,
            ArtifactTypeEnum.PACKAGES,
        ]

        # Filter artifact types if specified
        artifact_types_to_process = (
            artifact_types_filter if artifact_types_filter else all_artifact_types
        )

        for artifact_type in artifact_types_to_process:
            # Convert enum to string for registry data lookup
            artifact_type_str = artifact_type.value
            if artifact_type_str not in registry_data:
                continue

            for artifact_entry in registry_data[artifact_type_str]:
                artifact_name = artifact_entry.get("name")
                if not artifact_name:
                    continue

                for version_info in artifact_entry.get("versions", []):
                    artifact = self._load_single_artifact(
                        artifact_name,
                        artifact_type,
                        version_info,
                        root_path,
                        include_wip,
                    )

                    if artifact:
                        artifacts.append(artifact)

        return artifacts

    def _load_single_artifact(
        self,
        name: str,
        artifact_type: ArtifactTypeEnum,
        version_info: Dict[str, Any],
        root_path: Path,
        include_wip: bool,
    ) -> Optional[RegistryArtifact]:
        """
        Load a single artifact from version info.

        Args:
            name: Artifact name
            artifact_type: Type of artifact
            version_info: Version information from registry
            root_path: Root path for resolving relative paths
            include_wip: Whether to include WIP artifacts

        Returns:
            RegistryArtifact or None if failed/filtered
        """
        try:
            version = version_info.get("version")
            path_str = version_info.get("path")
            metadata_file = version_info.get("metadata_file")

            if not all([version, path_str, metadata_file]):
                self.errors.append(
                    RegistryLoadingError(
                        path=f"{name}/{version or 'unknown'}",
                        error_type=RegistryLoadingErrorTypeEnum.INVALID_REGISTRY_ENTRY,
                        error_message="Missing required fields in registry entry",
                        is_fatal=False,
                    )
                )
                return None

            # Type check: ensure we have strings
            if (
                not isinstance(version, str)
                or not isinstance(path_str, str)
                or not isinstance(metadata_file, str)
            ):
                self.errors.append(
                    RegistryLoadingError(
                        path=f"{name}/{version or 'unknown'}",
                        error_type=RegistryLoadingErrorTypeEnum.INVALID_REGISTRY_ENTRY,
                        error_message="Invalid field types in registry entry",
                        is_fatal=False,
                    )
                )
                return None

            artifact_path = root_path / path_str

            # Check for .wip marker
            wip_marker_path = artifact_path / ".wip"
            is_wip = wip_marker_path.exists()

            # Skip WIP artifacts if not including them
            if is_wip and not include_wip:
                return None

            # Load metadata (this will handle both valid and invalid cases)
            metadata, is_valid = self._load_artifact_metadata_with_validation(
                artifact_path, metadata_file, is_wip
            )

            # Always create the artifact, even if invalid
            # For invalid artifacts, we'll include error information in metadata
            if not is_valid and not is_wip:
                # Add error information to metadata for invalid artifacts
                if metadata is None:
                    metadata = {}
                metadata["_validation_error"] = (
                    f"Invalid or missing metadata file: {metadata_file}"
                )
                metadata["_is_valid"] = False
            else:
                if metadata is None:
                    metadata = {}
                metadata["_is_valid"] = True

            return RegistryArtifact(
                name=name,
                version=version,
                artifact_type=artifact_type,
                path=str(artifact_path),
                metadata=metadata,
                is_wip=is_wip,
            )

        except Exception as e:
            self.errors.append(
                RegistryLoadingError(
                    path=f"{name}/{version_info.get('version', 'unknown')}",
                    error_type=RegistryLoadingErrorTypeEnum.LOAD_ERROR,
                    error_message=f"Failed to load artifact: {str(e)}",
                    is_fatal=False,
                )
            )
            return None

    def _load_artifact_metadata_with_validation(
        self, artifact_path: Path, metadata_file: str, is_wip: bool
    ) -> tuple[Optional[Dict[str, Any]], bool]:
        """
        Load and parse artifact metadata file with validation.

        Args:
            artifact_path: Path to the artifact directory
            metadata_file: Name of the metadata file
            is_wip: Whether this is a WIP artifact

        Returns:
            Tuple of (metadata dict or None, is_valid boolean)
        """
        # For WIP artifacts, metadata is optional and they are always considered valid
        metadata_path = artifact_path / metadata_file

        if not metadata_path.exists():
            if is_wip:
                # WIP artifacts don't need metadata files
                return None, True
            else:
                # Non-WIP artifacts without metadata are invalid
                self.errors.append(
                    RegistryLoadingError(
                        path=str(metadata_path),
                        error_type=RegistryLoadingErrorTypeEnum.MISSING_METADATA,
                        error_message=f"Missing metadata file: {metadata_file}",
                        is_fatal=False,
                    )
                )
                return None, False

        try:
            with open(metadata_path, "r") as f:
                metadata = yaml.safe_load(f)

            if not isinstance(metadata, dict):
                self.errors.append(
                    RegistryLoadingError(
                        path=str(metadata_path),
                        error_type=RegistryLoadingErrorTypeEnum.INVALID_METADATA,
                        error_message="Metadata file is not a valid YAML dictionary",
                        is_fatal=False,
                    )
                )
                return None, False

            # Basic validation - check for required fields
            required_fields = ["name", "version", "schema_version"]
            missing_fields = [
                field for field in required_fields if field not in metadata
            ]

            if missing_fields:
                self.errors.append(
                    RegistryLoadingError(
                        path=str(metadata_path),
                        error_type=RegistryLoadingErrorTypeEnum.INVALID_METADATA,
                        error_message=f"Missing required metadata fields: {missing_fields}",
                        is_fatal=False,
                    )
                )
                return metadata, False  # Return the metadata but mark as invalid

            return metadata, True

        except Exception as e:
            self.errors.append(
                RegistryLoadingError(
                    path=str(metadata_path),
                    error_type=RegistryLoadingErrorTypeEnum.PARSE_ERROR,
                    error_message=f"Failed to parse metadata: {str(e)}",
                    is_fatal=False,
                )
            )
            return None, False
