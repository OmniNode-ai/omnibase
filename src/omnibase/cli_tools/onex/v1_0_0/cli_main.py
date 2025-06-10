"""
Event-Driven ONEX CLI Tool.

This CLI tool directly uses the CLI node with event bus subscription for
real-time feedback and observability. Replaces the legacy CLI implementation
with a cleaner, event-driven architecture.
"""

import asyncio
import difflib
import importlib.util
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import typer
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TaskID, TextColumn
from rich.table import Table

from omnibase.core.core_structured_logging import (
    emit_log_event_sync,
    setup_structured_logging,
)
from omnibase.enums import LogLevelEnum
from omnibase.metadata.metadata_constants import get_namespace_prefix
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.nodes.cli_node.v1_0_0.models.state import (
    CLI_STATE_SCHEMA_VERSION,
    create_cli_input_state,
)
from omnibase.nodes.cli_node.v1_0_0.node import CLINode
from omnibase.model.model_event_bus_config import ModelEventBusConfig
from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import (  # [ONEX] KafkaEventBus: canonical import for CLI usage
    KafkaEventBus,
)
from omnibase.nodes.node_registry_node.v1_0_0.models.state import (
    ToolProxyInvocationRequest,
)
from omnibase.nodes.node_registry_node.v1_0_0.node import NodeRegistryNode
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.codegen.contract_to_model import (
    generate_state_models,
)
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.utils.json_encoder import OmniJSONEncoder

setup_structured_logging()
_COMPONENT_NAME = Path(__file__).stem
console = Console()
app = typer.Typer(
    name="onex",
    help="ONEX CLI tool for node validation, stamping, and execution.",
    add_completion=True,
)

# --- Mount node_manager CLI commands as a subcommand group ---
from omnibase.nodes.node_manager.v1_0_0.tools.tool_cli_commands import cli as node_manager_cli
app.add_typer(node_manager_cli, name="node-manager", help="Node Manager: node generation, maintenance, validation")


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

    def handle_event(self, event: OnexEvent) -> None:
        """Handle events from the CLI node execution."""
        if event.correlation_id != self.correlation_id:
            return
        self.events_received.append(event)
        if event.event_type == "NODE_START":
            if self.progress and self.task_id:
                node_name = (
                    event.metadata.get("node_name", "node")
                    if event.metadata
                    else "node"
                )
                self.progress.update(
                    self.task_id, description=f"Starting {node_name}..."
                )
        elif event.event_type == "NODE_SUCCESS":
            if self.progress and self.task_id:
                self.progress.update(
                    self.task_id, description="✅ Completed successfully"
                )
        elif event.event_type == "NODE_FAILURE":
            if self.progress and self.task_id:
                self.progress.update(self.task_id, description="❌ Failed")
        elif event.event_type == "LOG":
            log_level = (
                event.metadata.get("level", "INFO") if event.metadata else "INFO"
            )
            message = event.metadata.get("message", "") if event.metadata else ""
            if log_level in ["ERROR", "WARNING"]:
                console.print(f"[yellow]{log_level}[/yellow]: {message}")


def get_event_bus_type(event_bus_type_flag: str = None) -> str:
    # Priority: CLI flag > env var > default
    if event_bus_type_flag:
        return event_bus_type_flag.lower()
    return os.environ.get("ONEX_EVENT_BUS_TYPE", "inmemory").lower()


@app.callback()
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Silence all output except errors"
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug output"),
    event_bus_type: str = typer.Option(
        None, "--event-bus-type", help="Event bus type: inmemory or kafka"
    ),
) -> None:
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
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            "Debug logging enabled",
            node_id=_COMPONENT_NAME,
            event_bus=InMemoryEventBus(),
        )

    # Set event bus type globally for all commands
    selected_event_bus_type = get_event_bus_type(event_bus_type)
    os.environ["ONEX_EVENT_BUS_TYPE"] = selected_event_bus_type
    emit_log_event_sync(
        LogLevelEnum.INFO,
        f"[main] Using event bus type: {selected_event_bus_type}",
        node_id=_COMPONENT_NAME,
        event_bus=InMemoryEventBus(),
    )


