import argparse
import importlib
import sys
from pathlib import Path
from typing import Any, Callable, Dict
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.metadata.metadata_constants import get_namespace_prefix
from ..cli_version_resolver import global_resolver
NODE_REGISTRY: Dict[str, tuple[str, str, Any]] = {'stamper_node': (
    f'{get_namespace_prefix()}.nodes.stamper_node.node', 'run_stamper_node',
    f'{get_namespace_prefix()}.nodes.stamper_node.helpers.stamper_node_cli_adapter.StamperNodeCliAdapter'
    )}
_COMPONENT_NAME = Path(__file__).stem


def add_run_node_command(subparsers: Any) ->None:
    """Add the run-node command to the CLI parser."""
    parser = subparsers.add_parser('run', help=
        'Run an ONEX node with automatic version resolution')
    parser.add_argument('node_name', help=
        'Name of the node to run (e.g., parity_validator_node, stamper_node)')
    parser.add_argument('--version', help=
        'Specific version to run (defaults to latest)')
    parser.add_argument('--list-versions', action='store_true', help=
        'List available versions for the specified node')
    parser.add_argument('--introspect', action='store_true', help=
        'Show node introspection information')
    parser.add_argument('node_args', nargs=argparse.REMAINDER, help=
        'Additional arguments to pass to the node')
    parser.set_defaults(func=run_node_command)


def run_node_command(args: Any) ->int:
    """Execute the run-node command."""
    node_name = args.node_name
    if args.list_versions:
        return list_node_versions(node_name)
    resolved_version = global_resolver.resolve_version(node_name, args.version)
    if not resolved_version:
        if args.version:
            emit_log_event(LogLevelEnum.ERROR,
                f"Version '{args.version}' not found for node '{node_name}'",
                context={'node_name': node_name, 'requested_version': args.
                version}, node_id=_COMPONENT_NAME)
        else:
            emit_log_event(LogLevelEnum.ERROR,
                f"No versions found for node '{node_name}'", context={
                'node_name': node_name}, node_id=_COMPONENT_NAME)
        return 1
    module_path = global_resolver.get_module_path(node_name, resolved_version)
    if not module_path:
        emit_log_event(LogLevelEnum.ERROR,
            f'Could not resolve module path for {node_name}@{resolved_version}'
            , context={'node_name': node_name, 'version': resolved_version},
            node_id=_COMPONENT_NAME)
        return 1
    emit_log_event(LogLevelEnum.INFO,
        f'Running {node_name}@{resolved_version}', context={'node_name':
        node_name, 'version': resolved_version}, node_id=_COMPONENT_NAME)
    try:
        module = importlib.import_module(module_path)
        if args.introspect:
            if hasattr(module, 'get_introspection'):
                introspection = module.get_introspection()
                emit_log_event(LogLevelEnum.INFO, 'Node introspection data',
                    context={'node_name': node_name, 'introspection':
                    introspection}, node_id=_COMPONENT_NAME)
                return 0
            else:
                emit_log_event(LogLevelEnum.ERROR,
                    f'Node {node_name} does not support introspection',
                    context={'node_name': node_name}, node_id=
                    _COMPONENT_NAME)
                return 1
        if hasattr(module, 'main'):
            node_argv = [f'{node_name}@{resolved_version}'] + (args.
                node_args or [])
            original_argv = sys.argv
            try:
                sys.argv = node_argv
                result = module.main()
                return int(result) if result is not None else 0
            finally:
                sys.argv = original_argv
        else:
            emit_log_event(LogLevelEnum.ERROR,
                f'Node {node_name} does not have a main() function',
                context={'node_name': node_name}, node_id=_COMPONENT_NAME)
            return 1
    except ImportError as e:
        emit_log_event(LogLevelEnum.ERROR,
            f'Failed to import node {node_name}: {e}', context={'node_name':
            node_name, 'error': str(e)}, node_id=_COMPONENT_NAME)
        return 1
    except Exception as e:
        emit_log_event(LogLevelEnum.ERROR,
            f'Error running node {node_name}: {e}', context={'node_name':
            node_name, 'error': str(e)}, node_id=_COMPONENT_NAME)
        return 1


