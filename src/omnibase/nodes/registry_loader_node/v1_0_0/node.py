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
# last_modified_at: 2025-05-25T20:45:00
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
Registry Loader Node - Main node implementation for loading ONEX registry.

This node loads and parses the ONEX registry from filesystem structure,
providing a complete catalog of available nodes, CLI tools, runtimes,
and other artifacts in the system.
"""

import logging
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional

# Add the project root to the path for direct execution
if __name__ == "__main__":
    # Get the project root (4 levels up from this file)
    project_root = Path(__file__).parent.parent.parent.parent.parent
    sys.path.insert(0, str(project_root))

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.error_codes import get_exit_code_for_status
from omnibase.model.enum_onex_status import OnexStatus
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import (
    OnexVersionLoader,
)

from .helpers.registry_engine import RegistryEngine
from .introspection import RegistryLoaderNodeIntrospection
from .models.state import (
    ArtifactTypeEnum,
    RegistryArtifact,
    RegistryLoaderInputState,
    RegistryLoaderOutputState,
)

logger = logging.getLogger(__name__)


def run_registry_loader_node(
    input_state: RegistryLoaderInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., RegistryLoaderOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> RegistryLoaderOutputState:
    """
    Main node entrypoint for registry loader node.

    Loads the complete ONEX registry from filesystem structure and returns
    a catalog of all discovered artifacts with their metadata.

    Args:
        input_state: RegistryLoaderInputState with loading parameters
        event_bus: ProtocolEventBus (optional, defaults to InMemoryEventBus)
        output_state_cls: Optional callable to construct output state (for testing/mocking)
        handler_registry: Optional FileTypeHandlerRegistry for custom file processing

    Returns:
        RegistryLoaderOutputState with loaded registry data

    Example of node-local handler registration:
        registry = FileTypeHandlerRegistry()
        registry.register_handler(".toml", MyTOMLHandler(), source="node-local")
        output = run_registry_loader_node(input_state, handler_registry=registry)
    """
    if event_bus is None:
        event_bus = InMemoryEventBus()
    if output_state_cls is None:
        output_state_cls = RegistryLoaderOutputState

    node_id = "registry_loader_node"

    # Emit NODE_START event
    event_bus.publish(
        OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id=node_id,
            metadata={"input_state": input_state.model_dump()},
        )
    )

    try:
        # Create registry engine with optional custom handler registry
        engine = RegistryEngine(handler_registry=handler_registry)

        # Example: Register node-local handlers if registry is provided
        # This demonstrates the plugin/override API for node-local handler extensions
        if handler_registry:
            logger.debug("Using custom handler registry for registry file processing")
            # Node could register custom handlers here:
            # handler_registry.register_handler(".toml", MyTOMLHandler(), source="node-local")
            # handler_registry.register_special("registry.json", MyJSONRegistryHandler(), source="node-local")

        output = engine.load_registry(input_state)

        # Emit NODE_SUCCESS event
        event_bus.publish(
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_SUCCESS,
                node_id=node_id,
                metadata={
                    "input_state": input_state.model_dump(),
                    "output_state": output.model_dump(),
                },
            )
        )

        return output

    except Exception as exc:
        # Create failure output state
        failure_output = output_state_cls(
            version=input_state.version,
            status=OnexStatus.ERROR,
            message=f"Registry loading failed: {str(exc)}",
            root_directory=input_state.root_directory,
        )

        # Emit NODE_FAILURE event
        event_bus.publish(
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_FAILURE,
                node_id=node_id,
                metadata={
                    "input_state": input_state.model_dump(),
                    "error": str(exc),
                },
            )
        )

        return failure_output


def main() -> None:
    """
    CLI entrypoint for standalone execution of registry loader node.

    Provides command-line interface for loading and inspecting the ONEX registry.
    """
    import argparse

    parser = argparse.ArgumentParser(description="ONEX Registry Loader Node CLI")
    parser.add_argument(
        "root_directory",
        type=str,
        nargs="?",
        help="Root directory path to scan for ONEX artifacts",
    )
    parser.add_argument(
        "--onextree-path",
        type=str,
        default=None,
        help="Path to .onextree file (optional)",
    )
    parser.add_argument(
        "--include-wip",
        action="store_true",
        help="Include work-in-progress (.wip) artifacts",
    )
    parser.add_argument(
        "--artifact-types",
        type=str,
        nargs="*",
        default=None,
        help="Filter to specific artifact types (nodes, cli_tools, runtimes, etc.)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="summary",
        help="Output format (default: summary)",
    )
    parser.add_argument(
        "--introspect",
        action="store_true",
        help="Display node contract and capabilities",
    )

    args = parser.parse_args()

    # Handle introspection command
    if args.introspect:
        RegistryLoaderNodeIntrospection.handle_introspect_command()
        return

    # Validate required arguments for normal operation
    if not args.root_directory:
        parser.error("root_directory is required when not using --introspect")

    # Get schema version
    schema_version = OnexVersionLoader().get_onex_versions().schema_version

    # Convert artifact types from strings to enums if provided
    artifact_types_enum = None
    if args.artifact_types:
        try:
            artifact_types_enum = [ArtifactTypeEnum(at) for at in args.artifact_types]
        except ValueError:
            print(
                f"Error: Invalid artifact type. Valid types are: {', '.join([at.value for at in ArtifactTypeEnum])}"
            )
            # Use canonical exit code mapping for error
            sys.exit(get_exit_code_for_status(OnexStatus.ERROR))

    # Create input state
    input_state = RegistryLoaderInputState(
        version=schema_version,
        root_directory=args.root_directory,
        onextree_path=args.onextree_path,
        include_wip=args.include_wip,
        artifact_types=artifact_types_enum,
    )

    # Run the node with default event bus for CLI
    output = run_registry_loader_node(input_state)

    # Print the output
    if args.format == "json":
        print(output.model_dump_json(indent=2))
    else:
        # Print summary format
        print("Registry Loading Results:")
        print(f"Status: {output.status.value}")
        print(f"Message: {output.message}")
        print(f"Root Directory: {output.root_directory}")
        if output.onextree_path:
            print(f"Onextree Path: {output.onextree_path}")
        print(f"Artifacts Found: {output.artifact_count}")
        print(
            f"Artifact Types: {', '.join([at.value for at in output.artifact_types_found])}"
        )
        if output.scan_duration_ms:
            print(f"Scan Duration: {output.scan_duration_ms:.2f}ms")

        if output.artifacts:
            print("\nArtifacts by Type:")
            by_type: Dict[ArtifactTypeEnum, List[RegistryArtifact]] = {}
            for artifact in output.artifacts:
                if artifact.artifact_type not in by_type:
                    by_type[artifact.artifact_type] = []
                by_type[artifact.artifact_type].append(artifact)

            for artifact_type, artifacts in by_type.items():
                print(f"  {artifact_type}: {len(artifacts)} artifacts")
                for artifact in artifacts[:5]:  # Show first 5
                    wip_marker = " (WIP)" if artifact.is_wip else ""
                    print(f"    - {artifact.name} v{artifact.version}{wip_marker}")
                if len(artifacts) > 5:
                    print(f"    ... and {len(artifacts) - 5} more")

    # Use canonical exit code mapping
    exit_code = get_exit_code_for_status(output.status)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
