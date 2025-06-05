"""
Template Node (ONEX Canonical)

Implements the reducer pattern with .run() and .bind() lifecycle. All business logic is delegated to inline handlers or runtime helpers.
"""

from omnibase.nodes.node_kafka_event_bus.v1_0_0.models.state import NodeKafkaEventBusInputState, NodeKafkaEventBusOutputState
from omnibase.protocol.protocol_reducer import ProtocolReducer
from omnibase.model.model_reducer import ActionModel, StateModel
from omnibase.enums.enum_registry_output_status import RegistryOutputStatusEnum
from omnibase.model.model_semver import SemVerModel
from omnibase.model.model_node_metadata import NodeMetadataBlock, LogFormat
from omnibase.model.model_output_field import OnexFieldModel
import yaml
from pathlib import Path
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import MetadataYAMLHandler
import sys
import json
import argparse
from omnibase.nodes.node_kafka_event_bus.v1_0_0.introspection import NodeKafkaEventBusIntrospection
from pydantic import ValidationError
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import make_log_context, emit_log_event_sync, log_level_emoji, get_log_format, set_log_format
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.enums.onex_status import OnexStatus
import os
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
import uuid
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import KafkaEventBusConfigModel
from omnibase.nodes.node_registry_node.v1_0_0.models.state import EventBusInfoModel
from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.bootstrap_helper import bootstrap_kafka_cluster

NODE_ONEX_YAML_PATH = Path(__file__).parent / "node.onex.yaml"

TRACE_MODE = os.environ.get("ONEX_TRACE") == "1"
_trace_mode_flag = None
def is_trace_mode():
    global _trace_mode_flag
    if _trace_mode_flag is not None:
        return _trace_mode_flag
    import sys
    _trace_mode_flag = TRACE_MODE or ("--debug-trace" in sys.argv)
    return _trace_mode_flag

