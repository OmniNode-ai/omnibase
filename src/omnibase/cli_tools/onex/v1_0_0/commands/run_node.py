import argparse
import importlib
import sys
from pathlib import Path
from typing import Any, Callable, Dict

from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum
from omnibase.metadata.metadata_constants import get_namespace_prefix
from omnibase.model.model_log_entry import LogContextModel
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)

from ..cli_version_resolver import global_resolver

_COMPONENT_NAME = Path(__file__).stem


def add_run_node_command(subparsers: Any) -> None:
    """Add the run-node command to the CLI parser."""
    parser = subparsers.add_parser(
        "run", help="Run an ONEX node with automatic version resolution"
    )
    parser.add_argument(
        "node_name",
        help="Name of the node to run (e.g., node_parity_validator, stamper_node)",
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
    parser.add_argument(
        "node_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments to pass to the node",
    )
    parser.set_defaults(func=run_node_command)


def run_node_command(args: Any) -> int:
    """Execute the run-node command."""
    node_name = args.node_name
    requested_version = args.version
    resolved_version = global_resolver.resolve_version(node_name, requested_version)
    if not resolved_version:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"Node '{node_name}' not found or version unavailable.",
            context=LogContextModel(
                calling_module=__name__,
                calling_function="run_node_command",
                calling_line=__import__("inspect").currentframe().f_lineno,
                timestamp="auto",
                node_id=_COMPONENT_NAME,
            ),
            node_id=_COMPONENT_NAME,
        )
        return 1
    module_path = global_resolver.get_module_path(node_name, resolved_version)
    if not module_path:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"Module path for node '{node_name}'@{resolved_version} not found.",
            context=LogContextModel(
                calling_module=__name__,
                calling_function="run_node_command",
                calling_line=__import__("inspect").currentframe().f_lineno,
                timestamp="auto",
                node_id=_COMPONENT_NAME,
            ),
            node_id=_COMPONENT_NAME,
        )
        return 1
    try:
        module = importlib.import_module(module_path)
        if args.introspect:
            if hasattr(module, "get_introspection"):
                introspection = module.get_introspection()
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    "Node introspection data",
                    context=LogContextModel(
                        calling_module=__name__,
                        calling_function="run_node_command",
                        calling_line=__import__("inspect").currentframe().f_lineno,
                        timestamp="auto",
                        node_id=_COMPONENT_NAME,
                    ),
                    node_id=_COMPONENT_NAME,
                )
                print(introspection)
                return 0
            else:
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    f"Node {node_name} does not support introspection",
                    context=LogContextModel(
                        calling_module=__name__,
                        calling_function="run_node_command",
                        calling_line=__import__("inspect").currentframe().f_lineno,
                        timestamp="auto",
                        node_id=_COMPONENT_NAME,
                    ),
                    node_id=_COMPONENT_NAME,
                )
                return 1
        if hasattr(module, "main"):
            node_argv = [f"{node_name}@{resolved_version}"] + (args.node_args or [])
            original_argv = sys.argv
            try:
                sys.argv = node_argv
                result = module.main()
                return int(result) if result is not None else 0
            finally:
                sys.argv = original_argv
        else:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Node {node_name} does not have a main() function",
                context=LogContextModel(
                    calling_module=__name__,
                    calling_function="run_node_command",
                    calling_line=__import__("inspect").currentframe().f_lineno,
                    timestamp="auto",
                    node_id=_COMPONENT_NAME,
                ),
                node_id=_COMPONENT_NAME,
            )
            return 1
    except ImportError as e:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"Failed to import node {node_name}: {e}",
            context=LogContextModel(
                calling_module=__name__,
                calling_function="run_node_command",
                calling_line=__import__("inspect").currentframe().f_lineno,
                timestamp="auto",
                node_id=_COMPONENT_NAME,
            ),
            node_id=_COMPONENT_NAME,
        )
        return 1
    except Exception as e:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"Error running node {node_name}: {e}",
            context=LogContextModel(
                calling_module=__name__,
                calling_function="run_node_command",
                calling_line=__import__("inspect").currentframe().f_lineno,
                timestamp="auto",
                node_id=_COMPONENT_NAME,
            ),
            node_id=_COMPONENT_NAME,
        )
        return 1


def list_node_versions(node_name: str) -> int:
    """List available versions for a node."""
    versions = global_resolver.discover_node_versions(node_name)
    if not versions:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"No versions found for node '{node_name}'",
            context=LogContextModel(
                calling_module=__name__,
                calling_function="list_node_versions",
                calling_line=__import__("inspect").currentframe().f_lineno,
                timestamp="auto",
                node_id=_COMPONENT_NAME,
            ),
            node_id=_COMPONENT_NAME,
        )
        return 1
    latest = global_resolver.get_latest_version(node_name)
    emit_log_event_sync(
        LogLevelEnum.INFO,
        f"Available versions for {node_name}",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="list_node_versions",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
    )
    return 0


