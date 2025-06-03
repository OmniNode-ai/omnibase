# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.001755'
# description: Stamped by PythonHandler
# entrypoint: python://tree_generator_engine
# hash: 3e853b13fbc5d08e7db7d29b4651528aa2c48161b160b4f53f4880fbc0a39b2b
# last_modified_at: '2025-05-29T14:14:00.105766+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: tree_generator_engine.py
# namespace: python://omnibase.nodes.tree_generator_node.v1_0_0.helpers.tree_generator_engine
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 13ab26f7-1903-4c6b-9442-9279cb069cec
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Tree Generator Engine - Core logic for generating .onextree manifest files.

This engine handles the core functionality of scanning directory structures,
counting artifacts, validating metadata, and generating manifest files.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
import fnmatch

import yaml
from pydantic import BaseModel

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum, OnexStatus, ArtifactTypeEnum
from omnibase.model.model_node_metadata import Namespace
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.model.model_onextree import (
    ArtifactCountsModel,
    MetadataValidationResultModel,
    OnexTreeNode,
    OnexTreeNodeTypeEnum,
    OnextreeRoot,
)
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.model.model_project_metadata import ProjectMetadataBlock, TreeGeneratorConfig
from omnibase.metadata.metadata_constants import (
    METADATA_FILE_NODE,
    METADATA_FILE_CLI_TOOL,
    METADATA_FILE_RUNTIME,
    METADATA_FILE_ADAPTER,
    METADATA_FILE_CONTRACT,
    METADATA_FILE_PACKAGE,
    DEFAULT_OUTPUT_FILENAME,
)
from omnibase.metadata.metadata_constants import DEFAULT_ONEX_IGNORE_PATTERNS

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem

# Add mapping from ArtifactTypeEnum to canonical constants
ARTIFACT_TYPE_TO_DIR = {
    ArtifactTypeEnum(ARTIFACT_TYPE_NODES): ARTIFACT_TYPE_NODES,
    ArtifactTypeEnum(ARTIFACT_TYPE_CLI_TOOLS): ARTIFACT_TYPE_CLI_TOOLS,
    ArtifactTypeEnum(ARTIFACT_TYPE_RUNTIMES): ARTIFACT_TYPE_RUNTIMES,
    ArtifactTypeEnum(ARTIFACT_TYPE_ADAPTERS): ARTIFACT_TYPE_ADAPTERS,
    ArtifactTypeEnum(ARTIFACT_TYPE_CONTRACTS): ARTIFACT_TYPE_CONTRACTS,
    ArtifactTypeEnum(ARTIFACT_TYPE_PACKAGES): ARTIFACT_TYPE_PACKAGES,
}

