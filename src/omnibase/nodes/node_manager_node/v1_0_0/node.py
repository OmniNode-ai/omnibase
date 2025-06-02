# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T09:34:52.828785'
# description: Stamped by PythonHandler
# entrypoint: python://node
# hash: 503447dc9d4cce168747e50076b334fa8d7ba6b99bfc45d9a780004ed5e33a50
# last_modified_at: '2025-05-29T14:13:59.423665+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: node.py
# namespace: python://omnibase.nodes.node_manager_node.v1_0_0.node
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 345d9587-a4ef-4745-abc8-f7072406d3cd
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
NodeManagerNode: ONEX node for managing nodes (generation and maintenance).

This node provides comprehensive node management capabilities including:
- Generating new ONEX nodes from templates
- Regenerating contracts and manifests for existing nodes
- Maintaining and fixing node health issues
- Synchronizing configuration files
"""

import sys
from pathlib import Path
from typing import Callable, Optional

from omnibase.core.core_error_codes import get_exit_code_for_status
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevel, OnexStatus
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import telemetry
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import (
    OnexVersionLoader,
)

from .introspection import NodeManagerIntrospection

# Import updated state models
from .models.state import (
    NodeManagerInputState,
    NodeManagerOperation,
    NodeManagerOutputState,
    create_node_manager_output_state,
)

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class NodeManagerNode(EventDrivenNodeMixin):
    def __init__(self, event_bus: Optional[ProtocolEventBus] = None, **kwargs):
        super().__init__(node_id="node_manager_node", event_bus=event_bus, **kwargs)
        self.event_bus = event_bus or InMemoryEventBus()

    @telemetry(node_name="node_manager_node", operation="run")
    def run(
        self,
        input_state: NodeManagerInputState,
        output_state_cls: Optional[Callable[..., NodeManagerOutputState]] = None,
        handler_registry: Optional[FileTypeHandlerRegistry] = None,
        event_bus: Optional[ProtocolEventBus] = None,
        **kwargs,
    ) -> NodeManagerOutputState:
        if output_state_cls is None:
            output_state_cls = create_node_manager_output_state
        self.emit_node_start({"input_state": input_state.model_dump()})
        try:
            # Register node-local handlers if registry is provided
            if handler_registry:
                emit_log_event(
                    LogLevel.DEBUG,
                    "Using custom handler registry for file processing",
                    node_id=_COMPONENT_NAME,
                    event_bus=self.event_bus,
                )
            # Route to appropriate operation handler
            if input_state.operation == NodeManagerOperation.GENERATE:
                output = _handle_generate_operation(
                    input_state, self.event_bus, output_state_cls
                )
            elif input_state.operation == NodeManagerOperation.REGENERATE_CONTRACT:
                output = _handle_regenerate_contract_operation(
                    input_state, self.event_bus, output_state_cls
                )
            elif input_state.operation == NodeManagerOperation.REGENERATE_MANIFEST:
                output = _handle_regenerate_manifest_operation(
                    input_state, self.event_bus, output_state_cls
                )
            elif input_state.operation == NodeManagerOperation.FIX_NODE_HEALTH:
                output = _handle_fix_node_health_operation(
                    input_state, self.event_bus, output_state_cls
                )
            elif input_state.operation == NodeManagerOperation.SYNCHRONIZE_CONFIGS:
                output = _handle_synchronize_configs_operation(
                    input_state, self.event_bus, output_state_cls
                )
            else:
                raise ValueError(f"Unsupported operation: {input_state.operation}")
            self.emit_node_success(
                {
                    "input_state": input_state.model_dump(),
                    "output_state": output.model_dump(),
                }
            )
            return output
        except Exception as e:
            emit_log_event(
                LogLevel.ERROR,
                f"Node manager operation failed: {str(e)}",
                node_id=_COMPONENT_NAME,
                event_bus=self.event_bus,
            )
            self.emit_node_failure(
                {
                    "input_state": input_state.model_dump(),
                    "error": str(e),
                }
            )
            # Create error output state
            output = output_state_cls(
                operation=input_state.operation,
                status=OnexStatus.ERROR,
                message=f"Operation failed: {str(e)}",
                input_state=input_state,
            )
            return output


def _handle_generate_operation(
    input_state: NodeManagerInputState,
    event_bus: ProtocolEventBus,
    output_state_cls: Callable[..., NodeManagerOutputState],
) -> NodeManagerOutputState:
    """Handle node generation operations."""
    # Import helper engines for node generation
    from .helpers.file_generator import FileGenerator
    from .helpers.template_engine import TemplateEngine
    from .helpers.validation_engine import ValidationEngine

    # Initialize engines
    template_engine = TemplateEngine()
    validation_engine = ValidationEngine()
    file_generator = FileGenerator()

    emit_log_event(
        LogLevel.INFO,
        f"Starting node generation: {input_state.node_name} from {input_state.template_source}",
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )

    # Step 1: Validate template source exists
    template_path = Path(input_state.template_source)
    if not template_path.exists():
        # Try relative to nodes directory
        template_path = Path("src/omnibase/nodes") / input_state.template_source
        if not template_path.exists():
            raise ValueError(
                f"Template source not found: {input_state.template_source}"
            )

    # Step 2: Generate target directory path
    target_path = Path(input_state.target_directory) / f"{input_state.node_name}_node"

    # Step 3: Copy and customize template
    generated_files = file_generator.copy_template_structure(
        template_path=template_path,
        target_path=target_path,
        node_name=input_state.node_name,
        customizations=input_state.customizations or {},
    )

    # Step 4: Process templates with customizations
    template_engine.process_templates(
        target_path=target_path,
        node_name=input_state.node_name,
        author=input_state.author,
        customizations=input_state.customizations or {},
    )

    # Step 5: Validate generated node
    validation_results = validation_engine.validate_generated_node(
        node_path=target_path, node_name=input_state.node_name
    )

    # Step 6: Optional post-generation tasks
    warnings = []
    next_steps = []

    if input_state.generation_options and input_state.generation_options.get(
        "run_initial_stamping", True
    ):
        try:
            file_generator.run_initial_stamping(target_path)
            next_steps.append("Initial file stamping completed")
        except Exception as e:
            warnings.append(f"Initial stamping failed: {str(e)}")

    if input_state.generation_options and input_state.generation_options.get(
        "generate_onextree", True
    ):
        try:
            file_generator.generate_onextree(target_path)
            next_steps.append("Generated .onextree file")
        except Exception as e:
            warnings.append(f"Failed to generate .onextree: {str(e)}")

    # Determine overall status
    status = OnexStatus.SUCCESS
    if validation_results.get("errors"):
        status = OnexStatus.ERROR
    elif warnings:
        status = OnexStatus.WARNING

    result_message = f"Generated node '{input_state.node_name}' from template '{input_state.template_source}'"
    if warnings:
        result_message += f" with {len(warnings)} warnings"

    # Create output state
    return output_state_cls(
        operation=input_state.operation,
        status=status,
        message=result_message,
        input_state=input_state,
        affected_files=generated_files,
        node_directory=str(target_path),
        processed_nodes=[input_state.node_name],
        validation_results=validation_results,
        warnings=warnings,
        next_steps=next_steps,
    )


def _handle_regenerate_contract_operation(
    input_state: NodeManagerInputState,
    event_bus: ProtocolEventBus,
    output_state_cls: Callable[..., NodeManagerOutputState],
) -> NodeManagerOutputState:
    """Handle contract regeneration operations."""
    from .helpers.helpers_maintenance import NodeMaintenanceGenerator

    maintenance_generator = NodeMaintenanceGenerator(
        backup_enabled=input_state.backup_enabled
    )

    emit_log_event(
        LogLevel.INFO,
        f"Starting contract regeneration (dry_run={input_state.dry_run})",
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )

    # Get nodes to process
    nodes_to_process = input_state.nodes or []
    if not nodes_to_process:
        # Find all nodes in target directory
        nodes_dir = Path(input_state.target_directory)
        if nodes_dir.exists():
            nodes_to_process = [
                d.name
                for d in nodes_dir.iterdir()
                if d.is_dir() and d.name.endswith("_node")
            ]

    affected_files = []
    processed_nodes = []
    warnings = []

    for node_name in nodes_to_process:
        try:
            node_path = Path(input_state.target_directory) / node_name
            if not node_path.exists():
                warnings.append(f"Node directory not found: {node_path}")
                continue

            result = maintenance_generator.regenerate_contract(
                node_path=node_path, dry_run=input_state.dry_run
            )

            if result.metadata and result.metadata.get("contract_path"):
                affected_files.append(str(result.metadata["contract_path"]))
            processed_nodes.append(node_name)

        except Exception as e:
            warnings.append(f"Failed to regenerate contract for {node_name}: {str(e)}")

    status = OnexStatus.SUCCESS if processed_nodes else OnexStatus.WARNING
    if warnings and not processed_nodes:
        status = OnexStatus.ERROR

    action_word = "Would regenerate" if input_state.dry_run else "Regenerated"
    message = f"{action_word} contracts for {len(processed_nodes)} nodes"

    return output_state_cls(
        operation=input_state.operation,
        status=status,
        message=message,
        input_state=input_state,
        affected_files=affected_files,
        processed_nodes=processed_nodes,
        warnings=warnings,
        operation_details={
            "dry_run": input_state.dry_run,
            "backup_enabled": input_state.backup_enabled,
        },
    )


def _handle_regenerate_manifest_operation(
    input_state: NodeManagerInputState,
    event_bus: ProtocolEventBus,
    output_state_cls: Callable[..., NodeManagerOutputState],
) -> NodeManagerOutputState:
    """Handle manifest regeneration operations."""
    from .helpers.helpers_maintenance import NodeMaintenanceGenerator

    maintenance_generator = NodeMaintenanceGenerator(
        backup_enabled=input_state.backup_enabled
    )

    emit_log_event(
        LogLevel.INFO,
        f"Starting manifest regeneration (dry_run={input_state.dry_run})",
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )

    # Get nodes to process
    nodes_to_process = input_state.nodes or []
    if not nodes_to_process:
        # Find all nodes in target directory
        nodes_dir = Path(input_state.target_directory)
        if nodes_dir.exists():
            nodes_to_process = [
                d.name
                for d in nodes_dir.iterdir()
                if d.is_dir() and d.name.endswith("_node")
            ]

    affected_files = []
    processed_nodes = []
    warnings = []

    for node_name in nodes_to_process:
        try:
            node_path = Path(input_state.target_directory) / node_name
            if not node_path.exists():
                warnings.append(f"Node directory not found: {node_path}")
                continue

            result = maintenance_generator.regenerate_manifest(
                node_path=node_path, dry_run=input_state.dry_run
            )

            if result.metadata and result.metadata.get("manifest_path"):
                affected_files.append(str(result.metadata["manifest_path"]))
            processed_nodes.append(node_name)

        except Exception as e:
            warnings.append(f"Failed to regenerate manifest for {node_name}: {str(e)}")

    status = OnexStatus.SUCCESS if processed_nodes else OnexStatus.WARNING
    if warnings and not processed_nodes:
        status = OnexStatus.ERROR

    action_word = "Would regenerate" if input_state.dry_run else "Regenerated"
    message = f"{action_word} manifests for {len(processed_nodes)} nodes"

    return output_state_cls(
        operation=input_state.operation,
        status=status,
        message=message,
        input_state=input_state,
        affected_files=affected_files,
        processed_nodes=processed_nodes,
        warnings=warnings,
        operation_details={
            "dry_run": input_state.dry_run,
            "backup_enabled": input_state.backup_enabled,
        },
    )


def _handle_fix_node_health_operation(
    input_state: NodeManagerInputState,
    event_bus: ProtocolEventBus,
    output_state_cls: Callable[..., NodeManagerOutputState],
) -> NodeManagerOutputState:
    """Handle comprehensive node health fixing operations."""
    from .helpers.helpers_maintenance import NodeMaintenanceGenerator

    maintenance_generator = NodeMaintenanceGenerator(
        backup_enabled=input_state.backup_enabled
    )

    emit_log_event(
        LogLevel.INFO,
        f"Starting node health fixing (dry_run={input_state.dry_run})",
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )

    # Get nodes to process
    nodes_to_process = input_state.nodes or []
    if not nodes_to_process:
        # Find all nodes in target directory
        nodes_dir = Path(input_state.target_directory)
        if nodes_dir.exists():
            nodes_to_process = [
                d.name
                for d in nodes_dir.iterdir()
                if d.is_dir() and d.name.endswith("_node")
            ]

    affected_files = []
    processed_nodes = []
    warnings = []

    for node_name in nodes_to_process:
        try:
            node_path = Path(input_state.target_directory) / node_name
            if not node_path.exists():
                warnings.append(f"Node directory not found: {node_path}")
                continue

            result = maintenance_generator.fix_node_health(
                node_path=node_path, dry_run=input_state.dry_run
            )

            if result.metadata and result.metadata.get("fixes_applied"):
                # Add placeholder files for the fixes that would be applied
                for fix_type in result.metadata["fixes_applied"]:
                    if fix_type == "contract":
                        affected_files.append(str(node_path / "contract.yaml"))
                    elif fix_type == "manifest":
                        affected_files.append(str(node_path / "node.onex.yaml"))
                    elif fix_type == "configurations":
                        affected_files.append(str(node_path / ".onexignore"))
            processed_nodes.append(node_name)

        except Exception as e:
            warnings.append(f"Failed to fix node health for {node_name}: {str(e)}")

    status = OnexStatus.SUCCESS if processed_nodes else OnexStatus.WARNING
    if warnings and not processed_nodes:
        status = OnexStatus.ERROR

    action_word = "Would fix" if input_state.dry_run else "Fixed"
    message = f"{action_word} health issues for {len(processed_nodes)} nodes"

    return output_state_cls(
        operation=input_state.operation,
        status=status,
        message=message,
        input_state=input_state,
        affected_files=affected_files,
        processed_nodes=processed_nodes,
        warnings=warnings,
        operation_details={
            "dry_run": input_state.dry_run,
            "backup_enabled": input_state.backup_enabled,
        },
    )


def _handle_synchronize_configs_operation(
    input_state: NodeManagerInputState,
    event_bus: ProtocolEventBus,
    output_state_cls: Callable[..., NodeManagerOutputState],
) -> NodeManagerOutputState:
    """Handle configuration synchronization operations."""
    from .helpers.helpers_maintenance import NodeMaintenanceGenerator

    maintenance_generator = NodeMaintenanceGenerator(
        backup_enabled=input_state.backup_enabled
    )

    emit_log_event(
        LogLevel.INFO,
        f"Starting configuration synchronization (dry_run={input_state.dry_run})",
        node_id=_COMPONENT_NAME,
        event_bus=event_bus,
    )

    # Get nodes to process
    nodes_to_process = input_state.nodes or []
    if not nodes_to_process:
        # Find all nodes in target directory
        nodes_dir = Path(input_state.target_directory)
        if nodes_dir.exists():
            nodes_to_process = [
                d.name
                for d in nodes_dir.iterdir()
                if d.is_dir() and d.name.endswith("_node")
            ]

    affected_files = []
    processed_nodes = []
    warnings = []

    for node_name in nodes_to_process:
        try:
            node_path = Path(input_state.target_directory) / node_name
            if not node_path.exists():
                warnings.append(f"Node directory not found: {node_path}")
                continue

            result = maintenance_generator.synchronize_configurations(
                node_path=node_path, dry_run=input_state.dry_run
            )

            if result.metadata and result.metadata.get("synchronized_files"):
                for sync_file in result.metadata["synchronized_files"]:
                    affected_files.append(str(node_path / sync_file))
            processed_nodes.append(node_name)

        except Exception as e:
            warnings.append(f"Failed to synchronize configs for {node_name}: {str(e)}")

    status = OnexStatus.SUCCESS if processed_nodes else OnexStatus.WARNING
    if warnings and not processed_nodes:
        status = OnexStatus.ERROR

    action_word = "Would synchronize" if input_state.dry_run else "Synchronized"
    message = f"{action_word} configurations for {len(processed_nodes)} nodes"

    return output_state_cls(
        operation=input_state.operation,
        status=status,
        message=message,
        input_state=input_state,
        affected_files=affected_files,
        processed_nodes=processed_nodes,
        warnings=warnings,
        operation_details={
            "dry_run": input_state.dry_run,
            "backup_enabled": input_state.backup_enabled,
        },
    )


def run_node_manager(
    input_state: NodeManagerInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., NodeManagerOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> NodeManagerOutputState:
    """
    Main orchestration function for node management operations.
    Instantiates NodeManagerNode and delegates to its run method.
    """
    node = NodeManagerNode(event_bus=event_bus)
    return node.run(
        input_state=input_state,
        output_state_cls=output_state_cls,
        handler_registry=handler_registry,
        event_bus=event_bus,
    )


# Legacy function for backward compatibility
def run_node_generator(
    input_state: NodeManagerInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., NodeManagerOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> NodeManagerOutputState:
    """Legacy function for backward compatibility."""
    return run_node_manager(input_state, event_bus, output_state_cls, handler_registry)


def main() -> None:
    """
    CLI entrypoint for NodeManagerNode standalone execution.
    """
    import argparse

    parser = argparse.ArgumentParser(description="ONEX Node Manager CLI")

    # Add operation subcommands
    subparsers = parser.add_subparsers(
        dest="operation", help="Node management operations"
    )

    # Generate operation
    generate_parser = subparsers.add_parser(
        "generate", help="Generate a new node from template"
    )
    generate_parser.add_argument("node_name", help="Name of the new node to generate")
    generate_parser.add_argument(
        "--template",
        default="template_node",
        help="Template source (default: template_node)",
    )
    generate_parser.add_argument(
        "--target-directory",
        default="src/omnibase/nodes",
        help="Target directory (default: src/omnibase/nodes)",
    )
    generate_parser.add_argument(
        "--author", default="OmniNode Team", help="Author name (default: OmniNode Team)"
    )

    # Regenerate contract operation
    contract_parser = subparsers.add_parser(
        "regenerate-contract", help="Regenerate contract.yaml files"
    )
    contract_parser.add_argument(
        "--nodes", nargs="*", help="Specific node names to process (default: all nodes)"
    )
    contract_parser.add_argument(
        "--target-directory",
        default="src/omnibase/nodes",
        help="Target directory (default: src/omnibase/nodes)",
    )
    contract_parser.add_argument(
        "--apply", action="store_true", help="Apply changes (default: dry-run)"
    )
    contract_parser.add_argument(
        "--no-backup", action="store_true", help="Disable backup creation"
    )

    # Regenerate manifest operation
    manifest_parser = subparsers.add_parser(
        "regenerate-manifest", help="Regenerate node.onex.yaml files"
    )
    manifest_parser.add_argument(
        "--nodes", nargs="*", help="Specific node names to process (default: all nodes)"
    )
    manifest_parser.add_argument(
        "--target-directory",
        default="src/omnibase/nodes",
        help="Target directory (default: src/omnibase/nodes)",
    )
    manifest_parser.add_argument(
        "--apply", action="store_true", help="Apply changes (default: dry-run)"
    )
    manifest_parser.add_argument(
        "--no-backup", action="store_true", help="Disable backup creation"
    )

    # Fix node health operation
    health_parser = subparsers.add_parser(
        "fix-health", help="Fix comprehensive node health issues"
    )
    health_parser.add_argument(
        "--nodes", nargs="*", help="Specific node names to process (default: all nodes)"
    )
    health_parser.add_argument(
        "--target-directory",
        default="src/omnibase/nodes",
        help="Target directory (default: src/omnibase/nodes)",
    )
    health_parser.add_argument(
        "--apply", action="store_true", help="Apply changes (default: dry-run)"
    )
    health_parser.add_argument(
        "--no-backup", action="store_true", help="Disable backup creation"
    )

    # Synchronize configs operation
    sync_parser = subparsers.add_parser(
        "sync-configs", help="Synchronize configuration files"
    )
    sync_parser.add_argument(
        "--nodes", nargs="*", help="Specific node names to process (default: all nodes)"
    )
    sync_parser.add_argument(
        "--target-directory",
        default="src/omnibase/nodes",
        help="Target directory (default: src/omnibase/nodes)",
    )
    sync_parser.add_argument(
        "--apply", action="store_true", help="Apply changes (default: dry-run)"
    )
    sync_parser.add_argument(
        "--no-backup", action="store_true", help="Disable backup creation"
    )

    # Global options
    parser.add_argument(
        "--introspect", action="store_true", help="Show introspection data"
    )
    parser.add_argument(
        "--schema-version", default="1.0.0", help="Schema version (default: 1.0.0)"
    )
    parser.add_argument(
        "--correlation-id", type=str, help="Correlation ID for request tracking"
    )

    args = parser.parse_args()

    # Handle introspection command
    if args.introspect:
        NodeManagerIntrospection.handle_introspect_command()
        return

    # Validate operation was provided
    if not args.operation:
        parser.print_help()
        sys.exit(1)

    schema_version = args.schema_version

    # Create input state based on operation
    if args.operation == "generate":
        if not hasattr(args, "node_name") or not args.node_name:
            print("❌ Error: node_name is required for generate operation")
            sys.exit(1)

        input_state = NodeManagerInputState(
            version=schema_version,
            operation=NodeManagerOperation.GENERATE,
            node_name=args.node_name,
            template_source=args.template,
            target_directory=args.target_directory,
            author=args.author,
        )
    elif args.operation == "regenerate-contract":
        input_state = NodeManagerInputState(
            version=schema_version,
            operation=NodeManagerOperation.REGENERATE_CONTRACT,
            nodes=args.nodes,
            target_directory=args.target_directory,
            dry_run=not args.apply,
            backup_enabled=not args.no_backup,
        )
    elif args.operation == "regenerate-manifest":
        input_state = NodeManagerInputState(
            version=schema_version,
            operation=NodeManagerOperation.REGENERATE_MANIFEST,
            nodes=args.nodes,
            target_directory=args.target_directory,
            dry_run=not args.apply,
            backup_enabled=not args.no_backup,
        )
    elif args.operation == "fix-health":
        input_state = NodeManagerInputState(
            version=schema_version,
            operation=NodeManagerOperation.FIX_NODE_HEALTH,
            nodes=args.nodes,
            target_directory=args.target_directory,
            dry_run=not args.apply,
            backup_enabled=not args.no_backup,
        )
    elif args.operation == "sync-configs":
        input_state = NodeManagerInputState(
            version=schema_version,
            operation=NodeManagerOperation.SYNCHRONIZE_CONFIGS,
            nodes=args.nodes,
            target_directory=args.target_directory,
            dry_run=not args.apply,
            backup_enabled=not args.no_backup,
        )
    else:
        print(f"❌ Error: Unknown operation '{args.operation}'")
        sys.exit(1)

    try:
        # Run the node manager
        output = run_node_manager(input_state)

        # Display results
        print(f"✅ {output.message}")

        if output.node_directory:
            print(f"📁 Node directory: {output.node_directory}")

        if output.affected_files:
            print(f"📄 Affected {len(output.affected_files)} files")

        if output.processed_nodes:
            print(
                f"🔧 Processed {len(output.processed_nodes)} nodes: {', '.join(output.processed_nodes)}"
            )

        if output.warnings:
            print(f"⚠️  {len(output.warnings)} warnings:")
            for warning in output.warnings:
                print(f"   - {warning}")

        if output.next_steps:
            print("📋 Next steps:")
            for step in output.next_steps:
                print(f"   - {step}")

        # Set exit code based on status
        exit_code = get_exit_code_for_status(output.status)
        sys.exit(exit_code)

    except Exception as exc:
        emit_log_event(
            LogLevel.ERROR,
            f"Node management failed: {exc}",
            node_id=_COMPONENT_NAME,
            event_bus=event_bus,
        )
        print(f"❌ Error: {exc}")
        sys.exit(1)


def get_introspection() -> dict:
    """Get introspection data for the node manager node."""
    return NodeManagerIntrospection.get_introspection_response().model_dump()


if __name__ == "__main__":
    main()