def list_node_versions(node_name: str) ->int:
    """List available versions for a node."""
    versions = global_resolver.discover_node_versions(node_name)
    if not versions:
        emit_log_event(LogLevelEnum.ERROR,
            f"No versions found for node '{node_name}'", context={
            'node_name': node_name}, node_id=_COMPONENT_NAME)
        return 1
    latest = global_resolver.get_latest_version(node_name)
    emit_log_event(LogLevelEnum.INFO, f'Available versions for {node_name}',
        context={'node_name': node_name, 'versions': versions,
        'latest_version': latest}, node_id=_COMPONENT_NAME)
    return 0


def list_all_nodes() ->int:
    """List all available nodes and their versions."""
    all_nodes = global_resolver.discover_all_nodes()
    if not all_nodes:
        emit_log_event(LogLevelEnum.ERROR, 'No ONEX nodes found', node_id=
            _COMPONENT_NAME)
        return 1
    node_info = []
    for node_name, versions in all_nodes.items():
        latest = versions[-1] if versions else 'none'
        version_count = len(versions)
        node_info.append({'name': node_name, 'version_count': version_count,
            'latest_version': latest, 'versions': versions})
    emit_log_event(LogLevelEnum.INFO, 'Available ONEX nodes', context={
        'nodes': node_info, 'total_nodes': len(all_nodes)}, node_id=
        _COMPONENT_NAME)
    return 0


def add_list_nodes_command(subparsers: Any) ->None:
    """Add the list-nodes command to the CLI parser."""
    parser = subparsers.add_parser('list-nodes', help=
        'List all available ONEX nodes')
    parser.set_defaults(func=lambda args: list_all_nodes())


def main() ->None:
    """
    Canonical CLI entrypoint for `onex run <node>`.
    Dynamically loads and runs the requested node using its CLI adapter.
    """
    parser = argparse.ArgumentParser(description=
        'Run an ONEX node and emit events.')
    parser.add_argument('node', type=str, help='Node name to execute')
    parser.add_argument('--args', nargs=argparse.REMAINDER, help=
        'Arguments to pass to the node')
    args = parser.parse_args()
    node_name = args.node
    node_info = NODE_REGISTRY.get(node_name)
    if not node_info:
        emit_log_event(LogLevelEnum.ERROR, f'Unknown node: {node_name}',
            context={'node_name': node_name, 'available_nodes': list(
            NODE_REGISTRY.keys())}, node_id=_COMPONENT_NAME)
        exit(1)
    module_name, func_name, adapter_path = node_info
    try:
        module = importlib.import_module(module_name)
        node_func: Callable = getattr(module, func_name)
        adapter_module_path, adapter_class_name = adapter_path.rsplit('.', 1)
        adapter_module = importlib.import_module(adapter_module_path)
        adapter_class = getattr(adapter_module, adapter_class_name)
        cli_adapter = adapter_class()
    except Exception as e:
        emit_log_event(LogLevelEnum.ERROR,
            f'Failed to import node or adapter {node_name}: {e}', context={
            'node_name': node_name, 'error': str(e)}, node_id=
            _COMPONENT_NAME)
        exit(1)
    node_args = args.args or []
    try:
        input_state = cli_adapter.parse_cli_args(node_args)
    except Exception as e:
        emit_log_event(LogLevelEnum.ERROR,
            f'Failed to parse CLI args for {node_name}: {e}', context={
            'node_name': node_name, 'error': str(e)}, node_id=
            _COMPONENT_NAME)
        exit(1)
    event_bus = InMemoryEventBus()
    try:
        result = node_func(input_state, event_bus=event_bus)
    except TypeError as e:
        raise RuntimeError(
            f"Node function {node_func.__name__} must accept event_bus as a parameter for protocol-pure logging. Error: {e}"
        )
    try:
        from pydantic import BaseModel
        if isinstance(result, BaseModel):
            if hasattr(result, 'model_dump_json'):
                emit_log_event(LogLevelEnum.INFO, result.model_dump_json(
                    indent=2), node_id=_COMPONENT_NAME, event_bus=event_bus)
            else:
                emit_log_event(LogLevelEnum.INFO, result.json(indent=2),
                    node_id=_COMPONENT_NAME, event_bus=event_bus)
        else:
            emit_log_event(LogLevelEnum.INFO, str(result), node_id=
                _COMPONENT_NAME, event_bus=event_bus)
    except ImportError:
        emit_log_event(LogLevelEnum.INFO, str(result), node_id=
            _COMPONENT_NAME, event_bus=event_bus)


if __name__ == '__main__':
    main()