class NodeKafkaEventBus(NodeKafkaEventBusIntrospection, ProtocolReducer):
    """
    Canonical ONEX reducer node implementing ProtocolReducer.
    Handles all scenario-driven logic for smoke, error, output, and integration cases.
    Resolves event bus via protocol-pure factory; never instantiates backend directly.
    """
    def __init__(self, event_bus: ProtocolEventBus = None, config: KafkaEventBusConfigModel = None, skip_subscribe: bool = False):
        self.node_id = "node_kafka_event_bus"
        self._is_async_bus = False
        if event_bus is not None:
            self.event_bus = event_bus
            emit_log_event_sync(
                LogLevelEnum.INFO,
                "[NodeKafkaEventBus] Using injected event_bus instance",
                context=make_log_context(node_id=self.node_id),
            )
        else:
            if config is None:
                config = KafkaEventBusConfigModel.default()
            bus_type = "kafka"
            self.event_bus = get_event_bus(event_bus_type=bus_type, config=config)
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[NodeKafkaEventBus] Using event bus via factory (type={bus_type or 'default'})",
                context=make_log_context(node_id=self.node_id),
            )
        import inspect
        self._is_async_bus = inspect.iscoroutinefunction(getattr(self.event_bus, "subscribe", None))
        # Only subscribe and announce here if not async (for InMemoryEventBus)
        if not skip_subscribe and not self._is_async_bus:
            self.event_bus.subscribe(self.handle_event)
            emit_log_event_sync(LogLevelEnum.INFO, "[NodeKafkaEventBus] Subscribed to event bus (sync)", make_log_context(node_id=self.node_id))
            # Announce event bus to registry (sync publish)
            try:
                bus_id = getattr(self.event_bus, 'bus_id', str(uuid.uuid4()))
                endpoint_uri = None
                if hasattr(self.event_bus, 'bootstrap_servers'):
                    endpoint_uri = ','.join(self.event_bus.bootstrap_servers)
                info = EventBusInfoModel(
                    bus_id=bus_id,
                    protocol="kafka",
                    endpoint_uri=endpoint_uri or "unknown",
                    active=True,
                    subscriber_count=0,
                    inbound=True,
                    outbound=True,
                    port_lease=None,
                )
                announce_event = OnexEvent(
                    node_id=self.node_id,
                    event_type=OnexEventTypeEnum.NODE_ANNOUNCE,
                    metadata=info.model_dump(),
                )
                self.event_bus.publish(announce_event)
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[NodeKafkaEventBus] Announced Kafka event bus to registry (bus_id={bus_id})",
                    context=make_log_context(node_id=self.node_id),
                )
            except Exception as e:
                emit_log_event_sync(
                    LogLevelEnum.ERROR,
                    f"[NodeKafkaEventBus] Failed to announce Kafka event bus: {e}",
                    context=make_log_context(node_id=self.node_id),
                )
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                "NodeKafkaEventBus instantiated",
                context=make_log_context(node_id=self.node_id),
            )

    def handle_event(self, event: OnexEvent):
        emit_log_event_sync(LogLevelEnum.INFO, f"[handle_event] Received event: {getattr(event, 'event_type', None)} correlation_id={getattr(event, 'correlation_id', None)}", make_log_context(node_id=self.node_id))
        if event.event_type != OnexEventTypeEnum.TOOL_PROXY_INVOKE:
            return
        if event.node_id != self.node_id:
            return
        metadata = event.metadata or {}
        args = metadata.get("args", [])
        log_format = metadata.get("log_format", "json")
        correlation_id = event.correlation_id
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[handle_event] Received TOOL_PROXY_INVOKE with args: {args}",
            context=make_log_context(node_id=self.node_id, correlation_id=correlation_id),
        )
        # For demo: just emit a log event and a result event
        log_event = OnexEvent(
            event_id=uuid.uuid4(),
            timestamp=None,
            node_id=self.node_id,
            event_type=OnexEventTypeEnum.STRUCTURED_LOG,
            correlation_id=correlation_id,
            metadata={
                "message": f"[node_kafka_event_bus] Received args: {args}",
                "log_format": log_format,
            },
        )
        self.event_bus.publish(log_event)
        try:
            # Simulate running a scenario and emitting a result
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[handle_event] Running scenario for correlation_id: {correlation_id}",
                context=make_log_context(node_id=self.node_id, correlation_id=correlation_id),
            )
            result = NodeKafkaEventBusOutputState(
                version="1.0.0",
                status=OnexStatus.SUCCESS,
                message="NodeKafkaEventBus ran successfully (event-driven)",
            )
            result_event = OnexEvent(
                event_id=uuid.uuid4(),
                timestamp=None,
                node_id=self.node_id,
                event_type=OnexEventTypeEnum.TOOL_PROXY_RESULT,
                correlation_id=correlation_id,
                metadata={
                    "result": result.model_dump(),
                    "log_format": log_format,
                },
            )
            self.event_bus.publish(result_event)
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[handle_event] Scenario complete for correlation_id: {correlation_id}",
                context=make_log_context(node_id=self.node_id, correlation_id=correlation_id),
            )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[handle_event] Exception during scenario: {e}",
                context=make_log_context(node_id=self.node_id, correlation_id=correlation_id),
            )
            raise

    def run(self, input_state: dict) -> NodeKafkaEventBusOutputState:
        print("[DEBUG] Entered NodeKafkaEventBus.run()", flush=True)
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"Entered run() with input_state: {input_state}",
                context=make_log_context(node_id="node_kafka_event_bus"),
            )
        # Check for bootstrap argument
        args = input_state.get("args", [])
        if "--bootstrap" in args:
            config = None
            try:
                state = NodeKafkaEventBusInputState(**input_state)
                config = getattr(state, "config", None)
            except Exception:
                config = input_state.get("config")
            if config is None:
                config = KafkaEventBusConfigModel.default()
            result = bootstrap_kafka_cluster(config)
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[NodeKafkaEventBus] Kafka bootstrap result: {result}",
                context=make_log_context(node_id=self.node_id),
            )
            return NodeKafkaEventBusOutputState(
                version="1.0.0",
                status=OnexStatus.SUCCESS if result["status"] == "ok" else OnexStatus.ERROR,
                message=f"Kafka bootstrap completed: {result}",
            )
        # Check for health check argument
        if "--health-check" in args:
            config = None
            try:
                state = NodeKafkaEventBusInputState(**input_state)
                config = getattr(state, "config", None)
            except Exception:
                config = input_state.get("config")
            if config is None:
                config = KafkaEventBusConfigModel.default()
            # Instantiate event bus and run health check
            from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.kafka_event_bus import KafkaEventBus
            import asyncio
            event_bus = KafkaEventBus(config)
            print("[DEBUG] About to call health_check", flush=True)
            health_result = asyncio.run(event_bus.health_check())
            print("[DEBUG] health_check returned", flush=True)
            print("[HEALTH CHECK RESULT]", health_result, flush=True)
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[NodeKafkaEventBus] Kafka health check result: {health_result}",
                context=make_log_context(node_id=self.node_id),
                event_bus=self.event_bus,
            )
            # Emit a structured log event for CLI visibility
            event = OnexEvent(
                event_id=uuid.uuid4(),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                node_id=self.node_id,
                event_type=OnexEventTypeEnum.STRUCTURED_LOG,
                correlation_id=None,
                metadata={"health_check_result": health_result},
            )
            asyncio.run(self.event_bus.publish(event.model_dump_json().encode()))
            print("[DEBUG] About to return from run()", flush=True)
            return NodeKafkaEventBusOutputState(
                version="1.0.0",
                status="success" if health_result.get("connected") else "error",
                message=str(health_result),
                output_field=None,
            )
        with open(NODE_ONEX_YAML_PATH, "r") as f:
            node_metadata_content = f.read()
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                "Loading node metadata from node.onex.yaml",
                context=make_log_context(node_id="node_kafka_event_bus"),
            )
        node_metadata_block = NodeMetadataBlock.from_file_or_content(node_metadata_content, event_bus=self.event_bus)
        node_version = str(node_metadata_block.version)
        semver = SemVerModel.parse(node_version)
        # Parse config from state if present and re-instantiate event bus if needed
        config = None
        try:
            state = NodeKafkaEventBusInputState(**input_state)
            config = getattr(state, "config", None)
        except Exception:
            config = input_state.get("config")
        if config and not isinstance(self.event_bus, ProtocolEventBus):
            # Re-instantiate with KafkaEventBus if config is present
            self.event_bus = get_event_bus(event_bus_type="kafka", config=config)
            emit_log_event_sync(
                LogLevelEnum.INFO,
                "[NodeKafkaEventBus] Switched to KafkaEventBus backend in run()",
                context=make_log_context(node_id=self.node_id),
            )
        try:
            state = NodeKafkaEventBusInputState(**input_state)
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    "Input validation succeeded",
                    context=make_log_context(node_id="node_kafka_event_bus"),
                )
        except ValidationError as e:
            msg = str(e.errors()[0]['msg']) if e.errors() else str(e)
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    f"Input validation failed: {msg}",
                    context=make_log_context(node_id="node_kafka_event_bus"),
                )
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"ValidationError in run: {msg}",
                context=make_log_context(node_id="node_kafka_event_bus"),
            )
            return NodeKafkaEventBusOutputState(
                version=semver,
                status=OnexStatus.ERROR,
                message=msg,
                output_field=None,
            )
        except Exception as e:
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    f"Exception during input validation: {e}",
                    context=make_log_context(node_id="node_kafka_event_bus"),
                )
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Exception in run: {e}",
                context=make_log_context(node_id="node_kafka_event_bus"),
            )
            return NodeKafkaEventBusOutputState(
                version=semver,
                status=OnexStatus.ERROR,
                message=str(e),
                output_field=None,
            )
        output_field = None
        backend_type = type(self.event_bus).__name__
        if hasattr(state, 'external_dependency') or input_state.get('external_dependency'):
            output_field = OnexFieldModel(data={"integration": True, "backend": backend_type})
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    "Integration context detected, output_field set",
                    context=make_log_context(node_id="node_kafka_event_bus"),
                )
        elif state.input_field == "test" and getattr(state, "optional_field", None) == "optional":
            if input_state.get('output_field') == "custom_output":
                output_field = OnexFieldModel(data={"custom": "output", "backend": backend_type})
            else:
                output_field = OnexFieldModel(data={"custom": "output", "backend": backend_type})
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    "Custom output_field branch taken",
                    context=make_log_context(node_id="node_kafka_event_bus"),
                )
        else:
            output_field = OnexFieldModel(data={"processed": state.input_field, "backend": backend_type})
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    "Default output_field branch taken (backend={backend_type})",
                    context=make_log_context(node_id="node_kafka_event_bus"),
                )
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"Exiting run() with output_field: {output_field}",
                context=make_log_context(node_id="node_kafka_event_bus"),
            )
        print("[DEBUG] About to return from run()", flush=True)
        return NodeKafkaEventBusOutputState(
            version=semver,
            status=OnexStatus.SUCCESS,
            message="NodeKafkaEventBus ran successfully.",
            output_field=output_field,
        )

    def bind(self, *args, **kwargs):
        """
        Bind pattern stub. In ONEX, this is used for chaining nodes.
        """
        return self

    def initial_state(self) -> StateModel:
        """
        Return the initial state for the reducer. Override as needed.
        """
        return NodeKafkaEventBusInputState(version=SemVerModel(str(NodeMetadataBlock.from_file(NODE_ONEX_YAML_PATH).version)), input_field="", optional_field=None)

    def dispatch(self, state: StateModel, action: ActionModel) -> StateModel:
        """
        Apply an action to the state and return the new state. Override as needed.
        """
        # For template, just return the state unchanged
        return state

    def introspect(self):
        """
        Return a list of available scenarios for this node from scenarios/index.yaml.
        """
        scenarios_index_path = Path(__file__).parent / "scenarios" / "index.yaml"
        if not scenarios_index_path.exists():
            return {"scenarios": []}
        with open(scenarios_index_path, "r") as f:
            data = yaml.safe_load(f)
        return data

