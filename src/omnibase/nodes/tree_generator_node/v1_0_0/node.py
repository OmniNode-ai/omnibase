#!/usr/bin/env python3
# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: node.py
# version: 1.0.0
# uuid: 4f13e6e3-84de-4e5d-8579-f90f3dd41a16
# author: OmniNode Team
# created_at: 2025-05-24T09:29:37.987105
# last_modified_at: 2025-05-24T13:39:57.890138
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 5aa9aa96ef80b9158d340ef33ab4819ec2ceeb1f608b2696a9363af138181e5c
# entrypoint: python@node.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.node
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Tree Generator Node - Generates .onextree manifest files from directory structure analysis.

This node scans the omnibase directory structure to discover all versioned artifacts
(nodes, CLI tools, runtimes, adapters, contracts, packages) and generates a canonical
.onextree manifest file that describes the project structure.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)

# Import state models with fallback for different execution contexts
try:
    from .models.state import TreeGeneratorInputState, TreeGeneratorOutputState
except ImportError:
    from models.state import TreeGeneratorInputState, TreeGeneratorOutputState

logger = logging.getLogger(__name__)


def scan_directory_structure(root_path: Path) -> Dict[str, Any]:
    """Scan directory structure and build tree representation."""

    def scan_recursive(path: Path, is_root: bool = False) -> Dict[str, Any]:
        """Recursively scan directory structure."""
        if not path.is_dir():
            return {"name": path.name, "type": "file"}

        children: List[Dict[str, Any]] = []
        for child in sorted(path.iterdir()):
            # Skip hidden files and cache directories
            if child.name.startswith(".") and child.name not in [".onexignore", ".wip"]:
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


def count_artifacts(root_path: Path) -> Dict[str, int]:
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


def validate_metadata(root_path: Path) -> Dict[str, Any]:
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
    tree_structure: Dict[str, Any], output_path: Path, output_format: str = "yaml"
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


def run_tree_generator_node(
    input_state: TreeGeneratorInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., TreeGeneratorOutputState]] = None,
) -> TreeGeneratorOutputState:
    """
    Main node entrypoint for tree_generator_node.

    Scans directory structure and generates .onextree manifest file.

    Args:
        input_state: Input parameters for tree generation
        event_bus: Optional event bus for emitting events
        output_state_cls: Optional output state class factory

    Returns:
        TreeGeneratorOutputState: Results of tree generation
    """
    # Set up event bus if not provided
    if event_bus is None:
        event_bus = InMemoryEventBus()

    # Emit start event
    start_event = OnexEvent(
        event_type=OnexEventTypeEnum.NODE_START,
        node_id="tree_generator_node",
        metadata={"input_state": input_state.model_dump()},
    )
    event_bus.publish(start_event)

    try:
        # Validate input
        root_path = Path(input_state.root_directory)
        if not root_path.exists():
            error_msg = f"Root directory {root_path} does not exist"
            return TreeGeneratorOutputState(
                version=input_state.version,
                status="error",
                message=error_msg,
                artifacts_discovered=None,
                validation_results=None,
            )

        # Scan directory structure
        tree_structure = scan_directory_structure(root_path)

        # Count artifacts
        artifact_counts = count_artifacts(root_path)

        # Validate metadata if requested
        validation_results = None
        if input_state.include_metadata:
            validation_results = validate_metadata(root_path)

        # Determine output path
        if input_state.output_path:
            output_path = Path(input_state.output_path)
        else:
            output_path = root_path / ".onextree"

        # Generate manifest
        manifest_path = generate_manifest(
            tree_structure, output_path, input_state.output_format
        )

        # Create success result
        result = TreeGeneratorOutputState(
            version=input_state.version,
            status="success",
            message=f"Successfully generated .onextree manifest at {manifest_path}",
            manifest_path=str(manifest_path),
            artifacts_discovered=artifact_counts,
            validation_results=validation_results,
            tree_structure=tree_structure,
        )

        # Emit success event
        success_event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_SUCCESS,
            node_id="tree_generator_node",
            metadata={"output_state": result.model_dump()},
        )
        event_bus.publish(success_event)

        # Print summary to stdout
        print(
            json.dumps(
                {
                    "status": result.status,
                    "message": result.message,
                    "artifacts_discovered": result.artifacts_discovered,
                },
                indent=2,
            )
        )

        return result

    except Exception as e:
        error_msg = f"Tree generation failed: {str(e)}"
        logger.error(error_msg, exc_info=True)

        # Create error result
        result = TreeGeneratorOutputState(
            version=input_state.version,
            status="error",
            message=error_msg,
            artifacts_discovered=None,
            validation_results=None,
        )

        # Emit failure event
        failure_event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_FAILURE,
            node_id="tree_generator_node",
            metadata={"error": error_msg, "input_state": input_state.model_dump()},
        )
        event_bus.publish(failure_event)

        return result


def main() -> None:
    """
    CLI entrypoint for standalone execution.

    Provides command-line interface for the tree generator node.
    """
    parser = argparse.ArgumentParser(
        description="Generate .onextree manifest from directory structure"
    )

    parser.add_argument(
        "--root-directory",
        type=str,
        default="src/omnibase",
        help="Root directory to scan for artifacts",
    )

    parser.add_argument(
        "--output-path",
        type=str,
        help="Output path for .onextree file (default: <root>/.onextree)",
    )

    parser.add_argument(
        "--output-format",
        type=str,
        choices=["yaml", "json"],
        default="yaml",
        help="Output format for manifest file",
    )

    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Skip metadata validation",
    )

    args = parser.parse_args()

    # Create input state from CLI arguments
    input_state = TreeGeneratorInputState(
        version="1.0.0",
        root_directory=args.root_directory,
        output_path=args.output_path,
        output_format=args.output_format,
        include_metadata=not args.no_metadata,
    )

    # Run the node
    result = run_tree_generator_node(input_state)

    # Exit with appropriate code
    sys.exit(0 if result.status == "success" else 1)


if __name__ == "__main__":
    main()
