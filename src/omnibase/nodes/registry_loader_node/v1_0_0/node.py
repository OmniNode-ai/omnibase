# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.468479'
# description: Stamped by PythonHandler
# entrypoint: python://node
# hash: 824afc07399efcd6d53be058179985e673c42ae098de04921cfdf6b1acfa0d09
# last_modified_at: '2025-05-29T14:13:59.696982+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: node.py
# namespace: python://omnibase.nodes.registry_loader_node.v1_0_0.node
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 302afe87-d2fa-48cc-a54f-1b5178d4f0b1
# version: 1.0.0
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
from omnibase.enums import LogLevel, OnexStatus
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
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
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class RegistryLoaderNode(EventDrivenNodeMixin):
    def __init__(self, event_bus: Optional[ProtocolEventBus] = None, **kwargs):
        super().__init__(node_id="registry_loader_node", event_bus=event_bus, **kwargs)
        if event_bus is None:
            raise RuntimeError('RegistryLoaderNode requires an explicit event_bus argument (protocol purity)')
        self.event_bus = event_bus

    @telemetry(node_name="registry_loader_node", operation="run")
    def run(
        self,
        input_state: RegistryLoaderInputState,
        output_state_cls: Optional[Callable[..., RegistryLoaderOutputState]] = None,
        handler_registry: Optional[FileTypeHandlerRegistry] = None,
        event_bus: Optional[ProtocolEventBus] = None,
        **kwargs,
    ) -> RegistryLoaderOutputState:
        if event_bus is None:
            event_bus = self.event_bus
        if event_bus is None:
            raise RuntimeError('RegistryLoaderNode.run requires an explicit event_bus argument (protocol purity)')
        self.emit_node_start({"input_state": input_state.model_dump()})
        try:
            # Create registry engine with optional custom handler registry
            engine = RegistryEngine(handler_registry=handler_registry, event_bus=event_bus)

            # Example: Register node-local handlers if registry is provided
            # This demonstrates the plugin/override API for node-local handler extensions
            if handler_registry:
                emit_log_event(
                    LogLevel.DEBUG,
                    "Using custom handler registry for registry file processing",
                    node_id=_COMPONENT_NAME,
                    event_bus=self.event_bus,
                )
                # Node could register custom handlers here:
                # handler_registry.register_handler(".toml", MyTOMLHandler(), source="node-local")
                # handler_registry.register_special("registry.json", MyJSONRegistryHandler(), source="node-local")

            output = engine.load_registry(input_state)

            self.emit_node_success(
                {
                    "input_state": input_state.model_dump(),
                    "output_state": output.model_dump(),
                }
            )

            return output

        except Exception as exc:
            self.emit_node_failure(
                {
                    "input_state": input_state.model_dump(),
                    "error": str(exc),
                }
            )
            raise


def run_registry_loader_node(
    input_state: RegistryLoaderInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., RegistryLoaderOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> RegistryLoaderOutputState:
    if event_bus is None:
        raise RuntimeError('run_registry_loader_node requires an explicit event_bus argument (protocol purity)')
    node = RegistryLoaderNode(event_bus=event_bus)
    return node.run(
        input_state,
        output_state_cls=output_state_cls,
        handler_registry=handler_registry,
        event_bus=event_bus,
    )


def main(event_bus=None) -> None:
    """
    Main entry point for CLI execution.
    """
    from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
    if event_bus is None:
        event_bus = InMemoryEventBus()

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
    parser.add_argument('--correlation-id', type=str, help='Correlation ID for request tracking')

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
                LogLevel.ERROR,
                f"Error: Invalid artifact type. Valid types are: {', '.join([at.value for at in ArtifactTypeEnum])}",
                node_id=_COMPONENT_NAME,
                event_bus=event_bus,
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
            LogLevel.INFO,
            output.model_dump_json(indent=2),
            node_id=_COMPONENT_NAME,
            event_bus=event_bus,
        )
    else:
        # Output summary format
        emit_log_event(
            LogLevel.INFO,
            "Registry Loading Results:",
            node_id=_COMPONENT_NAME,
            event_bus=event_bus,
        )
        emit_log_event(
            LogLevel.INFO,
            f"Status: {output.status.value}",
            node_id=_COMPONENT_NAME,
            event_bus=event_bus,
        )
        emit_log_event(
            LogLevel.INFO,
            f"Message: {output.message}",
            node_id=_COMPONENT_NAME,
            event_bus=event_bus,
        )
        emit_log_event(
            LogLevel.INFO,
            f"Root Directory: {output.root_directory}",
            node_id=_COMPONENT_NAME,
            event_bus=event_bus,
        )
        if output.onextree_path:
            emit_log_event(
                LogLevel.INFO,
                f"Onextree Path: {output.onextree_path}",
                node_id=_COMPONENT_NAME,
                event_bus=event_bus,
            )
        emit_log_event(
            LogLevel.INFO,
            f"Artifacts Found: {output.artifact_count}",
            node_id=_COMPONENT_NAME,
            event_bus=event_bus,
        )
        emit_log_event(
            LogLevel.INFO,
            f"Artifact Types: {', '.join([at.value for at in output.artifact_types_found])}",
            node_id=_COMPONENT_NAME,
            event_bus=event_bus,
        )
        if output.scan_duration_ms:
            emit_log_event(
                LogLevel.INFO,
                f"Scan Duration: {output.scan_duration_ms:.2f}ms",
                node_id=_COMPONENT_NAME,
                event_bus=event_bus,
            )

        if output.artifacts:
            emit_log_event(
                LogLevel.INFO,
                "\nArtifacts by Type:",
                node_id=_COMPONENT_NAME,
                event_bus=event_bus,
            )
            by_type: Dict[ArtifactTypeEnum, List[RegistryArtifact]] = {}
            for artifact in output.artifacts:
                if artifact.artifact_type not in by_type:
                    by_type[artifact.artifact_type] = []
                by_type[artifact.artifact_type].append(artifact)

            for artifact_type, artifacts in by_type.items():
                emit_log_event(
                    LogLevel.INFO,
                    f"  {artifact_type}: {len(artifacts)} artifacts",
                    node_id=_COMPONENT_NAME,
                    event_bus=event_bus,
                )
                for artifact in artifacts[:5]:  # Show first 5
                    wip_marker = " (WIP)" if artifact.is_wip else ""
                    emit_log_event(
                        LogLevel.INFO,
                        f"    - {artifact.name} v{artifact.version}{wip_marker}",
                        node_id=_COMPONENT_NAME,
                        event_bus=event_bus,
                    )
                if len(artifacts) > 5:
                    emit_log_event(
                        LogLevel.INFO,
                        f"    ... and {len(artifacts) - 5} more",
                        node_id=_COMPONENT_NAME,
                        event_bus=event_bus,
                    )

    # Use canonical exit code mapping
    exit_code = get_exit_code_for_status(output.status)
    sys.exit(exit_code)


def get_introspection() -> dict:
    """Get introspection data for the registry loader node."""
    return RegistryLoaderNodeIntrospection.get_introspection_response().model_dump()


if __name__ == "__main__":
    main()
