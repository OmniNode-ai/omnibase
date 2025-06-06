# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.048107'
# description: Stamped by PythonHandler
# entrypoint: python://node
# hash: 869cfa8f9999c14b67bc2ffbfbc06cd1cbd2f624565c6b3eeaf844d139ccf81d
# last_modified_at: '2025-05-29T14:14:00.163567+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: node.py
# namespace: python://omnibase.nodes.node_tree_generator.v1_0_0.node
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: eef32a1b-9a2e-4b31-b8a1-902baa4f3b96
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Tree Generator Node - Generates .onextree manifest files from directory structure analysis.

This node scans a directory tree and creates a manifest file that catalogs all artifacts
(nodes, adapters, contracts, runtimes, CLI tools, packages) with their versions and metadata.
"""

import sys
from pathlib import Path
from typing import Callable, Optional

import yaml

from omnibase.core.core_error_codes import get_exit_code_for_status
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.model.model_project_metadata import (
    PROJECT_ONEX_YAML_PATH,
    ProjectMetadataBlock,
)
from omnibase.model.model_semver import SemVerModel
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import telemetry
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import (
    OnexVersionLoader,
)

from .constants import (
    MSG_ERROR_DIRECTORY_NOT_FOUND,
    MSG_ERROR_UNKNOWN,
    MSG_SUCCESS_TEMPLATE,
    NODE_NAME,
    NODE_VERSION,
)
from .helpers.tree_generator_engine import TreeGeneratorEngine
from .helpers.tree_validator import OnextreeValidator
from .introspection import TreeGeneratorNodeIntrospection
from .models.state import TreeGeneratorInputState, TreeGeneratorOutputState

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class TreeGeneratorNode(EventDrivenNodeMixin):
    def __init__(self, event_bus: Optional[ProtocolEventBus] = None, **kwargs):
        super().__init__(node_id="node_tree_generator", event_bus=event_bus, **kwargs)
        self.event_bus = event_bus or get_event_bus(mode="bind")  # Publisher
        # Load project config from YAML
        with open(PROJECT_ONEX_YAML_PATH, "r") as f:
            project_data = yaml.safe_load(f)
        # Patch: Ensure entrypoint is a string or EntrypointBlock
        if "entrypoint" in project_data:
            entrypoint_val = project_data["entrypoint"]
            if isinstance(entrypoint_val, dict):
                # Convert dict to URI string if possible
                if "type" in entrypoint_val and "target" in entrypoint_val:
                    project_data["entrypoint"] = (
                        f"{entrypoint_val['type']}://{entrypoint_val['target']}"
                    )
        self.project_config = ProjectMetadataBlock.from_dict(project_data)
        self.engine = TreeGeneratorEngine(
            event_bus=self.event_bus, project_config=self.project_config
        )

    @telemetry(node_name="node_tree_generator", operation="run")
    def run(
        self,
        input_state: TreeGeneratorInputState,
        output_state_cls: Optional[Callable[..., TreeGeneratorOutputState]] = None,
        handler_registry: Optional[FileTypeHandlerRegistry] = None,
        event_bus: Optional[ProtocolEventBus] = None,
        **kwargs,
    ) -> TreeGeneratorOutputState:
        if output_state_cls is None:
            output_state_cls = TreeGeneratorOutputState
        self.emit_node_start({"input_state": input_state.model_dump()})
        try:
            # Validate input directory exists
            root_path = Path(input_state.root_directory)
            if not root_path.exists():
                error_msg = MSG_ERROR_DIRECTORY_NOT_FOUND.format(
                    path=input_state.root_directory
                )
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    error_msg,
                    node_id=_COMPONENT_NAME,
                    event_bus=self.event_bus,
                )

                self.emit_node_failure(
                    {
                        "input_state": input_state.model_dump(),
                        "error": error_msg,
                    }
                )

                return output_state_cls(
                    version=input_state.version,
                    status=OnexStatus.ERROR,
                    message=error_msg,
                    artifacts_discovered=None,
                    validation_results=None,
                )

            if not root_path.is_dir():
                error_msg = MSG_ERROR_DIRECTORY_NOT_FOUND.format(
                    path=input_state.root_directory
                )
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    error_msg,
                    node_id=_COMPONENT_NAME,
                    event_bus=self.event_bus,
                )

                self.emit_node_failure(
                    {
                        "input_state": input_state.model_dump(),
                        "error": error_msg,
                    }
                )

                return output_state_cls(
                    version=input_state.version,
                    status=OnexStatus.ERROR,
                    message=error_msg,
                    artifacts_discovered=None,
                    validation_results=None,
                )

            # Initialize tree generator engine with optional custom handler registry
            engine = TreeGeneratorEngine(
                handler_registry=handler_registry,
                event_bus=self.event_bus,
                project_config=self.project_config,
            )

            # Example: Register node-local handlers if registry is provided
            # This demonstrates the plugin/override API for node-local handler extensions
            if handler_registry:
                emit_log_event_sync(
                    LogLevelEnum.DEBUG,
                    "Using custom handler registry for metadata processing",
                    node_id=_COMPONENT_NAME,
                    event_bus=self.event_bus,
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
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    error_msg,
                    node_id=_COMPONENT_NAME,
                    event_bus=self.event_bus,
                )

                self.emit_node_failure(
                    {
                        "input_state": input_state.model_dump(),
                        "error": error_msg,
                    }
                )

                return output_state_cls(
                    version=input_state.version,
                    status=OnexStatus.ERROR,
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
                validator = OnextreeValidator(event_bus=self.event_bus)
                if manifest_path:
                    validation_result = validator.validate_onextree_file(
                        onextree_path=Path(manifest_path),
                        root_directory=Path(input_state.root_directory),
                    )
                    validation_results = validation_result.model_dump()
            except Exception as e:
                emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"Validation failed: {e}",
                    node_id=_COMPONENT_NAME,
                    event_bus=self.event_bus,
                )
                # Don't fail the whole operation if validation fails

            success_msg = MSG_SUCCESS_TEMPLATE.format(path=manifest_path)
            emit_log_event_sync(
                LogLevelEnum.INFO,
                success_msg,
                node_id=_COMPONENT_NAME,
                event_bus=self.event_bus,
            )

            output = output_state_cls(
                version=input_state.version,
                status=OnexStatus.SUCCESS,
                message=success_msg,
                artifacts_discovered=artifacts_discovered,
                validation_results=validation_results,
            )
            self.emit_node_success(
                {
                    "input_state": input_state.model_dump(),
                    "output_state": output.model_dump(),
                }
            )
            return output

        except Exception as e:
            error_msg = MSG_ERROR_UNKNOWN.format(error=str(e))
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                error_msg,
                node_id=_COMPONENT_NAME,
                event_bus=self.event_bus,
            )

            self.emit_node_failure(
                {
                    "input_state": input_state.model_dump(),
                    "error": error_msg,
                }
            )

            return output_state_cls(
                version=input_state.version,
                status=OnexStatus.ERROR,
                message=error_msg,
                artifacts_discovered=None,
                validation_results=None,
            )


def run_node_tree_generator(
    input_state: TreeGeneratorInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., TreeGeneratorOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
    file_io: Optional[FileTypeHandlerRegistry] = None,
) -> TreeGeneratorOutputState:
    if event_bus is None:
        event_bus = get_event_bus(mode="bind")  # Publisher
    node = TreeGeneratorNode(event_bus=event_bus)
    return node.run(
        input_state,
        output_state_cls=output_state_cls,
        handler_registry=handler_registry,
        event_bus=event_bus,
        file_io=file_io,
    )


def main() -> TreeGeneratorOutputState:
    """
    Protocol-pure entrypoint: never print or sys.exit. Always return a canonical output model.
    """
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
    parser.add_argument(
        "--correlation-id", type=str, help="Correlation ID for request tracking"
    )
    args = parser.parse_args()

    if args.introspect:
        TreeGeneratorNodeIntrospection.handle_introspect_command()
        return None

    # Validate required arguments for normal operation
    if not args.root_directory or not args.output_path:
        return TreeGeneratorOutputState(
            version="1.0.0",
            status=OnexStatus.ERROR.value,
            message="--root-directory and --output-path are required when not using --introspect",
        )

    try:
        # Run the tree generator logic (assume function run_tree_generator exists)
        output = run_tree_generator(
            root_directory=args.root_directory,
            output_path=args.output_path,
            output_format=args.output_format,
            no_metadata=args.no_metadata,
            validate=args.validate,
            verbose=args.verbose,
            correlation_id=args.correlation_id,
        )
        return output
    except Exception as e:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"Tree generator node error: {e}",
            node_id="node_tree_generator",
            event_bus=None,
        )
        return TreeGeneratorOutputState(
            version="1.0.0",
            status=OnexStatus.ERROR.value,
            message=f"Tree generator node error: {e}",
        )


def get_introspection() -> dict:
    """Get introspection data for the tree generator node."""
    return TreeGeneratorNodeIntrospection.get_introspection_response().model_dump()


if __name__ == "__main__":
    main()
