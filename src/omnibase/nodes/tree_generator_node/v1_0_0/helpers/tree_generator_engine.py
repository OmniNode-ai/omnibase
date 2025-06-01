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
from typing import Any, Dict, List, Optional, Literal

import yaml
from pydantic import BaseModel

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevel, OnexStatus
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.model.model_node_metadata import Namespace
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.model.model_onextree import OnextreeNode, OnextreeNodeTypeEnum, ArtifactCountsModel, MetadataValidationResultModel

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem

class TreeGeneratorEngine:
    """Engine for generating .onextree manifest files from directory structure analysis."""

    def __init__(
        self, handler_registry: Optional[FileTypeHandlerRegistry] = None, event_bus: Optional[ProtocolEventBus] = None
    ) -> None:
        """
        Initialize the tree generator engine.

        Args:
            handler_registry: Optional FileTypeHandlerRegistry for custom file processing
            event_bus: Optional ProtocolEventBus for logging
        """
        self.handler_registry = handler_registry
        self._event_bus = event_bus
        if self.handler_registry:
            # Register canonical handlers if not already done
            self.handler_registry.register_all_handlers()
            emit_log_event(
                LogLevel.DEBUG,
                "Tree generator engine initialized with custom handler registry",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )

    def scan_directory_structure(self, root_path: Path) -> OnextreeNode:
        namespace_map = {}
        event_bus = self._event_bus
        def scan_recursive(path: Path, is_root: bool = False) -> OnextreeNode:
            if not path.is_dir():
                ns = str(Namespace.from_path(path))
                namespace_map.setdefault(ns, []).append(str(path))
                emit_log_event(
                    LogLevel.DEBUG,
                    f"[TREEGEN] Including file: {path}",
                    node_id=_COMPONENT_NAME,
                    event_bus=event_bus,
                )
                return OnextreeNode(
                    name=path.name,
                    type=OnextreeNodeTypeEnum.FILE,
                    children=None
                )

            children: List[OnextreeNode] = []
            for child in sorted(path.iterdir()):
                if child.name.startswith(".") and child.name not in [
                    ".onexignore",
                    ".wip",
                ]:
                    emit_log_event(
                        LogLevel.DEBUG,
                        f"[TREEGEN] Skipping hidden: {child}",
                        node_id=_COMPONENT_NAME,
                        event_bus=event_bus,
                    )
                    continue
                if child.name == "__pycache__":
                    emit_log_event(
                        LogLevel.DEBUG,
                        f"[TREEGEN] Skipping __pycache__: {child}",
                        node_id=_COMPONENT_NAME,
                        event_bus=event_bus,
                    )
                    continue
                emit_log_event(
                    LogLevel.DEBUG,
                    f"[TREEGEN] Including: {child}",
                    node_id=_COMPONENT_NAME,
                    event_bus=event_bus,
                )
                children.append(scan_recursive(child))

            node_name = root_path.name if is_root else path.name
            return OnextreeNode(
                name=node_name,
                type=OnextreeNodeTypeEnum.DIRECTORY,
                children=children
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
        # Count nodes
        nodes_dir = root_path / "nodes"
        if nodes_dir.exists():
            for node_dir in nodes_dir.iterdir():
                if node_dir.is_dir() and not node_dir.name.startswith("."):
                    version_dirs = [
                        d
                        for d in node_dir.iterdir()
                        if d.is_dir() and d.name.startswith("v")
                    ]
                    counts.nodes += len(version_dirs)
        # Count CLI tools
        cli_tools_dir = root_path / "cli_tools"
        if cli_tools_dir.exists():
            for tool_dir in cli_tools_dir.iterdir():
                if tool_dir.is_dir() and not tool_dir.name.startswith("."):
                    version_dirs = [
                        d
                        for d in tool_dir.iterdir()
                        if d.is_dir() and d.name.startswith("v")
                    ]
                    counts.cli_tools += len(version_dirs)
        # Count runtimes
        runtimes_dir = root_path / "runtimes"
        if runtimes_dir.exists():
            for runtime_dir in runtimes_dir.iterdir():
                if runtime_dir.is_dir() and not runtime_dir.name.startswith("."):
                    version_dirs = [
                        d
                        for d in runtime_dir.iterdir()
                        if d.is_dir() and d.name.startswith("v")
                    ]
                    counts.runtimes += len(version_dirs)
        return counts

    def validate_metadata(self, root_path: Path) -> MetadataValidationResultModel:
        validation_results = MetadataValidationResultModel()
        # Check nodes
        nodes_dir = root_path / "nodes"
        if nodes_dir.exists():
            for node_dir in nodes_dir.iterdir():
                if node_dir.is_dir() and not node_dir.name.startswith("."):
                    for version_dir in node_dir.iterdir():
                        if version_dir.is_dir() and version_dir.name.startswith("v"):
                            metadata_file = version_dir / "node.onex.yaml"
                            if metadata_file.exists():
                                try:
                                    with open(metadata_file, "r") as f:
                                        yaml.safe_load(f)
                                    validation_results.valid_artifacts += 1
                                except Exception as e:
                                    validation_results.invalid_artifacts += 1
                                    validation_results.errors.append(
                                        f"Invalid metadata in {metadata_file}: {str(e)}"
                                    )
                            else:
                                validation_results.invalid_artifacts += 1
                                validation_results.errors.append(
                                    f"Missing metadata file: {metadata_file}"
                                )
        # Check CLI tools
        cli_tools_dir = root_path / "cli_tools"
        if cli_tools_dir.exists():
            for tool_dir in cli_tools_dir.iterdir():
                if tool_dir.is_dir() and not tool_dir.name.startswith("."):
                    for version_dir in tool_dir.iterdir():
                        if version_dir.is_dir() and version_dir.name.startswith("v"):
                            metadata_file = version_dir / "cli_tool.yaml"
                            if metadata_file.exists():
                                try:
                                    with open(metadata_file, "r") as f:
                                        yaml.safe_load(f)
                                    validation_results.valid_artifacts += 1
                                except Exception as e:
                                    validation_results.invalid_artifacts += 1
                                    validation_results.errors.append(
                                        f"Invalid metadata in {metadata_file}: {str(e)}"
                                    )
                            else:
                                validation_results.invalid_artifacts += 1
                                validation_results.errors.append(
                                    f"Missing metadata file: {metadata_file}"
                                )
        # Check runtimes
        runtimes_dir = root_path / "runtimes"
        if runtimes_dir.exists():
            for runtime_dir in runtimes_dir.iterdir():
                if runtime_dir.is_dir() and not runtime_dir.name.startswith("."):
                    for version_dir in runtime_dir.iterdir():
                        if version_dir.is_dir() and version_dir.name.startswith("v"):
                            metadata_file = version_dir / "runtime.yaml"
                            if metadata_file.exists():
                                try:
                                    with open(metadata_file, "r") as f:
                                        yaml.safe_load(f)
                                    validation_results.valid_artifacts += 1
                                except Exception as e:
                                    validation_results.invalid_artifacts += 1
                                    validation_results.errors.append(
                                        f"Invalid metadata in {metadata_file}: {str(e)}"
                                    )
                            else:
                                validation_results.invalid_artifacts += 1
                                validation_results.errors.append(
                                    f"Missing metadata file: {metadata_file}"
                                )
        return validation_results

    def generate_manifest(
        self,
        tree_structure: OnextreeNode,
        output_path: Path,
        output_format: str = "yaml",
    ) -> Path:
        """Generate the .onextree manifest file."""

        if output_format == "json":
            manifest_path = (
                output_path.with_suffix(".json")
                if output_path.suffix != ".json"
                else output_path
            )
            with open(manifest_path, "w") as f:
                json.dump(tree_structure.model_dump(), f, indent=2)
        else:
            manifest_path = (
                output_path if output_path.suffix else output_path.with_suffix("")
            )
            with open(manifest_path, "w") as f:
                yaml.safe_dump(tree_structure.model_dump(mode="json"), f, default_flow_style=False, sort_keys=False)

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
                    "validation_results": validation_results.model_dump() if validation_results else None,
                    "tree_structure": tree_structure.model_dump(),
                },
            )

        except Exception as e:
            emit_log_event(
                LogLevel.ERROR,
                f"Tree generation failed: {str(e)}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
            return OnexResultModel(
                status=OnexStatus.ERROR,
                metadata={"error": str(e)},
            )
