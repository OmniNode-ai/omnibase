# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:25.806934'
# description: Stamped by PythonHandler
# entrypoint: python://node.py
# hash: 90ddf7928ff074d3cdf3d8185ee758ffb1bb797b15692027188b41f3c90cf33e
# last_modified_at: '2025-05-29T11:50:11.146842+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: node.py
# namespace: omnibase.node
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 7d261022-2d50-4a53-919f-7be3ce843d04
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
CLI Node Implementation.

Main node implementation for the CLI node that handles command routing,
node discovery, and execution via event-driven architecture.
"""

import asyncio
import importlib
import json
import sys
import time
from pathlib import Path
from typing import Callable, Dict, Optional

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

from .introspection import CLINodeIntrospection
from .introspection_collector import IntrospectionCollector
from .models.state import (
    CLIInputState,
    CLIOutputState,
    NodeRegistrationState,
    create_cli_output_state,
)
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class CLINode(EventDrivenNodeMixin):
    """
    CLI Node for command routing and node management.

    Handles command execution, node discovery, and routing via event bus.
    """

    def __init__(self, node_id: str = "cli_node", event_bus: Optional[ProtocolEventBus] = None, **kwargs):
        super().__init__(node_id=node_id, event_bus=event_bus, **kwargs)
        self.registered_nodes: Dict[str, NodeRegistrationState] = {}
        # Subscribe to node registration events
        self.event_bus.subscribe(self._handle_node_registration)
        # Discover and register existing nodes
        self._discover_existing_nodes()

    def _handle_node_registration(self, event: OnexEvent) -> None:
        """Handle node registration events."""
        if event.event_type == OnexEventTypeEnum.NODE_REGISTER:
            try:
                if event.metadata is not None:
                    registration = NodeRegistrationState(**event.metadata)
                    self.registered_nodes[registration.node_name] = registration
                else:
                    emit_log_event(
                        LogLevelEnum.WARNING,
                        "Received NODE_REGISTER event with no metadata",
                        node_id=self.node_id,
                    )
                    return
                emit_log_event(
                    LogLevelEnum.INFO,
                    f"Registered node: {registration.node_name}@{registration.node_version}",
                    node_id=self.node_id,
                )
            except Exception as e:
                emit_log_event(
                    LogLevelEnum.ERROR,
                    f"Failed to register node from event: {e}",
                    node_id=self.node_id,
                )

    def _discover_existing_nodes(self) -> None:
        """Discover existing nodes in the system."""
        # Import the existing version resolver for compatibility
        try:
            from omnibase.cli_tools.onex.v1_0_0.cli_version_resolver import (
                global_resolver,
            )

            all_nodes = global_resolver.discover_all_nodes()
            for node_name, versions in all_nodes.items():
                if versions:
                    latest_version = versions[-1]  # Last version is latest
                    module_path = global_resolver.get_module_path(
                        node_name, latest_version
                    )
                    if module_path:
                        registration = NodeRegistrationState(
                            node_name=node_name,
                            node_version=latest_version,
                            module_path=module_path,
                            capabilities=["cli_execution"],
                            introspection_available=True,
                        )
                        self.registered_nodes[node_name] = registration

        except ImportError:
            emit_log_event(
                LogLevelEnum.WARNING,
                "Could not import existing node discovery - running in minimal mode",
                node_id=self.node_id,
            )

    async def execute(self, input_state: CLIInputState) -> CLIOutputState:
        start_time = time.time()
        self.emit_node_start({"input_state": input_state.model_dump()})
        try:
            if input_state.command == "run":
                result = self._handle_run_command(input_state)
            elif input_state.command == "list-nodes":
                result = await self._handle_list_nodes_command(input_state)
            elif input_state.command == "node-info":
                result = self._handle_node_info_command(input_state)
            elif input_state.command == "version":
                result = self._handle_version_command(input_state)
            elif input_state.command == "info":
                result = self._handle_info_command(input_state)
            elif input_state.command == "handlers":
                result = self._handle_handlers_command(input_state)
            else:
                result = create_cli_output_state(
                    status="error",
                    message=f"Unknown command: {input_state.command}",
                    command=input_state.command,
                    input_state=input_state,
                )

            # Add execution time
            execution_time = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time
            self.emit_node_success({
                "input_state": input_state.model_dump(),
                "output_state": result.model_dump(),
            })
            return result
        except Exception as exc:
            self.emit_node_failure({
                "input_state": input_state.model_dump(),
                "error": str(exc),
            })
            raise

    def _handle_run_command(self, input_state: CLIInputState) -> CLIOutputState:
        """Handle 'run' command to execute a target node."""
        if not input_state.target_node:
            return create_cli_output_state(
                status="error",
                message="target_node is required for 'run' command",
                command=input_state.command,
                input_state=input_state,
            )

        # Check if node is registered
        if input_state.target_node not in self.registered_nodes:
            return create_cli_output_state(
                status="error",
                message=f"Node '{input_state.target_node}' not found. Use 'list-nodes' to see available nodes.",
                command=input_state.command,
                input_state=input_state,
                target_node=input_state.target_node,
            )

        registration = self.registered_nodes[input_state.target_node]

        # Handle introspection request
        if input_state.introspect:
            try:
                module = importlib.import_module(registration.module_path)
                if hasattr(module, "get_introspection"):
                    introspection_data = module.get_introspection()
                    return create_cli_output_state(
                        status="success",
                        message=f"Introspection data for {input_state.target_node}",
                        command=input_state.command,
                        input_state=input_state,
                        target_node=input_state.target_node,
                        result_data=introspection_data,
                    )
                else:
                    return create_cli_output_state(
                        status="error",
                        message=f"Node {input_state.target_node} does not support introspection",
                        command=input_state.command,
                        input_state=input_state,
                        target_node=input_state.target_node,
                    )
            except Exception as e:
                return create_cli_output_state(
                    status="error",
                    message=f"Failed to get introspection for {input_state.target_node}: {e}",
                    command=input_state.command,
                    input_state=input_state,
                    target_node=input_state.target_node,
                )

        # Execute the target node
        try:
            module = importlib.import_module(registration.module_path)

            if hasattr(module, "main"):
                # Prepare arguments for the node
                node_argv = [
                    f"{input_state.target_node}@{registration.node_version}"
                ] + input_state.args

                # Temporarily replace sys.argv for the node
                original_argv = sys.argv
                try:
                    sys.argv = node_argv
                    result = module.main()

                    # Handle different return types
                    if result is None:
                        status = "success"
                        message = (
                            f"Node {input_state.target_node} executed successfully"
                        )
                    elif isinstance(result, int):
                        status = "success" if result == 0 else "error"
                        message = (
                            f"Node {input_state.target_node} exited with code {result}"
                        )
                    else:
                        # Assume it's a Pydantic model or other object
                        if hasattr(result, "status"):
                            status = (
                                "success"
                                if result.status == OnexStatus.SUCCESS
                                else "error"
                            )
                            message = f"Node {input_state.target_node} completed with status: {result.status}"
                        else:
                            status = "success"
                            message = (
                                f"Node {input_state.target_node} executed successfully"
                            )

                    return create_cli_output_state(
                        status=status,
                        message=message,
                        command=input_state.command,
                        input_state=input_state,
                        target_node=input_state.target_node,
                        result_data=(
                            {"return_value": str(result)}
                            if result is not None
                            else None
                        ),
                    )

                finally:
                    sys.argv = original_argv
            else:
                return create_cli_output_state(
                    status="error",
                    message=f"Node {input_state.target_node} does not have a main() function",
                    command=input_state.command,
                    input_state=input_state,
                    target_node=input_state.target_node,
                )

        except ImportError as e:
            return create_cli_output_state(
                status="error",
                message=f"Failed to import node {input_state.target_node}: {e}",
                command=input_state.command,
                input_state=input_state,
                target_node=input_state.target_node,
            )
        except Exception as e:
            return create_cli_output_state(
                status="error",
                message=f"Error running node {input_state.target_node}: {e}",
                command=input_state.command,
                input_state=input_state,
                target_node=input_state.target_node,
            )

    async def _handle_list_nodes_command(
        self, input_state: CLIInputState
    ) -> CLIOutputState:
        """Handle 'list-nodes' command using event-driven discovery."""
        try:
            # Use event-driven node discovery
            collector = IntrospectionCollector(
                event_bus=self.event_bus,
                timeout_ms=2000,  # 2 second timeout for discovery
                node_id=self.node_id,
            )

            discovery_result = await collector.discover_nodes()

            # Format nodes data from event responses
            nodes_data = {}
            for node_id, node_data in discovery_result["nodes"].items():
                node_info = node_data.get("node_info", {})
                nodes_data[node_id] = {
                    "version": node_info.get("node_version", "unknown"),
                    "capabilities": node_info.get("capabilities", []),
                    "introspection_available": node_info.get(
                        "introspection_available", False
                    ),
                    "status": node_info.get("status", "unknown"),
                    "discovery_time_ms": (
                        round(
                            (
                                node_data.get("discovered_at", 0)
                                - discovery_result.get("total_time_ms", 0)
                            )
                            * 1000,
                            2,
                        )
                        if "discovered_at" in node_data
                        else 0
                    ),
                    "event_driven": True,
                }

            # Fallback to registered nodes if no event responses
            if not nodes_data:
                for node_name, registration in self.registered_nodes.items():
                    nodes_data[node_name] = {
                        "version": registration.node_version,
                        "module_path": registration.module_path,
                        "capabilities": registration.capabilities,
                        "introspection_available": registration.introspection_available,
                        "status": "registered",
                        "event_driven": False,
                    }

            message = f"Found {len(nodes_data)} nodes via event-driven discovery"
            return create_cli_output_state(
                status="success",
                message=message,
                command=input_state.command,
                input_state=input_state,
                result_data={
                    "nodes": nodes_data,
                    "discovery_metadata": {
                        "correlation_id": discovery_result.get("correlation_id"),
                        "total_time_ms": discovery_result.get("total_time_ms"),
                        "timeout_ms": discovery_result.get("timeout_ms"),
                        "event_driven": True,
                    },
                },
            )
        except Exception as e:
            # Fallback to traditional method
            nodes_data = {}
            for node_name, registration in self.registered_nodes.items():
                nodes_data[node_name] = {
                    "version": registration.node_version,
                    "module_path": registration.module_path,
                    "capabilities": registration.capabilities,
                    "introspection_available": registration.introspection_available,
                    "status": "registered",
                    "event_driven": False,
                }

            message = f"Found {len(self.registered_nodes)} registered nodes (fallback mode: {str(e)})"
            return create_cli_output_state(
                status="success",
                message=message,
                command=input_state.command,
                input_state=input_state,
                result_data={"nodes": nodes_data},
            )

    def _handle_node_info_command(self, input_state: CLIInputState) -> CLIOutputState:
        """Handle 'node-info' command."""
        if not input_state.target_node:
            return create_cli_output_state(
                status="error",
                message="target_node is required for 'node-info' command",
                command=input_state.command,
                input_state=input_state,
            )

        if input_state.target_node not in self.registered_nodes:
            return create_cli_output_state(
                status="error",
                message=f"Node '{input_state.target_node}' not found",
                command=input_state.command,
                input_state=input_state,
                target_node=input_state.target_node,
            )

        registration = self.registered_nodes[input_state.target_node]
        node_info = {
            "name": registration.node_name,
            "version": registration.node_version,
            "module_path": registration.module_path,
            "capabilities": registration.capabilities,
            "introspection_available": registration.introspection_available,
            "metadata": registration.metadata,
        }

        return create_cli_output_state(
            status="success",
            message=f"Information for node {input_state.target_node}",
            command=input_state.command,
            input_state=input_state,
            target_node=input_state.target_node,
            result_data={"node_info": node_info},
        )

    def _handle_version_command(self, input_state: CLIInputState) -> CLIOutputState:
        """Handle 'version' command."""
        # Get version from metadata file
        version = CLINodeIntrospection.get_node_version()
        node_name = CLINodeIntrospection.get_node_name()

        return create_cli_output_state(
            status="success",
            message=f"ONEX CLI Node v{version}",
            command=input_state.command,
            input_state=input_state,
            result_data={"version": version, "type": node_name},
        )

    def _handle_info_command(self, input_state: CLIInputState) -> CLIOutputState:
        """Handle 'info' command."""
        info_data = {
            "python_version": sys.version,
            "platform": sys.platform,
            "registered_nodes": len(self.registered_nodes),
            "event_bus_type": type(self.event_bus).__name__,
        }

        return create_cli_output_state(
            status="success",
            message="ONEX CLI Node System Information",
            command=input_state.command,
            input_state=input_state,
            result_data={"system_info": info_data},
        )

    def _handle_handlers_command(self, input_state: CLIInputState) -> CLIOutputState:
        """Handle 'handlers' command."""
        # Get file type handlers information
        registry = FileTypeHandlerRegistry()
        registry.register_all_handlers()

        handlers_info = {}
        for ext, handler in registry._handlers.items():
            handlers_info[ext] = {
                "handler_type": type(handler).__name__,
                "module": type(handler).__module__,
            }

        return create_cli_output_state(
            status="success",
            message=f"Found {len(handlers_info)} file type handlers",
            command=input_state.command,
            input_state=input_state,
            result_data={"handlers": handlers_info},
        )


def run_cli_node(
    input_state: CLIInputState,
    event_bus: Optional[ProtocolEventBus] = None,
    output_state_cls: Optional[Callable[..., CLIOutputState]] = None,
    handler_registry: Optional[FileTypeHandlerRegistry] = None,
) -> CLIOutputState:
    """
    Main node entrypoint for CLI node.

    Args:
        input_state: CLIInputState (must include version)
        event_bus: ProtocolEventBus (optional, defaults to InMemoryEventBus)
        output_state_cls: Optional callable to construct output state (for testing/mocking)
        handler_registry: Optional FileTypeHandlerRegistry (not used by CLI node)

    Returns:
        CLIOutputState (version matches input_state.version)
    """
    if event_bus is None:
        event_bus = InMemoryEventBus()

    cli_node = CLINode(node_id="cli_node", event_bus=event_bus)

    # Run the async execute method in an event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an event loop, create a new task
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, cli_node.execute(input_state))
                return future.result()
        else:
            return loop.run_until_complete(cli_node.execute(input_state))
    except RuntimeError:
        # No event loop exists, create one
        return asyncio.run(cli_node.execute(input_state))


def main() -> None:
    """
    CLI entrypoint for standalone execution.
    """
    import argparse

    parser = argparse.ArgumentParser(description="ONEX CLI Node")
    parser.add_argument(
        "command",
        type=str,
        nargs="?",
        choices=["run", "list-nodes", "node-info", "version", "info", "handlers"],
        help="Command to execute",
    )
    parser.add_argument(
        "target_node",
        type=str,
        nargs="?",
        help="Target node name (for 'run' and 'node-info' commands)",
    )
    parser.add_argument(
        "--version",
        type=str,
        help="Specific version of target node to run",
    )
    parser.add_argument(
        "--introspect",
        action="store_true",
        help="Display node contract and capabilities",
    )
    parser.add_argument(
        "--list-versions",
        action="store_true",
        help="List available versions for the specified node",
    )
    parser.add_argument(
        "--args",
        type=str,
        help="Additional arguments to pass to the node (as JSON string)",
    )

    args = parser.parse_args()

    # Handle introspection command for CLI node itself
    if args.introspect and not args.command:
        CLINodeIntrospection.handle_introspect_command()
        return

    # Validate required arguments
    if not args.command:
        parser.error("command is required when not using --introspect")

    # Parse node arguments
    node_args = []
    if args.args:
        try:
            node_args = json.loads(args.args)
            if not isinstance(node_args, list):
                parser.error("Node arguments must be a JSON array")
        except json.JSONDecodeError as e:
            parser.error(f"Invalid JSON in node arguments: {e}")

    # Get schema version
    schema_version = OnexVersionLoader().get_onex_versions().schema_version

    # Create input state
    from .models.state import create_cli_input_state

    input_state = create_cli_input_state(
        command=args.command,
        target_node=args.target_node,
        node_version=args.version,
        args=node_args,
        introspect=args.introspect,
        list_versions=args.list_versions,
        version=schema_version,
    )

    # Execute CLI node
    output_state = run_cli_node(input_state)

    # Output result
    if output_state.result_data:
        print(json.dumps(output_state.result_data, indent=2))
    else:
        print(output_state.message)

    # Exit with appropriate code
    exit_code = 0 if output_state.status == "success" else 1
    sys.exit(exit_code)


def get_introspection() -> dict:
    """Get introspection data for the CLI node."""
    return CLINodeIntrospection.get_introspection_response().model_dump()


if __name__ == "__main__":
    main()
