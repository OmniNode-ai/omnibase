import argparse
import asyncio
import os
import signal
import sys
from pathlib import Path

from omnibase.nodes.node_kafka_event_bus.v1_0_0.node import NodeKafkaEventBus
from omnibase.tools.tool_bootstrap import tool_bootstrap
from omnibase.tools.tool_health_check import tool_health_check
from omnibase.tools.tool_compute_output_field import tool_compute_output_field
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models.state import NodeKafkaEventBusNodeInputState, NodeKafkaEventBusNodeOutputState, ModelEventBusOutputField
from omnibase.tools.tool_input_validation import ToolInputValidation
from omnibase.nodes.node_kafka_event_bus.v1_0_0.registry.registry_kafka_event_bus import RegistryKafkaEventBus
from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_backend_selection import ToolBackendSelection
from omnibase.model.model_event_bus_config import ModelEventBusConfig
from omnibase.runtimes.onex_runtime.v1_0_0.tools.tool_registry_resolver import registry_resolver_tool
from omnibase.nodes.node_kafka_event_bus.constants import NODE_KAFKA_EVENT_BUS_ID
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync, make_log_context
from omnibase.enums.log_level import LogLevelEnum

PID_FILE = Path(__file__).parent / "kafka_node_daemon.pid"


def write_pid():
    PID_FILE.write_text(str(os.getpid()))

def read_pid():
    if PID_FILE.exists():
        return int(PID_FILE.read_text().strip())
    return None

def remove_pid():
    if PID_FILE.exists():
        PID_FILE.unlink()

def stop_daemon():
    pid = read_pid()
    if not pid:
        print("[ERROR] No running daemon found (no PID file).")
        sys.exit(1)
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"[INFO] Sent SIGTERM to daemon process (PID {pid}).")
        remove_pid()
    except ProcessLookupError:
        print(f"[WARNING] No process found with PID {pid}. Removing stale PID file.")
        remove_pid()
    except Exception as e:
        print(f"[ERROR] Failed to stop daemon: {e}")
        sys.exit(1)
    print("[INFO] Daemon stopped.")
    sys.exit(0)

async def run_daemon():
    emit_log_event_sync(
        "INFO",
        "[daemon] Starting ONEX Kafka node daemon and injecting canonical tools...",
        make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
    )
    write_pid()
    # Canonical registry and tool injection
    config = ModelEventBusConfig.default()
    print(f"[DAEMON] Kafka config: {config.model_dump_json(indent=2)}")
    emit_log_event_sync(
        "DEBUG",
        f"[daemon] Kafka config: {config.model_dump_json(indent=2)}",
        make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
    )
    node_dir = Path(__file__).parent
    emit_log_event_sync(
        "DEBUG",
        f"[daemon] Using node_dir for registry: {node_dir}",
        make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
    )
    registry = RegistryKafkaEventBus(node_dir=node_dir)
    emit_log_event_sync(
        "DEBUG",
        f"[daemon] Registry instantiated with node_dir: {registry.node_dir}",
        make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
    )
    tool_backend_selection = ToolBackendSelection(registry)
    input_validation_tool = ToolInputValidation(
        input_model=NodeKafkaEventBusNodeInputState,
        output_model=NodeKafkaEventBusNodeOutputState,
        output_field_model=ModelEventBusOutputField,
        node_id=NODE_KAFKA_EVENT_BUS_ID,
    )
    node = NodeKafkaEventBus(
        tool_bootstrap=tool_bootstrap,
        tool_backend_selection=tool_backend_selection,
        tool_health_check=tool_health_check,
        input_validation_tool=input_validation_tool,
        output_field_tool=tool_compute_output_field,
        config=config,
        registry=registry,
        registry_resolver=registry_resolver_tool,
    )
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    def handle_signal(sig, frame=None):
        print(f"[INFO] Received signal {sig.name}, shutting down daemon...")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_signal, sig)
        except NotImplementedError:
            # Windows compatibility
            signal.signal(sig, handle_signal)

    try:
        # Explicitly connect the event bus before serving
        emit_log_event_sync(
            "DEBUG",
            "[daemon] Calling event_bus.connect() before serve_until...",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
        )
        await node.event_bus.connect()
        emit_log_event_sync(
            "DEBUG",
            "[daemon] event_bus.connect() completed.",
            make_log_context(node_id=NODE_KAFKA_EVENT_BUS_ID)
        )
        await node.serve_until(stop_event)
    finally:
        remove_pid()
        print("[INFO] ONEX Kafka node daemon stopped.")


def main():
    parser = argparse.ArgumentParser(description="ONEX Kafka Node Daemon")
    parser.add_argument("--stop", action="store_true", help="Stop the running daemon")
    args = parser.parse_args()

    if args.stop:
        stop_daemon()
    else:
        try:
            print("[DAEMON] Starting Kafka event bus daemon...")
            asyncio.run(run_daemon())
        except KeyboardInterrupt:
            print("[INFO] KeyboardInterrupt received, shutting down daemon...")
        except Exception as e:
            print(f"[ERROR] Daemon crashed: {e}")
            remove_pid()
            sys.exit(1)

if __name__ == "__main__":
    main() 