class TreeGeneratorEngine:
    """Engine for generating .onextree manifest files from directory structure analysis."""

    def __init__(
        self,
        handler_registry: Optional[FileTypeHandlerRegistry] = None,
        event_bus: Optional[ProtocolEventBus] = None,
        project_config: Optional[ProjectMetadataBlock] = None,
    ) -> None:
        """
        Initialize the tree generator engine.

        Args:
            handler_registry: Optional FileTypeHandlerRegistry for custom file processing
            event_bus: Optional ProtocolEventBus for logging
            project_config: Optional ProjectMetadataBlock for config-driven artifact discovery
        """
        self.handler_registry = handler_registry
        self._event_bus = event_bus
        self.project_config = project_config
        if self.handler_registry:
            self.handler_registry.register_all_handlers()
            emit_log_event_sync(
                LogLevelEnum.DEBUG,
                "Tree generator engine initialized with custom handler registry",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
        # Use config or ONEX defaults
        if project_config and project_config.tree_generator:
            self.tree_config = project_config.tree_generator
        else:
            # ONEX defaults
            self.tree_config = TreeGeneratorConfig(
                artifact_types=[
                    {"name": ArtifactTypeEnum.NODES, "metadata_file": METADATA_FILE_NODE, "version_pattern": "v*"},
                    {"name": ArtifactTypeEnum.CLI_TOOLS, "metadata_file": METADATA_FILE_CLI_TOOL, "version_pattern": "v*"},
                    {"name": ArtifactTypeEnum.RUNTIMES, "metadata_file": METADATA_FILE_RUNTIME, "version_pattern": "v*"},
                    {"name": ArtifactTypeEnum.ADAPTERS, "metadata_file": METADATA_FILE_ADAPTER, "version_pattern": "v*"},
                    {"name": ArtifactTypeEnum.CONTRACTS, "metadata_file": METADATA_FILE_CONTRACT, "version_pattern": "v*"},
                    {"name": ArtifactTypeEnum.PACKAGES, "metadata_file": METADATA_FILE_PACKAGE, "version_pattern": "v*"},
                ],
                # Namespace and metadata_validation use defaults
            )

    def scan_directory_structure(self, root_path: Path) -> OnexTreeNode:
        root_path = root_path.resolve()
        namespace_map = {}
        event_bus = self._event_bus

        # Prepare ignore patterns from config (tree_ignore) or fallback
        ignore_patterns = []
        if self.tree_config and self.tree_config.tree_ignore and self.tree_config.tree_ignore.patterns:
            ignore_patterns = self.tree_config.tree_ignore.patterns
        else:
            # Fallback minimal default
            ignore_patterns = DEFAULT_ONEX_IGNORE_PATTERNS

        def is_ignored(path: Path) -> bool:
            for pattern in ignore_patterns:
                if fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(str(path), pattern):
                    return True
            return False

        def scan_recursive(path: Path, is_root: bool = False) -> OnexTreeNode:
            if not path.is_dir():
                ns = str(Namespace.from_path(path))
                namespace_map.setdefault(ns, []).append(str(path))
                emit_log_event_sync(
                    LogLevelEnum.DEBUG,
                    f"[TREEGEN] Including file: {path}",
                    node_id=_COMPONENT_NAME,
                    event_bus=event_bus,
                )
                return OnexTreeNode(
                    name=path.name,
                    type=OnexTreeNodeTypeEnum.FILE,
                    namespace=ns
                )

            children: List[OnexTreeNode] = []
            for child in sorted(path.iterdir()):
                if is_ignored(child):
                    emit_log_event_sync(
                        LogLevelEnum.DEBUG,
                        f"[TREEGEN] Skipping ignored: {child}",
                        node_id=_COMPONENT_NAME,
                        event_bus=event_bus,
                    )
                    continue
                emit_log_event_sync(
                    LogLevelEnum.DEBUG,
                    f"[TREEGEN] Including: {child}",
                    node_id=_COMPONENT_NAME,
                    event_bus=event_bus,
                )
                children.append(scan_recursive(child))

            node_name = root_path.name if is_root else path.name
            return OnexTreeNode(
                name=node_name, type=OnexTreeNodeTypeEnum.DIRECTORY, children=children
            )

        tree = scan_recursive(root_path, is_root=True)

        # Check for namespace collisions
        collisions = {
            ns: files for ns, files in namespace_map.items() if len(files) > 1
        }
        if collisions:
            msg = ["ERROR: Namespace collision(s) detected in .onextree!"]
            for ns, files in collisions.items():
                msg.append(f"Namespace: {ns}\nFiles:")
                for f in files:
                    msg.append(f"  - {f}")
            raise RuntimeError("\n".join(msg))

        return tree

    def count_artifacts(self, root_path: Path) -> ArtifactCountsModel:
        counts = ArtifactCountsModel()
        for artifact_type in self.tree_config.artifact_types:
            dir_name = ARTIFACT_TYPE_TO_DIR.get(artifact_type.name, artifact_type.name.value)
            dir_path = root_path / dir_name
            if dir_path.exists():
                for artifact_dir in dir_path.iterdir():
                    if artifact_dir.is_dir() and not artifact_dir.name.startswith("."):
                        version_dirs = [
                            d
                            for d in artifact_dir.iterdir()
                            if d.is_dir() and (not artifact_type.version_pattern or d.name.startswith("v"))
                        ]
                        setattr(counts, dir_name, getattr(counts, dir_name, 0) + len(version_dirs))
        return counts

    def validate_metadata(self, root_path: Path) -> MetadataValidationResultModel:
        validation_results = MetadataValidationResultModel()
        for artifact_type in self.tree_config.artifact_types:
            dir_name = ARTIFACT_TYPE_TO_DIR.get(artifact_type.name, artifact_type.name.value)
            dir_path = root_path / dir_name
            if dir_path.exists():
                for artifact_dir in dir_path.iterdir():
                    if artifact_dir.is_dir() and not artifact_dir.name.startswith("."):
                        for version_dir in artifact_dir.iterdir():
                            if version_dir.is_dir() and (not artifact_type.version_pattern or version_dir.name.startswith("v")):
                                metadata_file = version_dir / (artifact_type.metadata_file or "")
                                if artifact_type.metadata_file and metadata_file.exists():
                                    try:
                                        with open(metadata_file, "r") as f:
                                            yaml.safe_load(f)
                                        validation_results.valid_artifacts += 1
                                    except Exception as e:
                                        validation_results.invalid_artifacts += 1
                                        validation_results.errors.append(
                                            f"Invalid metadata in {metadata_file}: {str(e)}"
                                        )
                                elif artifact_type.metadata_file:
                                    validation_results.invalid_artifacts += 1
                                    validation_results.errors.append(
                                        f"Missing metadata file: {metadata_file}"
                                    )
        return validation_results

    def _clean_tree_for_serialization(self, node):
        """Recursively clean the tree for YAML/JSON serialization: remove 'children' from files, ensure list for directories."""
        if hasattr(node, 'type') and hasattr(node, 'children'):
            if node.type == OnexTreeNodeTypeEnum.FILE:
                if hasattr(node, 'children'):
                    node.children = None
            elif node.type == OnexTreeNodeTypeEnum.DIRECTORY:
                node.children = node.children or []
                for child in node.children:
                    self._clean_tree_for_serialization(child)

    def generate_manifest(
        self,
        tree_structure: OnexTreeNode,
        output_path: Path,
        output_format: str = "yaml",
    ) -> Path:
        """Generate the .onextree manifest file."""
        # Wrap in OnextreeRoot for correct root node naming
        self._clean_tree_for_serialization(tree_structure)
        manifest_root = OnextreeRoot(
            name=tree_structure.name,
            type=OnexTreeNodeTypeEnum.DIRECTORY,
            children=tree_structure.children or [],
        )
        if output_format == "json":
            manifest_path = (
                output_path.with_suffix(".json")
                if output_path.suffix != ".json"
                else output_path
            )
            with open(manifest_path, "w") as f:
                json.dump(manifest_root.model_dump(), f, indent=2)
        else:
            manifest_path = (
                output_path if output_path.suffix else output_path.with_suffix("")
            )
            with open(manifest_path, "w") as f:
                yaml.safe_dump(
                    manifest_root.model_dump(mode="json"),
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                )
        return manifest_path

    def generate_tree(
        self,
        root_directory: str,
        output_path: Optional[str] = None,
        output_format: str = "yaml",
        include_metadata: bool = True,
    ) -> OnexResultModel:
        """
        Generate .onextree manifest from directory structure.

        Args:
            root_directory: Root directory to scan for artifacts
            output_path: Output path for .onextree file (optional)
            output_format: Output format (yaml or json)
            include_metadata: Whether to validate metadata files

        Returns:
            OnexResultModel with generation results
        """
        try:
            # Validate input
            root_path = Path(root_directory)
            if not root_path.exists():
                return OnexResultModel(
                    status=OnexStatus.ERROR,
                    metadata={"error": f"Root directory {root_path} does not exist"},
                )

            # Scan directory structure
            tree_structure = self.scan_directory_structure(root_path)

            # Count artifacts
            artifact_counts = self.count_artifacts(root_path)

            # Validate metadata if requested
            validation_results = None
            if include_metadata:
                validation_results = self.validate_metadata(root_path)

            # Determine output path
            if output_path:
                manifest_output_path = Path(output_path)
            else:
                manifest_output_path = root_path / ".onextree"

            # Generate manifest
            manifest_path = self.generate_manifest(
                tree_structure, manifest_output_path, output_format
            )

            # Return success result
            return OnexResultModel(
                status=OnexStatus.SUCCESS,
                metadata={
                    "manifest_path": str(manifest_path),
                    "artifacts_discovered": artifact_counts.model_dump(),
                    "validation_results": (
                        validation_results.model_dump() if validation_results else None
                    ),
                    "tree_structure": tree_structure.model_dump(),
                },
            )

        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Tree generation failed: {str(e)}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
            return OnexResultModel(
                status=OnexStatus.ERROR,
                metadata={"error": str(e)},
            )
