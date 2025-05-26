# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: run_node.py
# version: 1.0.0
# uuid: bf1b62fa-a11a-4c39-a582-bbd77d63190d
# author: OmniNode Team
# created_at: 2025-05-22T14:05:21.442415
# last_modified_at: 2025-05-22T20:21:24.989970
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 05994e6c182b403283b2a09e6b12d13131c92664e62296e110273e9bb0a60903
# entrypoint: python@run_node.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.run_node
# meta_type: tool
# === /OmniNode:Metadata ===


import argparse
import importlib
import logging
import sys
from typing import Any, Callable, Dict

from omnibase.core.version_resolver import global_resolver
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)

# Node registry: maps node name to (module, function, cli_adapter)
NODE_REGISTRY: Dict[str, tuple[str, str, Any]] = {
    "stamper_node": (
        "omnibase.nodes.stamper_node.node",
        "run_stamper_node",
        "omnibase.nodes.stamper_node.helpers.stamper_node_cli_adapter.StamperNodeCliAdapter",
    ),
    # Add more nodes here as needed
}

logger = logging.getLogger("onex.run_node")


def add_run_node_command(subparsers: Any) -> None:
    """Add the run-node command to the CLI parser."""
    parser = subparsers.add_parser(
        "run", help="Run an ONEX node with automatic version resolution"
    )

    parser.add_argument(
        "node_name",
        help="Name of the node to run (e.g., parity_validator_node, stamper_node)",
    )

    parser.add_argument(
        "--version", help="Specific version to run (defaults to latest)"
    )

    parser.add_argument(
        "--list-versions",
        action="store_true",
        help="List available versions for the specified node",
    )

    parser.add_argument(
        "--introspect", action="store_true", help="Show node introspection information"
    )

    # Allow passing through additional arguments to the node
    parser.add_argument(
        "node_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments to pass to the node",
    )

    parser.set_defaults(func=run_node_command)


def run_node_command(args: Any) -> int:
    """Execute the run-node command."""
    node_name = args.node_name

    # Handle list-versions request
    if args.list_versions:
        return list_node_versions(node_name)

    # Resolve version
    resolved_version = global_resolver.resolve_version(node_name, args.version)
    if not resolved_version:
        if args.version:
            print(f"❌ Version '{args.version}' not found for node '{node_name}'")
        else:
            print(f"❌ No versions found for node '{node_name}'")
        return 1

    # Get module path
    module_path = global_resolver.get_module_path(node_name, resolved_version)
    if not module_path:
        print(f"❌ Could not resolve module path for {node_name}@{resolved_version}")
        return 1

    print(f"🚀 Running {node_name}@{resolved_version}")

    try:
        # Import and run the node
        module = importlib.import_module(module_path)

        # Handle introspection request
        if args.introspect:
            if hasattr(module, "get_introspection"):
                introspection = module.get_introspection()
                import json

                print(json.dumps(introspection, indent=2))
                return 0
            else:
                print(f"❌ Node {node_name} does not support introspection")
                return 1

        # Run the node's main function with remaining arguments
        if hasattr(module, "main"):
            # Prepare arguments for the node
            node_argv = [f"{node_name}@{resolved_version}"] + (args.node_args or [])

            # Temporarily replace sys.argv for the node
            original_argv = sys.argv
            try:
                sys.argv = node_argv
                result = module.main()
                # Ensure we return an int
                return int(result) if result is not None else 0
            finally:
                sys.argv = original_argv
        else:
            print(f"❌ Node {node_name} does not have a main() function")
            return 1

    except ImportError as e:
        print(f"❌ Failed to import node {node_name}: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error running node {node_name}: {e}")
        return 1


def list_node_versions(node_name: str) -> int:
    """List available versions for a node."""
    versions = global_resolver.discover_node_versions(node_name)

    if not versions:
        print(f"❌ No versions found for node '{node_name}'")
        return 1

    latest = global_resolver.get_latest_version(node_name)

    print(f"📦 Available versions for {node_name}:")
    for version in versions:
        marker = " (latest)" if version == latest else ""
        print(f"  • {version}{marker}")

    return 0


def list_all_nodes() -> int:
    """List all available nodes and their versions."""
    all_nodes = global_resolver.discover_all_nodes()

    if not all_nodes:
        print("❌ No ONEX nodes found")
        return 1

    print("📦 Available ONEX nodes:")
    for node_name, versions in all_nodes.items():
        latest = versions[-1] if versions else "none"
        version_count = len(versions)
        print(
            f"  • {node_name} ({version_count} version{'s' if version_count != 1 else ''}, latest: {latest})"
        )

    return 0


def add_list_nodes_command(subparsers: Any) -> None:
    """Add the list-nodes command to the CLI parser."""
    parser = subparsers.add_parser("list-nodes", help="List all available ONEX nodes")

    parser.set_defaults(func=lambda args: list_all_nodes())


def main() -> None:
    """
    Canonical CLI entrypoint for `onex run <node>`.
    Dynamically loads and runs the requested node using its CLI adapter.
    """
    parser = argparse.ArgumentParser(description="Run an ONEX node and emit events.")
    parser.add_argument("node", type=str, help="Node name to execute")
    parser.add_argument(
        "--args", nargs=argparse.REMAINDER, help="Arguments to pass to the node"
    )
    args = parser.parse_args()

    node_name = args.node
    node_info = NODE_REGISTRY.get(node_name)
    if not node_info:
        logger.error(f"Unknown node: {node_name}")
        print(
            f"Error: Unknown node '{node_name}'. Available: {list(NODE_REGISTRY.keys())}"
        )
        exit(1)
    module_name, func_name, adapter_path = node_info
    try:
        module = importlib.import_module(module_name)
        node_func: Callable = getattr(module, func_name)
        # Dynamically import the adapter class
        adapter_module_path, adapter_class_name = adapter_path.rsplit(".", 1)
        adapter_module = importlib.import_module(adapter_module_path)
        adapter_class = getattr(adapter_module, adapter_class_name)
        cli_adapter = adapter_class()
    except Exception as e:
        logger.error(f"Failed to import node or adapter {node_name}: {e}")
        print(f"Error: Failed to import node or adapter '{node_name}': {e}")
        exit(1)

    node_args = args.args or []
    # Use the adapter to build the input state
    try:
        input_state = cli_adapter.parse_cli_args(node_args)
    except Exception as e:
        logger.error(f"Failed to parse CLI args for {node_name}: {e}")
        print(f"Error: Failed to parse CLI args for '{node_name}': {e}")
        exit(1)
    event_bus = InMemoryEventBus()
    try:
        result = node_func(input_state, event_bus=event_bus)
    except TypeError:
        result = node_func(input_state)
    # Print result as JSON if possible
    try:
        from pydantic import BaseModel

        if isinstance(result, BaseModel):
            # Pydantic v2: use model_dump_json; v1: use json()
            if hasattr(result, "model_dump_json"):
                print(result.model_dump_json(indent=2))
            else:
                print(result.json(indent=2))
        else:
            print(str(result))
    except ImportError:
        print(str(result))
    # TODO: Print or log emitted events if needed


if __name__ == "__main__":
    main()
