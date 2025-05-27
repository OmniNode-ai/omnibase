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
Tree Generator Node - Generates .onextree manifest files from directory structure analysis.

This node scans a directory tree and creates a manifest file that catalogs all artifacts
(nodes, adapters, contracts, runtimes, CLI tools, packages) with their versions and metadata.
"""

import sys
from pathlib import Path
from typing import Optional

from omnibase.core.core_error_codes import get_exit_code_for_status
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import (
    OnexVersionLoader,
)

from .constants import (
    MSG_ERROR_DIRECTORY_NOT_FOUND,
    MSG_ERROR_UNKNOWN,
    MSG_SUCCESS_TEMPLATE,
    NODE_NAME,
    NODE_VERSION,
    STATUS_ERROR,
    STATUS_SUCCESS,
)
from .helpers.tree_generator_engine import TreeGeneratorEngine
from .helpers.tree_validator import OnextreeValidator
from .introspection import TreeGeneratorNodeIntrospection
from .models.state import TreeGeneratorInputState, TreeGeneratorOutputState

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


def run_tree_generator_node(
    input_state: TreeGeneratorInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> TreeGeneratorOutputState:
    """
    Generate .onextree manifest file from directory structure analysis.

    Args:
        input_state: Input configuration containing root directory and output path
        event_bus: Optional event bus for emitting execution events
        handler_registry: Optional FileTypeHandlerRegistry for custom file processing

    Returns:
        TreeGeneratorOutputState: Results of tree generation including artifacts discovered

    Example of node-local handler registration:
        registry = FileTypeHandlerRegistry()
        registry.register_handler(".toml", MyTOMLHandler(), source="node-local")
        output = run_tree_generator_node(input_state, handler_registry=registry)
    """
    # Emit start event
    if event_bus:
        start_event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id=f"{NODE_NAME}:{NODE_VERSION}",
            metadata={"input_state": input_state.model_dump()},
        )
        event_bus.publish(start_event)

    try:
        # Validate input directory exists
        root_path = Path(input_state.root_directory)
        if not root_path.exists():
            error_msg = MSG_ERROR_DIRECTORY_NOT_FOUND.format(
                path=input_state.root_directory
            )
            emit_log_event(
                LogLevelEnum.ERROR,
                error_msg,
                node_id=_COMPONENT_NAME,
            )

            if event_bus:
                failure_event = OnexEvent(
                    event_type=OnexEventTypeEnum.NODE_FAILURE,
                    node_id=f"{NODE_NAME}:{NODE_VERSION}",
                    metadata={"error": error_msg},
                )
                event_bus.publish(failure_event)

            return TreeGeneratorOutputState(
                version=input_state.version,
                status=STATUS_ERROR,
                message=error_msg,
                artifacts_discovered=None,
                validation_results=None,
            )

        if not root_path.is_dir():
            error_msg = MSG_ERROR_DIRECTORY_NOT_FOUND.format(
                path=input_state.root_directory
            )
            emit_log_event(
                LogLevelEnum.ERROR,
                error_msg,
                node_id=_COMPONENT_NAME,
            )

            if event_bus:
                failure_event = OnexEvent(
                    event_type=OnexEventTypeEnum.NODE_FAILURE,
                    node_id=f"{NODE_NAME}:{NODE_VERSION}",
                    metadata={"error": error_msg},
                )
                event_bus.publish(failure_event)

            return TreeGeneratorOutputState(
                version=input_state.version,
                status=STATUS_ERROR,
                message=error_msg,
                artifacts_discovered=None,
                validation_results=None,
            )

        # Initialize tree generator engine with optional custom handler registry
        engine = TreeGeneratorEngine(handler_registry=handler_registry)

        # Example: Register node-local handlers if registry is provided
        # This demonstrates the plugin/override API for node-local handler extensions
        if handler_registry:
            emit_log_event(
                LogLevelEnum.DEBUG,
                "Using custom handler registry for metadata processing",
                node_id=_COMPONENT_NAME,
            )
            # Node could register custom handlers here:
            # handler_registry.register_handler(".toml", MyTOMLHandler(), source="node-local")
            # handler_registry.register_handler(".json5", MyJSON5Handler(), source="node-local")

        # Generate the tree using the engine
        result = engine.generate_tree(
            root_directory=input_state.root_directory,
            output_path=input_state.output_path,
            output_format=getattr(input_state, "output_format", "yaml"),
            include_metadata=getattr(input_state, "include_metadata", True),
        )

        # Check if generation was successful
        if result.status.value == "error":
            error_msg = (
                result.metadata.get("error", "Unknown error during tree generation")
                if result.metadata
                else "Unknown error during tree generation"
            )
            emit_log_event(
                LogLevelEnum.ERROR,
                error_msg,
                node_id=_COMPONENT_NAME,
            )

            if event_bus:
                failure_event = OnexEvent(
                    event_type=OnexEventTypeEnum.NODE_FAILURE,
                    node_id=f"{NODE_NAME}:{NODE_VERSION}",
                    metadata={"error": error_msg},
                )
                event_bus.publish(failure_event)

            return TreeGeneratorOutputState(
                version=input_state.version,
                status=STATUS_ERROR,
                message=error_msg,
                artifacts_discovered=None,
                validation_results=None,
            )

        # Extract results from engine output
        metadata = result.metadata or {}
        artifacts_discovered = metadata.get("artifacts_discovered")
        validation_results = metadata.get("validation_results")
        manifest_path = metadata.get("manifest_path")

        # Validate the generated file if validator is available
        try:
            validator = OnextreeValidator()
            if manifest_path:
                validation_result = validator.validate_onextree_file(
                    onextree_path=Path(manifest_path),
                    root_directory=Path(input_state.root_directory),
                )
                validation_results = validation_result.model_dump()
        except Exception as e:
            emit_log_event(
                LogLevelEnum.WARNING,
                f"Validation failed: {e}",
                node_id=_COMPONENT_NAME,
            )
            # Don't fail the whole operation if validation fails

        success_msg = MSG_SUCCESS_TEMPLATE.format(path=manifest_path)
        emit_log_event(
            LogLevelEnum.INFO,
            success_msg,
            node_id=_COMPONENT_NAME,
        )

        # Emit success event
        if event_bus:
            success_event = OnexEvent(
                event_type=OnexEventTypeEnum.NODE_SUCCESS,
                node_id=f"{NODE_NAME}:{NODE_VERSION}",
                metadata={
                    "output_path": manifest_path,
                    "artifacts_discovered": artifacts_discovered,
                },
            )
            event_bus.publish(success_event)

        return TreeGeneratorOutputState(
            version=input_state.version,
            status=STATUS_SUCCESS,
            message=success_msg,
            artifacts_discovered=artifacts_discovered,
            validation_results=validation_results,
        )

    except Exception as e:
        error_msg = MSG_ERROR_UNKNOWN.format(error=str(e))
        emit_log_event(
            LogLevelEnum.ERROR,
            error_msg,
            node_id=_COMPONENT_NAME,
        )

        if event_bus:
            failure_event = OnexEvent(
                event_type=OnexEventTypeEnum.NODE_FAILURE,
                node_id=f"{NODE_NAME}:{NODE_VERSION}",
                metadata={"error": error_msg},
            )
            event_bus.publish(failure_event)

        return TreeGeneratorOutputState(
            version=input_state.version,
            status=STATUS_ERROR,
            message=error_msg,
            artifacts_discovered=None,
            validation_results=None,
        )


def main() -> None:
    """CLI entrypoint for standalone execution."""
    import argparse

    parser = argparse.ArgumentParser(description="ONEX Tree Generator Node CLI")
    parser.add_argument(
        "--root-directory",
        type=str,
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
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate .onextree file against directory",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--introspect",
        action="store_true",
        help="Enable introspection",
    )
    args = parser.parse_args()

    # Handle introspection command
    if args.introspect:
        TreeGeneratorNodeIntrospection.handle_introspect_command()
        return

    # Validate required arguments for normal operation
    if not args.root_directory or not args.output_path:
        parser.error(
            "--root-directory and --output-path are required when not using --introspect"
        )

    if args.validate:
        validator = OnextreeValidator(verbose=args.verbose)
        onextree_path = (
            Path(args.output_path)
            if args.output_path
            else Path(args.root_directory) / ".onextree"
        )
        result = validator.validate_onextree_file(
            onextree_path=onextree_path,
            root_directory=Path(args.root_directory),
        )
        validator.print_results(result)
        # Use canonical exit code mapping
        exit_code = get_exit_code_for_status(OnexStatus(result.status))
        sys.exit(exit_code)
    else:
        # Generation mode
        schema_version = OnexVersionLoader().get_onex_versions().schema_version
        input_state = TreeGeneratorInputState(
            version=schema_version,
            root_directory=args.root_directory,
            output_path=args.output_path,
            output_format=args.output_format,
            include_metadata=not args.no_metadata,
        )
        # Use default event bus for CLI
        output = run_tree_generator_node(input_state)
        emit_log_event(
            LogLevelEnum.INFO, output.model_dump_json(indent=2), node_id=_COMPONENT_NAME
        )

        # Use canonical exit code mapping
        exit_code = get_exit_code_for_status(OnexStatus(output.status))
        sys.exit(exit_code)


def get_introspection() -> dict:
    """Get introspection data for the tree generator node."""
    return TreeGeneratorNodeIntrospection.get_introspection_response().model_dump()


if __name__ == "__main__":
    main()