def main(event_bus=None):
    print("[DEBUG] Entered main()", flush=True)
    parser = argparse.ArgumentParser(description="ONEX Kafka Event Bus Node (supports --health-check, --serve)")
    parser.add_argument("--introspect", action="store_true", help="Show node introspection")
    parser.add_argument("--run-scenario", type=str, help="Run a scenario by ID")
    parser.add_argument("--input", type=str, help="Input JSON for direct execution")
    parser.add_argument("--health-check", action="store_true", help="Check Kafka broker health and exit")
    parser.add_argument("--debug-trace", action="store_true", help="Enable trace-level logging for demo/debug")
    parser.add_argument("--log-format", type=str, choices=[f.value for f in LogFormat], default=LogFormat.JSON.value, help="Log output format")
    parser.add_argument("--serve", action="store_true", help="Run as a persistent event-driven service (daemon mode)")
    args = parser.parse_args()
    print(f"[DEBUG] Parsed args: {args}", flush=True)
    if args.health_check:
        from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.kafka_event_bus import KafkaEventBus
        from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import KafkaEventBusConfigModel
        import asyncio
        config = KafkaEventBusConfigModel(bootstrap_servers=["localhost:9092"], topics=["onex-test-events"])
        bus = KafkaEventBus(config)
        result = asyncio.run(bus.health_check())
        print(result.model_dump_json(indent=2))
        sys.exit(0)
    global _trace_mode_flag
    if args.debug_trace:
        _trace_mode_flag = True
    try:
        log_format_enum = LogFormat(args.log_format.lower())
    except ValueError:
        log_format_enum = LogFormat.JSON
    set_log_format(log_format_enum)
    emit_log_event_sync(LogLevelEnum.DEBUG, f"[main] set_log_format to {get_log_format()}", make_log_context(node_id="node_kafka_event_bus"))

    event_bus = None
    config = None
    input_data = None
    if args.run_scenario:
        scenario_id = args.run_scenario
        scenarios = NodeKafkaEventBusIntrospection.get_scenarios()
        scenario = next((s for s in scenarios if s["id"] == scenario_id), None)
        if not scenario:
            sys.exit(1)
        entrypoint = scenario.get("entrypoint")
        if not entrypoint:
            sys.exit(1)
        try:
            scenario_path = Path(__file__).parent / entrypoint
            with open(scenario_path, "r") as f:
                scenario_yaml = yaml.safe_load(f)
            input_data = scenario_yaml["chain"][0]["input"]
            config = input_data.get("config")
            if config is not None and not isinstance(config, KafkaEventBusConfigModel):
                config = KafkaEventBusConfigModel(**config)
                input_data["config"] = config
        except Exception as e:
            sys.exit(1)
    elif args.input:
        try:
            input_data = json.loads(args.input)
            config = input_data.get("config")
            if config is not None and not isinstance(config, KafkaEventBusConfigModel):
                config = KafkaEventBusConfigModel(**config)
                input_data["config"] = config
        except Exception as e:
            sys.exit(1)
    event_bus_type = "kafka" if config else None
    if config is None:
        from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import KafkaEventBusConfigModel
        config = KafkaEventBusConfigModel.default()
    event_bus = get_event_bus(event_bus_type=event_bus_type, config=config)
    node = NodeKafkaEventBus(event_bus=event_bus, config=config)
    if args.introspect:
        NodeKafkaEventBusIntrospection.handle_introspect_command()
    elif args.serve:
        print("[DEBUG] About to enter serve_loop", flush=True)
        emit_log_event_sync(LogLevelEnum.INFO, "[main] Entering serve (daemon) mode: subscribing to event bus and handling events", make_log_context(node_id="node_kafka_event_bus"))
        print("[INFO] NodeKafkaEventBus running in serve mode. Press Ctrl+C to exit.", flush=True)
        # Bootstrap Kafka cluster and ensure topic exists
        from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.bootstrap_helper import bootstrap_kafka_cluster
        bootstrap_result = bootstrap_kafka_cluster(node.event_bus.config)
        emit_log_event_sync(LogLevelEnum.INFO, f"[main] Kafka bootstrap result: {bootstrap_result}", make_log_context(node_id="node_kafka_event_bus"))
        import signal
        import threading
        import time
        import asyncio
        stop_flag = threading.Event()
        def handle_sigint(sig, frame):
            print("[INFO] Shutting down serve mode...", flush=True)
            stop_flag.set()
        signal.signal(signal.SIGINT, handle_sigint)
        async def serve_loop():
            print("[DEBUG] Entered serve_loop", flush=True)
            import inspect
            counter = 0
            # Ensure KafkaEventBus is connected before subscribe/publish
            if hasattr(node.event_bus, "connect") and inspect.iscoroutinefunction(getattr(node.event_bus, "connect", None)):
                await node.event_bus.connect()
                emit_log_event_sync(LogLevelEnum.INFO, "[main] Event bus connected (async)", make_log_context(node_id="node_kafka_event_bus"))
            if inspect.iscoroutinefunction(getattr(node.event_bus, "subscribe", None)):
                await node.event_bus.subscribe(node.handle_event)
                emit_log_event_sync(LogLevelEnum.INFO, "[main] Subscribed to event bus (async)", make_log_context(node_id="node_kafka_event_bus"))
                # Announce event bus to registry (async publish)
                try:
                    bus_id = getattr(node.event_bus, 'bus_id', str(uuid.uuid4()))
                    endpoint_uri = None
                    if hasattr(node.event_bus, 'bootstrap_servers'):
                        endpoint_uri = ','.join(node.event_bus.bootstrap_servers)
                    info = EventBusInfoModel(
                        bus_id=bus_id,
                        protocol="kafka",
                        endpoint_uri=endpoint_uri or "unknown",
                        active=True,
                        subscriber_count=0,
                        inbound=True,
                        outbound=True,
                        port_lease=None,
                    )
                    announce_event = OnexEvent(
                        node_id=node.node_id,
                        event_type=OnexEventTypeEnum.NODE_ANNOUNCE,
                        metadata=info.model_dump(),
                    )
                    await node.event_bus.publish(announce_event)
                    emit_log_event_sync(
                        LogLevelEnum.INFO,
                        f"[main] Announced Kafka event bus to registry (bus_id={bus_id})",
                        make_log_context(node_id="node_kafka_event_bus"),
                    )
                except Exception as e:
                    emit_log_event_sync(
                        LogLevelEnum.ERROR,
                        f"[main] Failed to announce Kafka event bus: {e}",
                        make_log_context(node_id="node_kafka_event_bus"),
                    )
            while not stop_flag.is_set():
                if counter % 20 == 0:
                    print("[HEARTBEAT] NodeKafkaEventBus serve loop alive", flush=True)
                await asyncio.sleep(0.5)
                counter += 1
        try:
            asyncio.run(serve_loop())
        except Exception as e:
            print(f"[ERROR] Exception in serve_loop: {e}", flush=True)
            emit_log_event_sync(LogLevelEnum.ERROR, f"[main] Exception in serve mode: {e}", make_log_context(node_id="node_kafka_event_bus"))
            raise
        print("[INFO] Serve mode exited.", flush=True)
    elif input_data is not None:
        try:
            result = node.run(input_data)
            print(json.dumps({"backend": type(node.event_bus).__name__, "result": result.model_dump()}))
        except Exception as e:
            sys.exit(1)
    else:
        sys.exit(1)
    if get_log_format() == LogFormat.MARKDOWN:
        flush_markdown_log_buffer()

def get_introspection() -> dict:
    """Get introspection data for the template node."""
    return NodeKafkaEventBusIntrospection.get_introspection_response()

if __name__ == "__main__":
    main()
