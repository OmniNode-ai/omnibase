# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: node.py
# version: 1.0.0
# uuid: 302afe87-d2fa-48cc-a54f-1b5178d4f0b1
# author: OmniNode Team
# created_at: 2025-05-28T12:36:26.468479
# last_modified_at: 2025-05-28T17:20:04.759416
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 766c33cd523412b82d0c0ca9721e95c4cbd84cb39a36d2868909f4505029f5dc
# entrypoint: python@node.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.node
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Registry Loader Node - Main node implementation for loading ONEX registry.

This node loads and parses the ONEX registry from filesystem structure,
providing a complete catalog of available nodes, CLI tools, runtimes,
and other artifacts in the system.
"""

import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional

# Add the project root to the path for direct execution
if __name__ == "__main__":
    # Get the project root (4 levels up from this file)
    project_root = Path(__file__).parent.parent.parent.parent.parent
    sys.path.insert(0, str(project_root))

from omnibase.core.core_error_codes import OnexError, get_exit_code_for_status
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import (
    OnexVersionLoader,
)
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import telemetry

from .helpers.registry_engine import RegistryEngine
from .introspection import RegistryLoaderNodeIntrospection
from .models.state import (
    ArtifactTypeEnum,
    RegistryArtifact,
    RegistryLoaderInputState,
    RegistryLoaderOutputState,
)
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class RegistryLoaderNode(EventDrivenNodeMixin):
    def __init__(self, node_id: str = "registry_loader_node", event_bus: Optional[ProtocolEventBus] = None, **kwargs):
        super().__init__(node_id=node_id, event_bus=event_bus, **kwargs)

    @telemetry(node_name="registry_loader_node", operation="run")
    def run(self, input_state: RegistryLoaderInputState, output_state_cls: Optional[Callable[..., RegistryLoaderOutputState]] = None, handler_registry: Optional[FileTypeHandlerRegistry] = None, event_bus: Optional[ProtocolEventBus] = None, **kwargs) -> RegistryLoaderOutputState:
        if output_state_cls is None:
            output_state_cls = RegistryLoaderOutputState
        self.emit_node_start({"input_state": input_state.model_dump()})
        try:
            # Create registry engine with optional custom handler registry
            engine = RegistryEngine(handler_registry=handler_registry)

            # Example: Register node-local handlers if registry is provided
            # This demonstrates the plugin/override API for node-local handler extensions
            if handler_registry:
                emit_log_event(
                    LogLevelEnum.DEBUG,
                    "Using custom handler registry for registry file processing",
                    node_id=_COMPONENT_NAME,
                )
                # Node could register custom handlers here:
                # handler_registry.register_handler(".toml", MyTOMLHandler(), source="node-local")
                # handler_registry.register_special("registry.json", MyJSONRegistryHandler(), source="node-local")

            output = engine.load_registry(input_state)

            self.emit_node_success({
                "input_state": input_state.model_dump(),
                "output_state": output.model_dump(),
            })

            return output

        except Exception as exc:
            self.emit_node_failure({
                "input_state": input_state.model_dump(),
                "error": str(exc),
            })
            raise


def run_registry_loader_node(
    input_state: RegistryLoaderInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., RegistryLoaderOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> RegistryLoaderOutputState:
    node = RegistryLoaderNode(event_bus=event_bus)
    return node.run(input_state, output_state_cls=output_state_cls, handler_registry=handler_registry)


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
        except OnexError:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Error: Invalid artifact type. Valid types are: {', '.join([at.value for at in ArtifactTypeEnum])}",
                node_id=_COMPONENT_NAME,
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

    # Output the results
    if args.format == "json":
        emit_log_event(
            LogLevelEnum.INFO,
            output.model_dump_json(indent=2),
            node_id=_COMPONENT_NAME,
        )
    else:
        # Output summary format
        emit_log_event(
            LogLevelEnum.INFO,
            "Registry Loading Results:",
            node_id=_COMPONENT_NAME,
        )
        emit_log_event(
            LogLevelEnum.INFO,
            f"Status: {output.status.value}",
            node_id=_COMPONENT_NAME,
        )
        emit_log_event(
            LogLevelEnum.INFO,
            f"Message: {output.message}",
            node_id=_COMPONENT_NAME,
        )
        emit_log_event(
            LogLevelEnum.INFO,
            f"Root Directory: {output.root_directory}",
            node_id=_COMPONENT_NAME,
        )
        if output.onextree_path:
            emit_log_event(
                LogLevelEnum.INFO,
                f"Onextree Path: {output.onextree_path}",
                node_id=_COMPONENT_NAME,
            )
        emit_log_event(
            LogLevelEnum.INFO,
            f"Artifacts Found: {output.artifact_count}",
            node_id=_COMPONENT_NAME,
        )
        emit_log_event(
            LogLevelEnum.INFO,
            f"Artifact Types: {', '.join([at.value for at in output.artifact_types_found])}",
            node_id=_COMPONENT_NAME,
        )
        if output.scan_duration_ms:
            emit_log_event(
                LogLevelEnum.INFO,
                f"Scan Duration: {output.scan_duration_ms:.2f}ms",
                node_id=_COMPONENT_NAME,
            )

        if output.artifacts:
            emit_log_event(
                LogLevelEnum.INFO,
                "\nArtifacts by Type:",
                node_id=_COMPONENT_NAME,
            )
            by_type: Dict[ArtifactTypeEnum, List[RegistryArtifact]] = {}
            for artifact in output.artifacts:
                if artifact.artifact_type not in by_type:
                    by_type[artifact.artifact_type] = []
                by_type[artifact.artifact_type].append(artifact)

            for artifact_type, artifacts in by_type.items():
                emit_log_event(
                    LogLevelEnum.INFO,
                    f"  {artifact_type}: {len(artifacts)} artifacts",
                    node_id=_COMPONENT_NAME,
                )
                for artifact in artifacts[:5]:  # Show first 5
                    wip_marker = " (WIP)" if artifact.is_wip else ""
                    emit_log_event(
                        LogLevelEnum.INFO,
                        f"    - {artifact.name} v{artifact.version}{wip_marker}",
                        node_id=_COMPONENT_NAME,
                    )
                if len(artifacts) > 5:
                    emit_log_event(
                        LogLevelEnum.INFO,
                        f"    ... and {len(artifacts) - 5} more",
                        node_id=_COMPONENT_NAME,
                    )

    # Use canonical exit code mapping
    exit_code = get_exit_code_for_status(output.status)
    sys.exit(exit_code)


def get_introspection() -> dict:
    """Get introspection data for the registry loader node."""
    return RegistryLoaderNodeIntrospection.get_introspection_response().model_dump()


if __name__ == "__main__":
    main()
