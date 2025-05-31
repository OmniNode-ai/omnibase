"""
Event-Driven ONEX CLI Tool.

This CLI tool directly uses the CLI node with event bus subscription for
real-time feedback and observability. Replaces the legacy CLI implementation
with a cleaner, event-driven architecture.
"""
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TaskID, TextColumn
from rich.table import Table
from omnibase.core.core_structured_logging import emit_log_event, setup_structured_logging
from omnibase.enums import LogLevelEnum
from omnibase.model.model_onex_event import OnexEvent
from omnibase.nodes.cli_node.v1_0_0.models.state import CLI_STATE_SCHEMA_VERSION, create_cli_input_state
from omnibase.nodes.cli_node.v1_0_0.node import CLINode
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.metadata.metadata_constants import get_namespace_prefix
setup_structured_logging()
_COMPONENT_NAME = Path(__file__).stem
console = Console()
app = typer.Typer(name='onex', help=
    'ONEX CLI tool for node validation, stamping, and execution.',
    add_completion=True)


class CLIEventSubscriber:
    """
    Event subscriber for CLI operations.

    Provides real-time feedback during CLI node execution by subscribing
    to relevant events on the event bus.
    """

    def __init__(self, correlation_id: str):
        self.correlation_id = correlation_id
        self.events_received: list[OnexEvent] = []
        self.progress: Optional[Progress] = None
        self.task_id: Optional[TaskID] = None

    def handle_event(self, event: OnexEvent) ->None:
        """Handle events from the CLI node execution."""
        if event.correlation_id != self.correlation_id:
            return
        self.events_received.append(event)
        if event.event_type == 'NODE_START':
            if self.progress and self.task_id:
                node_name = event.metadata.get('node_name', 'node'
                    ) if event.metadata else 'node'
                self.progress.update(self.task_id, description=
                    f'Starting {node_name}...')
        elif event.event_type == 'NODE_SUCCESS':
            if self.progress and self.task_id:
                self.progress.update(self.task_id, description=
                    '✅ Completed successfully')
        elif event.event_type == 'NODE_FAILURE':
            if self.progress and self.task_id:
                self.progress.update(self.task_id, description='❌ Failed')
        elif event.event_type == 'LOG':
            log_level = event.metadata.get('level', 'INFO'
                ) if event.metadata else 'INFO'
            message = event.metadata.get('message', ''
                ) if event.metadata else ''
            if log_level in ['ERROR', 'WARNING']:
                console.print(f'[yellow]{log_level}[/yellow]: {message}')


def execute_cli_command(command: str, target_node: Optional[str]=None,
    node_version: Optional[str]=None, args: Optional[list]=None, introspect:
    bool=False, list_versions: bool=False, show_progress: bool=True) ->tuple[
    bool, str, Optional[Dict[str, Any]]]:
    """
    Execute a CLI command using the CLI node with event bus subscription.

    Args:
        command: Command to execute
        target_node: Target node name (for 'run' command)
        node_version: Specific version to run
        args: Arguments to pass to the target node
        introspect: Whether to show introspection
        list_versions: Whether to list versions
        show_progress: Whether to show progress indicators

    Returns:
        Tuple of (success, message, result_data)
    """
    correlation_id = str(uuid.uuid4())
    event_bus: ProtocolEventBus = InMemoryEventBus()
    subscriber = CLIEventSubscriber(correlation_id)
    event_bus.subscribe(subscriber.handle_event)
    input_state = create_cli_input_state(command=command, target_node=
        target_node, node_version=node_version, args=args or [], introspect
        =introspect, list_versions=list_versions, correlation_id=
        correlation_id, version=CLI_STATE_SCHEMA_VERSION)
    cli_node = CLINode(event_bus=event_bus)
    import asyncio

    async def _execute_async() ->Any:
        return await cli_node.execute(input_state)
    if show_progress:
        with Progress(SpinnerColumn(), TextColumn(
            '[progress.description]{task.description}'), console=console
            ) as progress:
            subscriber.progress = progress
            subscriber.task_id = progress.add_task('Executing command...',
                total=None)
            try:
                output_state = asyncio.run(_execute_async())
            except Exception as e:
                return False, f'CLI node execution failed: {e}', None
    else:
        try:
            output_state = asyncio.run(_execute_async())
        except Exception as e:
            return False, f'CLI node execution failed: {e}', None
    success = output_state.status == 'success'
    return success, output_state.message, output_state.result_data


@app.callback()
def main(verbose: bool=typer.Option(False, '--verbose', '-v', help=
    'Enable verbose output'), quiet: bool=typer.Option(False, '--quiet',
    '-q', help='Silence all output except errors'), debug: bool=typer.
    Option(False, '--debug', help='Enable debug output')) ->None:
    """
    ONEX: Open Node Execution - Command Line Interface

    Event-driven CLI that uses the CLI node for all operations.
    """
    if debug:
        log_level = LogLevelEnum.DEBUG
    elif verbose:
        log_level = LogLevelEnum.DEBUG
    elif quiet:
        log_level = LogLevelEnum.ERROR
    else:
        log_level = LogLevelEnum.INFO
    from omnibase.core.core_structured_logging import get_global_config
    config = get_global_config()
    if config:
        config.log_level = log_level
    if debug:
        emit_log_event(LogLevelEnum.DEBUG, 'Debug logging enabled', node_id
            =_COMPONENT_NAME, event_bus=self._event_bus)