def list_all_nodes() -> int:
    """List all available nodes and their versions."""
    all_nodes = global_resolver.discover_all_nodes()
    if not all_nodes:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            "No ONEX nodes found",
            context=LogContextModel(
                calling_module=__name__,
                calling_function="list_all_nodes",
                calling_line=__import__("inspect").currentframe().f_lineno,
                timestamp="auto",
                node_id=_COMPONENT_NAME,
            ),
            node_id=_COMPONENT_NAME,
        )
        return 1
    node_info = []
    for node_name, versions in all_nodes.items():
        latest = versions[-1] if versions else "none"
        version_count = len(versions)
        node_info.append(
            {
                "name": node_name,
                "version_count": version_count,
                "latest_version": latest,
                "versions": versions,
            }
        )
    emit_log_event_sync(
        LogLevelEnum.INFO,
        "Available ONEX nodes",
        context=LogContextModel(
            calling_module=__name__,
            calling_function="list_all_nodes",
            calling_line=__import__("inspect").currentframe().f_lineno,
            timestamp="auto",
            node_id=_COMPONENT_NAME,
        ),
        node_id=_COMPONENT_NAME,
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
        "--version", help="Specific version to run (defaults to latest)"
    )
    parser.add_argument(
        "--introspect", action="store_true", help="Show node introspection information"
    )
    parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="Arguments to pass to the node"
    )
    args = parser.parse_args()
    node_name = args.node
    requested_version = args.version
    resolved_version = global_resolver.resolve_version(node_name, requested_version)
    if not resolved_version:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"Node '{node_name}' not found or version unavailable.",
            context=LogContextModel(
                calling_module=__name__,
                calling_function="main",
                calling_line=__import__("inspect").currentframe().f_lineno,
                timestamp="auto",
                node_id=_COMPONENT_NAME,
            ),
            node_id=_COMPONENT_NAME,
        )
        exit(1)
    module_path = global_resolver.get_module_path(node_name, resolved_version)
    if not module_path:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"Module path for node '{node_name}'@{resolved_version} not found.",
            context=LogContextModel(
                calling_module=__name__,
                calling_function="main",
                calling_line=__import__("inspect").currentframe().f_lineno,
                timestamp="auto",
                node_id=_COMPONENT_NAME,
            ),
            node_id=_COMPONENT_NAME,
        )
        exit(1)
    try:
        module = importlib.import_module(module_path)
        if args.introspect:
            if hasattr(module, "get_introspection"):
                introspection = module.get_introspection()
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    "Node introspection data",
                    context=LogContextModel(
                        calling_module=__name__,
                        calling_function="main",
                        calling_line=__import__("inspect").currentframe().f_lineno,
                        timestamp="auto",
                        node_id=_COMPONENT_NAME,
                    ),
                    node_id=_COMPONENT_NAME,
                )
                print(introspection)
                exit(0)
            else:
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    f"Node {node_name} does not support introspection",
                    context=LogContextModel(
                        calling_module=__name__,
                        calling_function="main",
                        calling_line=__import__("inspect").currentframe().f_lineno,
                        timestamp="auto",
                        node_id=_COMPONENT_NAME,
                    ),
                    node_id=_COMPONENT_NAME,
                )
                exit(1)
        if hasattr(module, "main"):
            node_argv = [f"{node_name}@{resolved_version}"] + (args.args or [])
            original_argv = sys.argv
            try:
                sys.argv = node_argv
                result = module.main()
                exit(int(result) if result is not None else 0)
            finally:
                sys.argv = original_argv
        else:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Node {node_name} does not have a main() function",
                context=LogContextModel(
                    calling_module=__name__,
                    calling_function="main",
                    calling_line=__import__("inspect").currentframe().f_lineno,
                    timestamp="auto",
                    node_id=_COMPONENT_NAME,
                ),
                node_id=_COMPONENT_NAME,
            )
            exit(1)
    except ImportError as e:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"Failed to import node {node_name}: {e}",
            context=LogContextModel(
                calling_module=__name__,
                calling_function="main",
                calling_line=__import__("inspect").currentframe().f_lineno,
                timestamp="auto",
                node_id=_COMPONENT_NAME,
            ),
            node_id=_COMPONENT_NAME,
        )
        exit(1)
    except Exception as e:
        emit_log_event_sync(
            LogLevelEnum.ERROR,
            f"Error running node {node_name}: {e}",
            context=LogContextModel(
                calling_module=__name__,
                calling_function="main",
                calling_line=__import__("inspect").currentframe().f_lineno,
                timestamp="auto",
                node_id=_COMPONENT_NAME,
            ),
            node_id=_COMPONENT_NAME,
        )
        exit(1)


if __name__ == "__main__":
    main()