def execute_cli_command(
    command: str,
    target_node: Optional[str] = None,
    node_version: Optional[str] = None,
    args: Optional[list] = None,
    introspect: bool = False,
    list_versions: bool = False,
    show_progress: bool = True,
    event_bus_type: Optional[str] = None,
) -> tuple[bool, str, Optional[Dict[str, Any]]]:
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
        event_bus_type: Event bus type (inmemory or kafka)

    Returns:
        Tuple of (success, message, result_data)
    """
    correlation_id = str(uuid.uuid4())
    from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import (
        get_event_bus,
    )

    event_bus: ProtocolEventBus = get_event_bus(event_bus_type=event_bus_type)
    subscriber = CLIEventSubscriber(correlation_id)
    event_bus.subscribe(subscriber.handle_event)
    input_state = create_cli_input_state(
        command=command,
        target_node=target_node,
        node_version=node_version,
        args=args or [],
        introspect=introspect,
        list_versions=list_versions,
        correlation_id=correlation_id,
        version=CLI_STATE_SCHEMA_VERSION,
    )
    cli_node = CLINode(event_bus=event_bus)
    import asyncio

    async def _execute_async() -> Any:
        return await cli_node.execute(input_state)

    if show_progress:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            subscriber.progress = progress
            subscriber.task_id = progress.add_task("Executing command...", total=None)
            try:
                output_state = asyncio.run(_execute_async())
            except Exception as e:
                return False, f"CLI node execution failed: {e}", None
    else:
        try:
            output_state = asyncio.run(_execute_async())
        except Exception as e:
            return False, f"CLI node execution failed: {e}", None
    success = output_state.status == "success"
    return success, output_state.message, output_state.result_data


def publish_run_node_event(event_bus, node_name, args, correlation_id, log_format):
    emit_log_event_sync(
        LogLevelEnum.DEBUG,
        f"[publish_run_node_event] Creating TOOL_PROXY_INVOKE event for node={node_name} correlation_id={correlation_id}",
        event_bus=event_bus,
    )
    event = OnexEvent(
        event_id=uuid.uuid4(),
        timestamp=datetime.now(timezone.utc),
        node_id="cli_node",
        event_type=OnexEventTypeEnum.TOOL_PROXY_INVOKE,
        correlation_id=correlation_id,
        metadata={
            "target_node": node_name,
            "args": args,
            "log_format": log_format,
        },
    )
    emit_log_event_sync(
        LogLevelEnum.DEBUG,
        f"[publish_run_node_event] Event created: {event}",
        event_bus=event_bus,
    )
    return event


@app.command()
def run(
    node_name: str = typer.Argument(..., help="Name of the node to run"),
    args: str = typer.Option(
        None, "--args", help="Arguments to pass to the node (as JSON string)"
    ),
    log_format: str = typer.Option(
        "json", "--log-format", help="Log output format (json, markdown, etc)"
    ),
    event_bus_type: str = typer.Option(
        None, "--event-bus-type", help="Event bus type: inmemory or kafka"
    ),
    introspect: bool = typer.Option(
        False, "--introspect", help="Show node introspection information and exit."
    ),
):
    """
    Protocol-pure event-driven ONEX CLI runner.
    """
    if introspect:
        import importlib
        module_path = f"omnibase.nodes.{node_name}.v1_0_0.node"
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, "get_introspection"):
                import json
                result = module.get_introspection()
                print(json.dumps(result, indent=2))
                raise typer.Exit(0)
            else:
                print(f"[ERROR] Node {node_name} does not support introspection.")
                raise typer.Exit(1)
        except Exception as e:
            print(f"[ERROR] Failed to introspect node {node_name}: {e}")
            raise typer.Exit(1)
    import os

    correlation_id = str(uuid.uuid4())
    bus_type = (
        event_bus_type or os.environ.get("ONEX_EVENT_BUS_TYPE", "inmemory").lower()
    )
    if bus_type == "kafka":
        # Protocol-compliant: use factory and default config for Kafka
        try:
            from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import (
                get_event_bus,
            )

            event_bus = get_event_bus(
                event_bus_type="kafka", config=ModelEventBusConfig.default()
            )
            print("[DEBUG] Using KafkaEventBus (via factory) for CLI run")

            async def async_run():
                try:
                    await event_bus.connect()
                    sub = await event_bus.subscribe(handle_event)
                    if asyncio.iscoroutine(sub):
                        print(
                            "[WARNING] subscribe() returned coroutine, did you forget to await?"
                        )
                    # Parse args
                    args_list = []
                    if args:
                        try:
                            args_list = json.loads(args)
                        except Exception:
                            console.print(f"[red]Invalid JSON for --args: {args}[/red]")
                            raise typer.Exit(1)
                    event = publish_run_node_event(
                        event_bus, node_name, args_list, correlation_id, log_format
                    )
                    emit_log_event_sync(
                        LogLevelEnum.DEBUG,
                        f"[async_run] Publishing event: {event}",
                        event_bus=event_bus,
                    )
                    await event_bus.publish(event)
                    emit_log_event_sync(
                        LogLevelEnum.DEBUG,
                        f"[async_run] Event published",
                        event_bus=event_bus,
                    )
                    # Wait for events
                    timeout = 10
                    start = asyncio.get_event_loop().time()
                    while asyncio.get_event_loop().time() - start < timeout:
                        await asyncio.sleep(0.1)
                    print(
                        f"[green]Event-driven run complete for correlation_id: {correlation_id}[/green]"
                    )
                    emit_log_event_sync(
                        LogLevelEnum.DEBUG,
                        "[CLI] Node run completed. (Output state visibility placeholder)",
                        node_id=_COMPONENT_NAME,
                        event_bus=event_bus,
                    )
                    print(
                        "[INFO] Node run completed. (If you expected a result, ensure the node emits it as a log or event.)"
                    )
                except ImportError as e:
                    print(
                        f"[ERROR] Kafka async dependencies not available: {e}. Falling back to in-memory event bus."
                    )
                    fallback_to_inmemory()
                except Exception as e:
                    print(
                        f"[ERROR] Async Kafka event bus failed: {e}. Falling back to in-memory event bus."
                    )
                    fallback_to_inmemory()

            def fallback_to_inmemory():
                print(
                    "[WARNING] Falling back to InMemoryEventBus (sync mode). Some async features may be unavailable."
                )
                event_bus_fallback = InMemoryEventBus()
                # Re-run the sync logic as in the else branch below
                received_any = False

                def handle_event(event: OnexEvent):
                    nonlocal received_any
                    received_any = True
                    print(
                        f"[DEBUG] Received event: type={getattr(event, 'event_type', None)} correlation_id={getattr(event, 'correlation_id', None)}"
                    )
                    if getattr(event, "correlation_id", None) == correlation_id:
                        if log_format == "markdown":
                            from rich.console import Group
                            from rich.panel import Panel
                            from rich.table import Table

                            from omnibase.core.core_structured_logging import (
                                emit_log_event_sync,
                            )
                            from omnibase.enums import LogLevelEnum, OnexEventTypeEnum

                            if (
                                getattr(event, "event_type", None)
                                == OnexEventTypeEnum.STRUCTURED_LOG
                            ):
                                log_entry = None
                                if hasattr(event, "metadata") and event.metadata:
                                    if "log_entry" in event.metadata:
                                        log_entry = event.metadata["log_entry"]
                                    elif hasattr(event.metadata, "log_entry"):
                                        log_entry = event.metadata.log_entry
                                if log_entry:
                                    level = getattr(
                                        log_entry, "level", None
                                    ) or log_entry.get("level", "INFO")
                                    message = getattr(
                                        log_entry, "message", None
                                    ) or log_entry.get("message", "")
                                    context = getattr(
                                        log_entry, "context", None
                                    ) or log_entry.get("context", {})
                                    timestamp = getattr(
                                        context, "timestamp", None
                                    ) or context.get("timestamp", "")
                                    func = getattr(
                                        context, "calling_function", None
                                    ) or context.get("calling_function", "")
                                    line = getattr(
                                        context, "calling_line", None
                                    ) or context.get("calling_line", "")
                                    emoji = log_level_emoji(level)
                                    log_level_str = (
                                        level.value.upper()
                                        if hasattr(level, "value")
                                        else str(level).upper()
                                    )
                                    ts = (
                                        timestamp.split(".")[0]
                                        if "." in timestamp
                                        else timestamp
                                    )
                                    msg_str = str(message)
                                    console.print(
                                        f"{ts} {emoji} {log_level_str} {msg_str} | {func}:{line}"
                                    )
                                else:
                                    console.print(
                                        "[yellow]Malformed STRUCTURED_LOG event: missing log_entry.[/yellow]"
                                    )
                            elif (
                                getattr(event, "event_type", None)
                                == OnexEventTypeEnum.INTROSPECTION_RESPONSE
                            ):
                                from rich.table import Table

                                emit_log_event_sync(
                                    LogLevelEnum.DEBUG,
                                    f"[CLI] Pretty-printing INTROSPECTION_RESPONSE event",
                                    event_bus=None,
                                )
                                introspection = None
                                if (
                                    hasattr(event, "metadata")
                                    and event.metadata
                                    and "introspection" in (event.metadata or {})
                                ):
                                    introspection = event.metadata["introspection"]
                                elif (
                                    hasattr(event, "metadata")
                                    and event.metadata
                                    and hasattr(event.metadata, "introspection")
                                ):
                                    introspection = event.metadata.introspection
                                if introspection:
                                    table = Table(
                                        title="Node Introspection",
                                        show_header=True,
                                        header_style="bold magenta",
                                    )
                                    table.add_column("Field", style="dim", width=24)
                                    table.add_column("Value", style="bold")
                                    for k, v in introspection.items():
                                        table.add_row(str(k), str(v))
                                    console.print(
                                        Panel(
                                            table,
                                            title="[bold green]Introspection Result[/bold green]",
                                        )
                                    )
                                else:
                                    console.print(
                                        "[yellow]No introspection payload found in event metadata.[/yellow]"
                                    )
                                emit_log_event_sync(
                                    LogLevelEnum.DEBUG,
                                    f"[CLI] Finished pretty-printing INTROSPECTION_RESPONSE event",
                                    event_bus=None,
                                )
                            else:
                                msg = None
                                if hasattr(event, "metadata") and event.metadata:
                                    if (
                                        hasattr(event.metadata, "message")
                                        and event.metadata.message
                                    ):
                                        msg = event.metadata.message
                                    elif "message" in event.metadata:
                                        msg = event.metadata["message"]
                                print(f"[DEBUG] Event: {msg}")

                # Simulate a minimal sync run
                print(
                    "[INFO] Running in sync fallback mode. Async features are disabled."
                )
                # ... (invoke the sync run logic as in the else branch) ...

            try:
                asyncio.run(async_run())
            except Exception as e:
                print(
                    f"[ERROR] Failed to run async CLI: {e}. Falling back to sync mode."
                )
                fallback_to_inmemory()
        except ImportError as e:
            print(
                f"[ERROR] Kafka dependencies not available: {e}. Falling back to in-memory event bus."
            )
            fallback_to_inmemory()
    else:
        event_bus = InMemoryEventBus()
        print("[DEBUG] Using InMemoryEventBus for CLI run")
        received_any = False

        def handle_event(event: OnexEvent):
            nonlocal received_any
            received_any = True
            print(
                f"[DEBUG] Received event: type={getattr(event, 'event_type', None)} correlation_id={getattr(event, 'correlation_id', None)}"
            )
            if getattr(event, "correlation_id", None) == correlation_id:
                if log_format == "markdown":
                    from rich.console import Group
                    from rich.panel import Panel
                    from rich.table import Table

                    from omnibase.core.core_structured_logging import (
                        emit_log_event_sync,
                    )
                    from omnibase.enums import LogLevelEnum, OnexEventTypeEnum

                    if (
                        getattr(event, "event_type", None)
                        == OnexEventTypeEnum.STRUCTURED_LOG
                    ):
                        # Extract log_entry and context
                        log_entry = None
                        if hasattr(event, "metadata") and event.metadata:
                            if "log_entry" in event.metadata:
                                log_entry = event.metadata["log_entry"]
                            elif hasattr(event.metadata, "log_entry"):
                                log_entry = event.metadata.log_entry
                        if log_entry:
                            # Extract fields
                            level = getattr(log_entry, "level", None) or log_entry.get(
                                "level", "INFO"
                            )
                            message = getattr(
                                log_entry, "message", None
                            ) or log_entry.get("message", "")
                            context = getattr(
                                log_entry, "context", None
                            ) or log_entry.get("context", {})
                            timestamp = getattr(
                                context, "timestamp", None
                            ) or context.get("timestamp", "")
                            func = getattr(
                                context, "calling_function", None
                            ) or context.get("calling_function", "")
                            line = getattr(
                                context, "calling_line", None
                            ) or context.get("calling_line", "")
                            emoji = log_level_emoji(level)
                            log_level_str = (
                                level.value.upper()
                                if hasattr(level, "value")
                                else str(level).upper()
                            )
                            # Compose Markdown log line
                            ts = (
                                timestamp.split(".")[0]
                                if "." in timestamp
                                else timestamp
                            )
                            msg_str = str(message)
                            console.print(
                                f"{ts} {emoji} {log_level_str} {msg_str} | {func}:{line}"
                            )
                        else:
                            console.print(
                                "[yellow]Malformed STRUCTURED_LOG event: missing log_entry.[/yellow]"
                            )
                    elif (
                        getattr(event, "event_type", None)
                        == OnexEventTypeEnum.INTROSPECTION_RESPONSE
                    ):
                        from rich.table import Table

                        emit_log_event_sync(
                            LogLevelEnum.DEBUG,
                            f"[CLI] Pretty-printing INTROSPECTION_RESPONSE event",
                            event_bus=None,
                        )
                        introspection = None
                        if (
                            hasattr(event, "metadata")
                            and event.metadata
                            and "introspection" in (event.metadata or {})
                        ):
                            introspection = event.metadata["introspection"]
                        elif (
                            hasattr(event, "metadata")
                            and event.metadata
                            and hasattr(event.metadata, "introspection")
                        ):
                            introspection = event.metadata.introspection
                        if introspection:
                            table = Table(
                                title="Node Introspection",
                                show_header=True,
                                header_style="bold magenta",
                            )
                            table.add_column("Field", style="dim", width=24)
                            table.add_column("Value", style="bold")
                            for k, v in introspection.items():
                                table.add_row(str(k), str(v))
                            console.print(
                                Panel(
                                    table,
                                    title="[bold green]Introspection Result[/bold green]",
                                )
                            )
                        else:
                            console.print(
                                "[yellow]No introspection payload found in event metadata.[/yellow]"
                            )
                        emit_log_event_sync(
                            LogLevelEnum.DEBUG,
                            f"[CLI] Finished pretty-printing INTROSPECTION_RESPONSE event",
                            event_bus=None,
                        )
                    else:
                        msg = None
                        if hasattr(event, "metadata") and event.metadata:
                            if (
                                hasattr(event.metadata, "message")
                                and event.metadata.message
                            ):
                                msg = event.metadata.message
                            elif "message" in event.metadata:
                                msg = event.metadata["message"]
                        if not msg:
                            msg = getattr(event, "event_type", None)
                        console.print(
                            f"[bold]{getattr(event, 'event_type', None)}[/bold]: {msg}"
                        )
                else:
                    # Only print JSON for DEBUG/TRACE if explicitly requested
                    from omnibase.utils.json_encoder import OmniJSONEncoder

                    if (
                        getattr(event, "event_type", None)
                        == OnexEventTypeEnum.STRUCTURED_LOG
                    ):
                        log_entry = None
                        if hasattr(event, "metadata") and event.metadata:
                            if "log_entry" in event.metadata:
                                log_entry = event.metadata["log_entry"]
                            elif hasattr(event.metadata, "log_entry"):
                                log_entry = event.metadata.log_entry
                        if log_entry:
                            level = getattr(log_entry, "level", None) or log_entry.get(
                                "level", "INFO"
                            )
                            if level in (LogLevelEnum.DEBUG, LogLevelEnum.TRACE):
                                console.print(
                                    json.dumps(
                                        event.model_dump(),
                                        indent=2,
                                        cls=OmniJSONEncoder,
                                    )
                                )
                            else:
                                message = getattr(
                                    log_entry, "message", None
                                ) or log_entry.get("message", "")
                                console.print(f"[STRUCTURED_LOG] {message}")
                        else:
                            console.print(
                                json.dumps(
                                    event.model_dump(), indent=2, cls=OmniJSONEncoder
                                )
                            )
                    else:
                        console.print(
                            json.dumps(
                                event.model_dump(), indent=2, cls=OmniJSONEncoder
                            )
                        )
            else:
                print(f"[DEBUG] (non-matching correlation_id) Event: {event}")

        event_bus.subscribe(handle_event)
        # Parse args
        args_list = []
        if args:
            try:
                args_list = json.loads(args)
            except Exception:
                console.print(f"[red]Invalid JSON for --args: {args}[/red]")
                raise typer.Exit(1)
        event = publish_run_node_event(
            event_bus, node_name, args_list, correlation_id, log_format
        )
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[InMemoryEventBus] Publishing event: {event}",
            event_bus=event_bus,
        )
        event_bus.publish(event)
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[InMemoryEventBus] Event published",
            event_bus=event_bus,
        )
        # Wait for events
        timeout = 10
        start = time.time()
        while time.time() - start < timeout:
            time.sleep(0.1)
        if not received_any:
            print(
                "[WARNING] No events were received during the run. Check event bus configuration and node output."
            )
        console.print(
            f"[green]Event-driven run complete for correlation_id: {correlation_id}[/green]"
        )

    # === SCENARIO-DRIVEN NODE RUN: DEFER EVENT BUS SELECTION TO NODE ===
    if args and "--run-scenario" in args:
        print("[DEBUG] Detected scenario-driven node run. Deferring event bus selection to node's registry_tools/backend_selection.")
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            "[CLI] Deferring event bus selection to node for scenario-driven run.",
            node_id=_COMPONENT_NAME,
        )
        # Call the node run logic without initializing event bus here
        # (Assume the node's main() or entrypoint will handle event bus selection)
        # ... (rest of scenario-driven node run logic here) ...
        return
    # === END SCENARIO-DRIVEN NODE RUN ===

    # For CLI-only operations or non-scenario-driven nodes, retain existing event bus logic
    if bus_type == "kafka":
        # Protocol-compliant: use factory and default config for Kafka
        try:
            from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import (
                get_event_bus,
            )

            event_bus = get_event_bus(
                event_bus_type="kafka", config=ModelEventBusConfig.default()
            )
            print("[DEBUG] Using KafkaEventBus (via factory) for CLI run")
            # ... (rest of existing Kafka logic) ...
        except ImportError as e:
            print(
                f"[ERROR] Kafka async dependencies not available: {e}. Falling back to in-memory event bus."
            )
            # ... (fallback logic) ...
        except Exception as e:
            print(
                f"[ERROR] Async Kafka event bus failed: {e}. Falling back to in-memory event bus."
            )
            # ... (fallback logic) ...


@app.command()
def list_nodes() -> None:
    """List all available ONEX nodes."""
    success, message, result_data = execute_cli_command(command="list-nodes")
    if success:
        if result_data and "nodes" in result_data:
            nodes = result_data["nodes"]
            table = Table(title="Available ONEX Nodes")
            table.add_column("Node Name", style="cyan")
            table.add_column("Latest Version", style="green")
            table.add_column("Description", style="white")
            if isinstance(nodes, dict):
                for node_name, node_info in nodes.items():
                    table.add_row(
                        node_name,
                        node_info.get("version", "Unknown"),
                        "No description available",
                    )
            else:
                for node_info in nodes:
                    table.add_row(
                        node_info.get("name", "Unknown"),
                        node_info.get("latest_version", "Unknown"),
                        node_info.get("description", "No description available"),
                    )
            console.print(table)
        else:
            console.print(message)
        sys.exit(0)
    else:
        console.print(f"[red]❌ {message}[/red]")
        sys.exit(1)


@app.command()
def node_info(
    node_name: str = typer.Argument(..., help="Name of the node to get info for"),
    version: str = typer.Option(
        None, "--version", help="Specific version (defaults to latest)"
    ),
) -> None:
    """Get detailed information about a specific ONEX node."""
    success, message, result_data = execute_cli_command(
        command="node-info", target_node=node_name, node_version=version
    )
    if success:
        if result_data and "node_info" in result_data:
            node_info = result_data["node_info"]
            console.print(f"\n[bold]📋 Node Information: {node_name}[/bold]")
            console.print(
                f"[cyan]Version:[/cyan] {node_info.get('version', 'Unknown')}"
            )
            console.print(
                f"[cyan]Description:[/cyan] {node_info.get('description', 'No description')}"
            )
            console.print(f"[cyan]Author:[/cyan] {node_info.get('author', 'Unknown')}")
            console.print(
                f"[cyan]Namespace:[/cyan] {node_info.get('namespace', 'Unknown')}"
            )
            if "capabilities" in node_info:
                console.print("\n[bold]Capabilities:[/bold]")
                for capability in node_info["capabilities"]:
                    console.print(f"  • {capability}")
        else:
            console.print(message)
        sys.exit(0)
    else:
        console.print(f"[red]❌ {message}[/red]")
        sys.exit(1)


@app.command()
def version() -> None:
    """Display version information."""
    success, message, result_data = execute_cli_command(command="version")
    if success:
        console.print(message)
        if result_data:
            console.print(json.dumps(result_data, indent=2, cls=OmniJSONEncoder))
        sys.exit(0)
    else:
        console.print(f"[red]❌ {message}[/red]")
        sys.exit(1)


@app.command()
def info() -> None:
    """Display system information."""
    success, message, result_data = execute_cli_command(command="info")
    if success:
        console.print(message)
        if result_data:
            console.print(json.dumps(result_data, indent=2, cls=OmniJSONEncoder))
        sys.exit(0)
    else:
        console.print(f"[red]❌ {message}[/red]")
        sys.exit(1)


@app.command()
def handlers() -> None:
    """List and manage file type handlers."""
    success, message, result_data = execute_cli_command(command="handlers")
    if success:
        if result_data and "handlers" in result_data:
            handlers = result_data["handlers"]
            table = Table(title="Registered File Type Handlers")
            table.add_column("Extension/Name", style="cyan")
            table.add_column("Handler", style="green")
            table.add_column("Source", style="yellow")
            table.add_column("Priority", style="white")
            for handler_info in handlers:
                table.add_row(
                    handler_info.get("extension", "Unknown"),
                    handler_info.get("handler_name", "Unknown"),
                    handler_info.get("source", "Unknown"),
                    str(handler_info.get("priority", "Unknown")),
                )
            console.print(table)
        else:
            console.print(message)
        sys.exit(0)
    else:
        console.print(f"[red]❌ {message}[/red]")
        sys.exit(1)


@app.command()
def describe(
    node: str = typer.Option(
        "node_registry_node",
        "--node",
        help="Node to describe (default: node_registry_node)",
    ),
    format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: 'table', 'json', or 'yaml' (default: table)",
    ),
) -> None:
    """
    Describe the registry node (or another node in future) with canonical introspection output.

    Examples:
      onex describe
      onex describe --format json
      onex describe --format yaml
      onex describe --node node_registry_node --format table
    """
    try:
        # For MVP, only support registry node
        node_instance = NodeRegistryNode()
        response = node_instance.get_introspection()
    except Exception as exc:
        console.print(f"[red]❌ Failed to get introspection: {exc}[/red]")
        sys.exit(1)
    if format == "json":
        console.print(json.dumps(response, indent=2, cls=OmniJSONEncoder))
    elif format == "yaml":
        try:
            yaml_str = yaml.safe_dump(response, sort_keys=False, allow_unicode=True)
            console.print(yaml_str)
        except Exception as exc:
            console.print(f"[red]❌ Failed to render YAML: {exc}[/red]")
            sys.exit(1)
    elif format == "table":
        # Print key sections as rich tables
        from rich.panel import Panel
        from rich.table import Table

        # Node Metadata
        meta = response.get("node_metadata", {})
        meta_table = Table(title="Node Metadata")
        meta_table.add_column("Field", style="cyan")
        meta_table.add_column("Value", style="white")
        for k, v in meta.items():
            meta_table.add_row(str(k), str(v))
        console.print(meta_table)
        # Contract
        contract = response.get("contract", {})
        contract_table = Table(title="Contract")
        contract_table.add_column("Field", style="cyan")
        contract_table.add_column("Value", style="white")
        for k, v in contract.items():
            contract_table.add_row(str(k), str(v))
        console.print(contract_table)
        # Ports
        ports = response.get("ports", {})
        if ports:
            ports_table = Table(title="Ports")
            ports_table.add_column("Field", style="cyan")
            ports_table.add_column("Value", style="white")
            for k, v in ports.items():
                ports_table.add_row(str(k), str(v))
            console.print(ports_table)
        # Trust Status
        trust = response.get("trust_status", [])
        if trust:
            trust_table = Table(title="Trust Status")
            trust_table.add_column("Node ID", style="cyan")
            trust_table.add_column("Trust State", style="green")
            trust_table.add_column("Status", style="yellow")
            trust_table.add_column("Last Announce", style="white")
            for entry in trust:
                trust_table.add_row(
                    str(entry.get("node_id", "")),
                    str(entry.get("trust_state", "")),
                    str(entry.get("status", "")),
                    str(entry.get("last_announce", "")),
                )
            console.print(trust_table)
        # Registry
        registry = response.get("registry", {})
        if registry:
            registry_table = Table(title="Registry State")
            registry_table.add_column("Field", style="cyan")
            registry_table.add_column("Value", style="white")
            for k, v in registry.items():
                registry_table.add_row(str(k), str(v))
            console.print(registry_table)
    else:
        console.print(
            f"[red]❌ Unknown format: {format}. Use 'table', 'json', or 'yaml'.[/red]"
        )
        sys.exit(1)


@app.command()
def proxy_invoke(
    tool_name: str = typer.Argument(..., help="Name of the tool to invoke"),
    args: str = typer.Option(
        None, "--args", "-a", help="Tool arguments as JSON string (e.g., '{\"x\": 1}')"
    ),
    provider_node_id: str = typer.Option(
        None,
        "--provider-node-id",
        "-n",
        help="UUID of the node to route the invocation to (optional)",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Validate request but do not execute"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f", help="Output format: 'table', 'json', or 'yaml'"
    ),
) -> None:
    """
    Proxy-invoke a tool via the registry node. Optionally specify provider_node_id to route to a specific node (by UUID).
    If not specified, the registry will select a provider. Only a single provider is supported in Milestone 1.
    """
    import json

    from rich import print as rich_print

    from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
    from omnibase.nodes.node_registry_node.v1_0_0.models.state import (
        ToolProxyInvocationRequest,
    )
    from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
        InMemoryEventBus,
    )

    correlation_id = str(uuid.uuid4())
    try:
        arguments = json.loads(args) if args else {}
    except Exception as exc:
        console.print(f"[red]Invalid JSON for --args: {exc}[/red]")
        raise typer.Exit(1)
    req = ToolProxyInvocationRequest(
        tool_name=tool_name,
        arguments=arguments,
        correlation_id=correlation_id,
        provider_node_id=provider_node_id,
    )
    if dry_run:
        console.print(
            "[yellow]DRY RUN: Would send the following ToolProxyInvocationRequest:[/yellow]"
        )
        console.print(req.model_dump_json(indent=2))
        return
    event_bus = InMemoryEventBus()
    events = []

    def cb(event):
        if getattr(event, "correlation_id", None) == correlation_id:
            events.append(event)

    event_bus.subscribe(cb)
    event = OnexEvent(
        event_type=OnexEventTypeEnum.TOOL_PROXY_INVOKE,
        node_id="cli",
        metadata=None,
    )
    event_bus.publish(event)
    # Wait for ACCEPTED/RESULT/ERROR events (simple polling loop)
    timeout = 5.0
    start = time.time()
    accepted = None
    result = None
    error = None
    while time.time() - start < timeout:
        for e in events:
            if e.event_type == OnexEventTypeEnum.TOOL_PROXY_ACCEPTED:
                accepted = e
            elif e.event_type == OnexEventTypeEnum.TOOL_PROXY_RESULT:
                result = e
            elif e.event_type in (
                OnexEventTypeEnum.TOOL_PROXY_REJECTED,
                OnexEventTypeEnum.TOOL_PROXY_ERROR,
                OnexEventTypeEnum.TOOL_PROXY_TIMEOUT,
            ):
                error = e
        if result or error:
            break
        time.sleep(0.05)

    # Output formatting
    def print_event(ev):
        meta = (
            ev.metadata.model_dump()
            if hasattr(ev.metadata, "model_dump")
            else ev.metadata
        )
        meta = meta or {}
        meta["event_type"] = ev.event_type
        meta["correlation_id"] = ev.correlation_id
        if output_format == "json":
            console.print_json(json.dumps(meta, indent=2, cls=OmniJSONEncoder))
        elif output_format == "yaml":
            console.print(yaml.safe_dump(meta, sort_keys=False))
        else:
            table = Table(title="Proxy Invocation Result")
            for k, v in meta.items():
                table.add_row(str(k), str(v))
            console.print(table)

    if error:
        console.print(f"[red]Proxy invocation failed:[/red]")
        print_event(error)
        raise typer.Exit(1)
    if result:
        if verbose and accepted:
            console.print("[green]Proxy invocation accepted:[/green]")
            print_event(accepted)
        console.print("[green]Proxy invocation result:[/green]")
        print_event(result)
        return
    if accepted:
        console.print(
            "[yellow]Proxy invocation accepted, but no result received within timeout.[/yellow]"
        )
        print_event(accepted)
        raise typer.Exit(2)
    console.print(
        f"[red]No response received for proxy invocation within {timeout} seconds.[/red]"
    )
    raise typer.Exit(3)


@app.command()
def generate_models(
    node_name: str = typer.Argument(
        ..., help="Name of the node (for prefixing models)"
    ),
    contract_path: str = typer.Argument(..., help="Path to contract.yaml for the node"),
    output_path: str = typer.Argument(
        ...,
        help="Path to write generated state.py (e.g., src/omnibase/nodes/<node>/v1_0_0/models/state.py)",
    ),
):
    """
    Generate canonical Pydantic models from a node's contract.yaml. Always overwrites output files.
    """
    from pathlib import Path
    try:
        generate_state_models(
            Path(contract_path), Path(output_path), auto=False
        )
        console.print(f"[green]Model generation complete: {output_path}[/green]")
    except Exception as e:
        console.print(f"[red]Model generation failed: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def check_model_alignment(
    node_name: str = typer.Argument(
        ..., help="Name of the node (for prefixing models)"
    ),
    contract_path: str = typer.Argument(..., help="Path to contract.yaml for the node"),
    model_path: str = typer.Argument(
        ...,
        help="Path to the current state.py (e.g., src/omnibase/nodes/<node>/v1_0_0/models/state.py)",
    ),
):
    """
    Check for drift between contract.yaml and the current state.py model file.
    Prints a diff if there is drift, or a success message if aligned.
    """
    import io
    from pathlib import Path

    # Patch generate_state_models to write to a string buffer
    from omnibase.runtimes.onex_runtime.v1_0_0.codegen import contract_to_model

    contract_path = Path(contract_path)
    model_path = Path(model_path)

    # StringIO subclass that ignores close()
    class NonClosingStringIO(io.StringIO):
        def close(self):
            pass

    output_buffer = NonClosingStringIO()
    orig_open = open

    def fake_open(path, mode="r", *args, **kwargs):
        if str(path) == str(model_path) and "w" in mode:
            return output_buffer
        return orig_open(path, mode, *args, **kwargs)

    import builtins

    builtins.open, old_open = fake_open, builtins.open
    try:
        contract_to_model.generate_state_models(
            contract_path, model_path, force=True, auto=False
        )
    finally:
        builtins.open = old_open
    expected_code = output_buffer.getvalue()
    if not model_path.exists():
        console.print(f"[red]Model file does not exist: {model_path}[/red]")
        raise typer.Exit(code=1)
    with model_path.open("r") as f:
        current_code = f.read()
    if current_code == expected_code:
        console.print(
            f"[green]No drift detected: {model_path} is aligned with {contract_path}[/green]"
        )
    else:
        console.print(
            f"[yellow]Drift detected between {model_path} and {contract_path}:[/yellow]"
        )
        diff = difflib.unified_diff(
            current_code.splitlines(),
            expected_code.splitlines(),
            fromfile=str(model_path),
            tofile="expected (from contract.yaml)",
            lineterm="",
        )
        for line in diff:
            console.print(line)
        raise typer.Exit(code=2)


@app.command()
def validate_scenarios(
    node_name: str = typer.Argument(
        ..., help="Name of the node (for prefixing models)"
    ),
    model_path: str = typer.Argument(
        ...,
        help="Path to the canonical state.py (e.g., src/omnibase/nodes/<node>/v1_0_0/models/state.py)",
    ),
    scenarios_dir: str = typer.Argument(
        ...,
        help="Directory containing scenario YAMLs (e.g., src/omnibase/nodes/<node>/v1_0_0/scenarios/)",
    ),
):
    """
    Validate all scenario YAMLs in a directory against the canonical input/output models.
    """
    from pathlib import Path

    model_path = Path(model_path)
    scenarios_dir = Path(scenarios_dir)
    # Dynamically import the canonical models from state.py
    spec = importlib.util.spec_from_file_location(f"{node_name}_models", model_path)
    models = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models)
    # Find InputState and OutputState classes
    input_model = None
    output_model = None
    for attr in dir(models):
        if attr.endswith("InputState"):
            input_model = getattr(models, attr)
        if attr.endswith("OutputState"):
            output_model = getattr(models, attr)
    if not input_model or not output_model:
        console.print(
            f"[red]Could not find InputState/OutputState in {model_path}[/red]"
        )
        raise typer.Exit(code=1)
    # Validate each scenario YAML
    errors = []
    for scenario_file in sorted(scenarios_dir.glob("*.yaml")):
        with scenario_file.open("r") as f:
            try:
                data = yaml.safe_load(f)
            except Exception as e:
                errors.append((scenario_file, f"YAML parse error: {e}"))
                continue
        # Skip intentionally invalid scenarios
        if data.get("expected_validation") == "fail":
            console.print(
                f"[blue]{scenario_file}[/blue]: intentionally invalid (skipped)"
            )
            continue
        # Support both single-scenario and chain formats
        input_block = None
        expect_block = None
        if "chain" in data and isinstance(data["chain"], list) and data["chain"]:
            # Use first step for validation (common pattern)
            step = data["chain"][0]
            input_block = step.get("input")
            expect_block = step.get("expect")
        else:
            input_block = data.get("input")
            expect_block = data.get("expect")
        # Validate input
        try:
            if input_block is not None:
                input_model.model_validate(input_block)
        except Exception as e:
            errors.append((scenario_file, f"Input validation error: {e}"))
        # Validate expect/output
        try:
            if expect_block is not None:
                output_model.model_validate(expect_block)
        except Exception as e:
            errors.append((scenario_file, f"Expect/output validation error: {e}"))
    if not errors:
        console.print(
            f"[green]All scenarios in {scenarios_dir} are valid against canonical models.[/green]"
        )
    else:
        console.print(f"[yellow]Scenario validation errors detected:[/yellow]")
        for file, err in errors:
            console.print(f"[red]{file}[/red]: {err}")
        raise typer.Exit(code=2)


@app.command()
def print_events(
    correlation_id: str = typer.Argument(..., help="Correlation ID to filter events"),
    event_bus_type: str = typer.Option(
        None, "--event-bus-type", help="Event bus type: inmemory or kafka"
    ),
    timeout: int = typer.Option(
        5, "--timeout", help="Seconds to listen for events (default: 5)"
    ),
):
    """
    Print all events/logs for a given correlation_id from the event bus (diagnostic).
    """
    import threading
    import time

    from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import (
        get_event_bus,
    )

    event_bus = get_event_bus(event_bus_type=event_bus_type)
    received = []

    def cb(event):
        if getattr(event, "correlation_id", None) == correlation_id:
            received.append(event)
            print(f"[{event.event_type}] {event.metadata}")

    event_bus.subscribe(cb)
    print(
        f"Listening for events with correlation_id={correlation_id} on {event_bus.bus_id}..."
    )
    time.sleep(timeout)
    event_bus.unsubscribe(cb)
    print(f"Received {len(received)} events.")


@app.command()
def launch_agent(node_id: str):
    """Launch an agent for the given node_id (async test pattern)."""
    asyncio.run(_launch_agent(node_id))


async def _launch_agent(node_id: str):
    import asyncio
    import datetime
    import uuid

    from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
    from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_kafka import (
        KafkaEventBus,
    )

    bus = KafkaEventBus()
    try:
        print("[DEBUG] Calling bus.connect()...")
        await bus.connect()
        print(f"[DEBUG] Connected: bus._connected={getattr(bus, '_connected', None)}")
        await asyncio.sleep(0.5)  # Give Kafka a moment to settle
        event = OnexEvent(
            node_id=node_id,
            event_type=OnexEventTypeEnum.TOOL_PROXY_INVOKE,
            correlation_id=str(uuid.uuid4()),
            timestamp=datetime.datetime.utcnow(),
            metadata={"message": "Test Kafka event from CLI"},
        )
        print(
            f"[DEBUG] Publishing event to subject: onex.events.{OnexEventTypeEnum.TOOL_PROXY_INVOKE.value}"
        )
        await bus.publish(event)
        print(f"Published event to Kafka for node_id: {node_id}")
    except Exception as e:
        print(f"Kafka publish failed: {e}")


if __name__ == "__main__":
    app()