@app.command()
def run(node_name: str=typer.Argument(..., help='Name of the node to run'),
    version: str=typer.Option(None, '--version', help=
    'Specific version to run (defaults to latest)'), list_versions: bool=
    typer.Option(False, '--list-versions', help=
    'List available versions for the specified node'), introspect: bool=
    typer.Option(False, '--introspect', help=
    'Show node introspection information'), node_args: str=typer.Option(
    None, '--args', help=
    'Additional arguments to pass to the node (as JSON string)')) ->None:
    """
    Run an ONEX node with automatic version resolution.

    Examples:
      onex run parity_validator_node --args='["--format", "summary"]'
      onex run stamper_node --version v1_0_0 --args='["file", "README.md"]'
      onex run parity_validator_node --introspect
    """
    args_list = []
    if node_args:
        try:
            args_list = json.loads(node_args)
        except json.JSONDecodeError:
            console.print(f'[red]❌ Invalid JSON in --args: {node_args}[/red]')
            raise typer.Exit(1)
    success, message, result_data = execute_cli_command(command='run',
        target_node=node_name, node_version=version, args=args_list,
        introspect=introspect, list_versions=list_versions)
    if success:
        console.print(f'[green]✅ {message}[/green]')
        if result_data:
            if introspect and 'introspection' in result_data:
                introspection = result_data['introspection']
                table = Table(title=f'Node Introspection: {node_name}')
                table.add_column('Property', style='cyan')
                table.add_column('Value', style='white')
                for key, value in introspection.items():
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value, indent=2)
                    table.add_row(key, str(value))
                console.print(table)
            elif list_versions and 'versions' in result_data:
                versions = result_data['versions']
                latest = result_data.get('latest_version')
                console.print(
                    f'\n[bold]📦 Available versions for {node_name}:[/bold]')
                for version_str in versions:
                    marker = (' [green](latest)[/green]' if version_str ==
                        latest else '')
                    console.print(f'  • {version_str}{marker}')
            else:
                console.print('\n[bold]Result Data:[/bold]')
                console.print(json.dumps(result_data, indent=2))
        sys.exit(0)
    else:
        console.print(f'[red]❌ {message}[/red]')
        sys.exit(1)


@app.command()
def list_nodes() ->None:
    """List all available ONEX nodes."""
    success, message, result_data = execute_cli_command(command='list-nodes')
    if success:
        if result_data and 'nodes' in result_data:
            nodes = result_data['nodes']
            table = Table(title='Available ONEX Nodes')
            table.add_column('Node Name', style='cyan')
            table.add_column('Latest Version', style='green')
            table.add_column('Description', style='white')
            if isinstance(nodes, dict):
                for node_name, node_info in nodes.items():
                    table.add_row(node_name, node_info.get('version',
                        'Unknown'), 'No description available')
            else:
                for node_info in nodes:
                    table.add_row(node_info.get('name', 'Unknown'),
                        node_info.get('latest_version', 'Unknown'),
                        node_info.get('description',
                        'No description available'))
            console.print(table)
        else:
            console.print(message)
        sys.exit(0)
    else:
        console.print(f'[red]❌ {message}[/red]')
        sys.exit(1)


@app.command()
def node_info(node_name: str=typer.Argument(..., help=
    'Name of the node to get info for'), version: str=typer.Option(None,
    '--version', help='Specific version (defaults to latest)')) ->None:
    """Get detailed information about a specific ONEX node."""
    success, message, result_data = execute_cli_command(command='node-info',
        target_node=node_name, node_version=version)
    if success:
        if result_data and 'node_info' in result_data:
            node_info = result_data['node_info']
            console.print(f'\n[bold]📋 Node Information: {node_name}[/bold]')
            console.print(
                f"[cyan]Version:[/cyan] {node_info.get('version', 'Unknown')}")
            console.print(
                f"[cyan]Description:[/cyan] {node_info.get('description', 'No description')}"
                )
            console.print(
                f"[cyan]Author:[/cyan] {node_info.get('author', 'Unknown')}")
            console.print(
                f"[cyan]Namespace:[/cyan] {node_info.get('namespace', 'Unknown')}"
                )
            if 'capabilities' in node_info:
                console.print('\n[bold]Capabilities:[/bold]')
                for capability in node_info['capabilities']:
                    console.print(f'  • {capability}')
        else:
            console.print(message)
        sys.exit(0)
    else:
        console.print(f'[red]❌ {message}[/red]')
        sys.exit(1)


@app.command()
def version() ->None:
    """Display version information."""
    success, message, result_data = execute_cli_command(command='version')
    if success:
        console.print(message)
        if result_data:
            console.print(json.dumps(result_data, indent=2))
        sys.exit(0)
    else:
        console.print(f'[red]❌ {message}[/red]')
        sys.exit(1)


@app.command()
def info() ->None:
    """Display system information."""
    success, message, result_data = execute_cli_command(command='info')
    if success:
        console.print(message)
        if result_data:
            console.print(json.dumps(result_data, indent=2))
        sys.exit(0)
    else:
        console.print(f'[red]❌ {message}[/red]')
        sys.exit(1)


@app.command()
def handlers() ->None:
    """List and manage file type handlers."""
    success, message, result_data = execute_cli_command(command='handlers')
    if success:
        if result_data and 'handlers' in result_data:
            handlers = result_data['handlers']
            table = Table(title='Registered File Type Handlers')
            table.add_column('Extension/Name', style='cyan')
            table.add_column('Handler', style='green')
            table.add_column('Source', style='yellow')
            table.add_column('Priority', style='white')
            for handler_info in handlers:
                table.add_row(handler_info.get('extension', 'Unknown'),
                    handler_info.get('handler_name', 'Unknown'),
                    handler_info.get('source', 'Unknown'), str(handler_info
                    .get('priority', 'Unknown')))
            console.print(table)
        else:
            console.print(message)
        sys.exit(0)
    else:
        console.print(f'[red]❌ {message}[/red]')
        sys.exit(1)


if __name__ == '__main__':
    app()
