# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: tree_generator_engine.py
# version: 1.0.0
# uuid: f27e1a48-d537-404f-b777-9ee08b8b2e2d
# author: OmniNode Team
# created_at: 2025-05-24T10:56:37.726449
# last_modified_at: 2025-05-24T15:01:16.175703
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 96c0924d4ac231f055019b785ddf39ab5fe8d08c749270509dfb44d97144ca5e
# entrypoint: python@tree_generator_engine.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.tree_generator_engine
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Tree Generator Engine - Core logic for generating .onextree manifest files.

This engine handles the core functionality of scanning directory structures,
counting artifacts, validating metadata, and generating manifest files.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from omnibase.model.enum_onex_status import OnexStatus
from omnibase.model.model_onex_message_result import OnexResultModel

logger = logging.getLogger(__name__)


class TreeGeneratorEngine:
    """Engine for generating .onextree manifest files from directory structure analysis."""

    def __init__(self) -> None:
        """Initialize the tree generator engine."""
        pass

    def scan_directory_structure(self, root_path: Path) -> Dict[str, Any]:
        """Scan directory structure and build tree representation."""

        def scan_recursive(path: Path, is_root: bool = False) -> Dict[str, Any]:
            """Recursively scan directory structure."""
            if not path.is_dir():
                return {"name": path.name, "type": "file"}

            children: List[Dict[str, Any]] = []
            for child in sorted(path.iterdir()):
                # Skip hidden files and cache directories
                if child.name.startswith(".") and child.name not in [
                    ".onexignore",
                    ".wip",
                ]:
                    continue
                if child.name == "__pycache__":
                    continue

                children.append(scan_recursive(child))

            # For the root node, use a more descriptive name
            if is_root:
                name = path.name if path.name else "omnibase"
            else:
                name = path.name

            return {"name": name, "type": "directory", "children": children}

        return scan_recursive(root_path, is_root=True)

    def count_artifacts(self, root_path: Path) -> Dict[str, int]:
        """Count versioned artifacts in the directory structure."""
        counts = {
            "nodes": 0,
            "cli_tools": 0,
            "runtimes": 0,
            "adapters": 0,
            "contracts": 0,
            "packages": 0,
        }

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
                    counts["nodes"] += len(version_dirs)

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
                    counts["cli_tools"] += len(version_dirs)

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
                    counts["runtimes"] += len(version_dirs)

        return counts

    def validate_metadata(self, root_path: Path) -> Dict[str, Any]:
        """Validate metadata files for artifacts."""
        validation_results: Dict[str, Any] = {
            "valid_artifacts": 0,
            "invalid_artifacts": 0,
            "errors": [],
        }

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
                                    validation_results["valid_artifacts"] += 1
                                except Exception as e:
                                    validation_results["invalid_artifacts"] += 1
                                    validation_results["errors"].append(
                                        f"Invalid metadata in {metadata_file}: {str(e)}"
                                    )
                            else:
                                validation_results["invalid_artifacts"] += 1
                                validation_results["errors"].append(
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
                                    validation_results["valid_artifacts"] += 1
                                except Exception as e:
                                    validation_results["invalid_artifacts"] += 1
                                    validation_results["errors"].append(
                                        f"Invalid metadata in {metadata_file}: {str(e)}"
                                    )
                            else:
                                validation_results["invalid_artifacts"] += 1
                                validation_results["errors"].append(
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
                                    validation_results["valid_artifacts"] += 1
                                except Exception as e:
                                    validation_results["invalid_artifacts"] += 1
                                    validation_results["errors"].append(
                                        f"Invalid metadata in {metadata_file}: {str(e)}"
                                    )
                            else:
                                validation_results["invalid_artifacts"] += 1
                                validation_results["errors"].append(
                                    f"Missing metadata file: {metadata_file}"
                                )

        return validation_results

    def generate_manifest(
        self,
        tree_structure: Dict[str, Any],
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
                json.dump(tree_structure, f, indent=2)
        else:
            manifest_path = (
                output_path if output_path.suffix else output_path.with_suffix("")
            )
            with open(manifest_path, "w") as f:
                yaml.dump(tree_structure, f, default_flow_style=False, sort_keys=False)

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
                    "artifacts_discovered": artifact_counts,
                    "validation_results": validation_results,
                    "tree_structure": tree_structure,
                },
            )

        except Exception as e:
            logger.error(f"Tree generation failed: {str(e)}", exc_info=True)
            return OnexResultModel(
                status=OnexStatus.ERROR,
                metadata={"error": str(e)},
            )
