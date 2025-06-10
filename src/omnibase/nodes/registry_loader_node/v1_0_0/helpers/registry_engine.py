"""
Registry Engine - Core registry loading logic for the registry loader node.

This module contains the core logic for loading and parsing the ONEX registry
from filesystem structure. It's designed to work with the registry loader node's
state models and provide clean separation between the node interface and the
registry loading implementation.
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.model.model_onextree import OnexTreeNode, OnextreeRoot
from omnibase.core.errors import OnexError, CoreErrorCode

_COMPONENT_NAME = Path(__file__).stem
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
    import sys
    from pathlib import Path

    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    sys.path.insert(0, str(parent_dir))
    from models.state import (
        ArtifactTypeEnum,
        RegistryArtifact,
        RegistryLoaderInputState,
        RegistryLoaderOutputState,
        RegistryLoadingError,
        RegistryLoadingErrorTypeEnum,
    )


class RegistryEngine:
    """
    Core registry loading engine.

    Handles the actual filesystem scanning, metadata parsing, and artifact discovery
    for the registry loader node.
    """

    def __init__(
        self, handler_registry: Optional[FileTypeHandlerRegistry] = None, event_bus=None
    ) -> None:
        """
        Initialize the registry engine.

        Args:
            handler_registry: Optional FileTypeHandlerRegistry for custom file processing
            event_bus: Event bus for logging
        """
        self.errors: List[RegistryLoadingError] = []
        self.handler_registry = handler_registry
        if event_bus is None:
            raise OnexError(CoreErrorCode.UNSUPPORTED_OPERATION, "Registry engine operation not supported in this context.")
        self._event_bus = event_bus
        if self.handler_registry:
            self.handler_registry.register_all_handlers()
            emit_log_event_sync(
                LogLevelEnum.DEBUG,
                "Registry engine initialized with custom handler registry",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )

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
            root_path = Path(input_state.root_directory).resolve()
            onextree_path = self._resolve_onextree_path(
                root_path, input_state.onextree_path
            )
            if not onextree_path or not onextree_path.exists():
                return RegistryLoaderOutputState(
                    version=input_state.version,
                    status=OnexStatus.ERROR,
                    message=f"Failed to find .onextree file. Expected at {onextree_path or root_path / '.onextree'}",
                    root_directory=str(root_path),
                    onextree_path=str(onextree_path) if onextree_path else None,
                    scan_duration_ms=(time.time() - start_time) * 1000,
                )
            onextree_model = self._load_onextree_model(onextree_path)
            if not onextree_model:
                return RegistryLoaderOutputState(
                    version=input_state.version,
                    status=OnexStatus.ERROR,
                    message=f"Failed to load .onextree from {onextree_path}",
                    root_directory=str(root_path),
                    onextree_path=str(onextree_path),
                    scan_duration_ms=(time.time() - start_time) * 1000,
                )
            artifacts = self._discover_artifacts_from_onextree_model(
                onextree_model,
                root_path,
                input_state.artifact_types,
                input_state.include_wip,
            )
            artifact_types_found = list(
                set(artifact.artifact_type for artifact in artifacts)
            )
            scan_duration = (time.time() - start_time) * 1000
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
            status = OnexStatus.SUCCESS
            message = f"Successfully loaded {total_count} artifacts from .onextree"
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
                onextree_path=str(onextree_path),
                scan_duration_ms=scan_duration,
                errors=self.errors,
            )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Registry loading failed: {e}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
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
        parent_onextree = root_path.parent / ".onextree"
        return parent_onextree if parent_onextree.exists() else None

    def _load_onextree_model(self, onextree_path: Path) -> Optional[OnextreeRoot]:
        """
        Load and parse the .onextree file into a Pydantic model.

        Args:
            onextree_path: Path to .onextree

        Returns:
            OnextreeRoot model or None if failed
        """
        try:
            if not onextree_path.exists():
                self.errors.append(
                    RegistryLoadingError(
                        path=str(onextree_path),
                        error_type=RegistryLoadingErrorTypeEnum.MISSING_FILE,
                        error_message=f"Onextree file not found: {onextree_path}",
                        is_fatal=True,
                    )
                )
                return None
            onextree_model = OnextreeRoot.from_yaml_file(str(onextree_path))
            return onextree_model
        except Exception as e:
            self.errors.append(
                RegistryLoadingError(
                    path=str(onextree_path),
                    error_type=RegistryLoadingErrorTypeEnum.PARSE_ERROR,
                    error_message=f"Failed to parse onextree: {str(e)}",
                    is_fatal=True,
                )
            )
            return None

    def _discover_artifacts_from_onextree_model(
        self,
        onextree_model: OnextreeRoot,
        root_path: Path,
        artifact_types_filter: Optional[List[ArtifactTypeEnum]],
        include_wip: bool,
    ) -> List[RegistryArtifact]:
        """
        Discover artifacts from the .onextree model.

        Args:
            onextree_model: Parsed .onextree model
            root_path: Root path for resolving relative paths
            artifact_types_filter: Filter to specific artifact types or None for all
            include_wip: Whether to include WIP artifacts

        Returns:
            List of discovered registry artifacts
        """
        artifacts = []
        all_artifact_types = [
            ArtifactTypeEnum.NODES,
            ArtifactTypeEnum.CLI_TOOLS,
            ArtifactTypeEnum.RUNTIMES,
            ArtifactTypeEnum.ADAPTERS,
            ArtifactTypeEnum.CONTRACTS,
            ArtifactTypeEnum.PACKAGES,
        ]
        artifact_types_to_process = (
            artifact_types_filter if artifact_types_filter else all_artifact_types
        )
        versioned_artifacts = onextree_model.find_versioned_artifacts()
        type_mapping = {
            "nodes": ArtifactTypeEnum.NODES,
            "cli_tools": ArtifactTypeEnum.CLI_TOOLS,
            "runtimes": ArtifactTypeEnum.RUNTIMES,
            "adapters": ArtifactTypeEnum.ADAPTERS,
            "contracts": ArtifactTypeEnum.CONTRACTS,
            "packages": ArtifactTypeEnum.PACKAGES,
        }
        for artifact_type_str, artifact_name, version, node in versioned_artifacts:
            artifact_type = type_mapping.get(artifact_type_str)
            if artifact_type and artifact_type in artifact_types_to_process:
                metadata_file = self._find_metadata_file_in_node(node, artifact_type)
                if metadata_file:
                    full_path = (
                        Path(onextree_model.name)
                        / artifact_type_str
                        / artifact_name
                        / version
                    )
                    artifact = self._create_artifact_from_onextree(
                        artifact_name,
                        artifact_type,
                        version,
                        str(full_path),
                        metadata_file,
                        root_path,
                        include_wip,
                    )
                    if artifact:
                        artifacts.append(artifact)
        return artifacts

    def _find_metadata_file_in_node(
        self, node: OnexTreeNode, artifact_type: ArtifactTypeEnum
    ) -> Optional[str]:
        """
        Find the appropriate metadata file in the node's children.

        Args:
            node: OnexTreeNode to search in
            artifact_type: Type of artifact to find metadata for

        Returns:
            Metadata filename or None if not found
        """
        metadata_files = {
            ArtifactTypeEnum.NODES: "node.onex.yaml",
            ArtifactTypeEnum.CLI_TOOLS: "cli_tool.yaml",
            ArtifactTypeEnum.RUNTIMES: "runtime.yaml",
            ArtifactTypeEnum.ADAPTERS: "adapter.yaml",
            ArtifactTypeEnum.CONTRACTS: "contract.yaml",
            ArtifactTypeEnum.PACKAGES: "package.yaml",
        }
        expected_file = metadata_files.get(artifact_type)
        if not expected_file:
            return None
        metadata_node = node.find_file(expected_file)
        return expected_file if metadata_node else None

    def _create_artifact_from_onextree(
        self,
        name: str,
        artifact_type: ArtifactTypeEnum,
        version: str,
        path: str,
        metadata_file: str,
        root_path: Path,
        include_wip: bool,
    ) -> Optional[RegistryArtifact]:
        """
        Create a RegistryArtifact from .onextree discovery.

        Args:
            name: Artifact name
            artifact_type: Type of artifact
            version: Version string
            path: Relative path from root
            metadata_file: Metadata filename
            root_path: Root path for resolving relative paths
            include_wip: Whether to include WIP artifacts

        Returns:
            RegistryArtifact or None if failed/filtered
        """
        try:
            artifact_path = root_path / path
            wip_marker_path = artifact_path / ".wip"
            is_wip = wip_marker_path.exists()
            if is_wip and not include_wip:
                return None
            metadata, is_valid = self._load_artifact_metadata_with_validation(
                artifact_path, metadata_file, is_wip
            )
            if not is_valid and not is_wip:
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
                    path=f"{name}/{version}",
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
        metadata_path = artifact_path / metadata_file
        if not metadata_path.exists():
            if is_wip:
                return None, True
            else:
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
                return metadata, False
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
