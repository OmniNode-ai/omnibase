"""
Node Manager Node (ONEX Canonical)

Implements the reducer pattern with .run() and .bind() lifecycle. All business logic is delegated to protocol-typed helpers or runtime tools.
"""

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
import datetime
from datetime import timezone

import yaml
from pydantic import ValidationError

from omnibase.enums.enum_registry_output_status import RegistryOutputStatusEnum
from omnibase.enums.log_level import LogLevelEnum
from omnibase.enums.onex_status import OnexStatus
from omnibase.model.model_node_metadata import LogFormat, NodeMetadataBlock
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.model.model_output_field import OnexFieldModel
from omnibase.model.model_reducer import ActionModel, StateModel
from omnibase.model.model_semver import SemVerModel
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
from omnibase.protocol.protocol_reducer import ProtocolReducer
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import (
    MetadataYAMLHandler,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import (
    emit_log_event_sync,
    get_log_format,
    log_level_emoji,
    make_log_context,
    set_log_format,
)
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus

from .introspection import NodeManagerIntrospection
from .models.state import NodeManagerInputState, NodeManagerOutputState, ModelNodeManagerOutputField
from omnibase.nodes.node_manager.protocols.input_validation_tool_protocol import InputValidationToolProtocol
from omnibase.nodes.node_manager.protocols.output_field_tool_protocol import OutputFieldTool as OutputFieldToolProtocol
from omnibase.runtimes.onex_runtime.v1_0_0.protocol.tool_scenario_runner_protocol import ToolScenarioRunnerProtocol
from omnibase.runtimes.onex_runtime.v1_0_0.tools.tool_scenario_runner import ToolScenarioRunner
from omnibase.tools.tool_input_validation import ToolInputValidation
from omnibase.tools.tool_compute_output_field import tool_compute_output_field
from .tools.tool_backend_selection import StubBackendSelection
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.constants import (
    SCENARIO_ID_KEY,
    SCENARIO_PATH_KEY,
    SCENARIO_HASH_KEY,
    ENTRYPOINT_KEY,
    SCENARIOS_KEY,
    STORE_TRUE,
    SERVE_ARG,
    SERVE_ASYNC_ARG,
    DRY_RUN_ARG,
    DEBUG_TRACE_ARG,
    NODE_METADATA_FILENAME,
    MAIN_MODULE_NAME,
    SCENARIOS_DIRNAME,
    SCENARIOS_INDEX_FILENAME,
    LOG_FORMAT_KEY,
    RESULT_KEY,
    ERROR_KEY,
    CORRELATION_ID_KEY,
    NODE_ID_KEY,
    EVENT_TYPE_KEY,
    INPUT_FIELD_KEY,
    OPTIONAL_FIELD_KEY,
    VERSION_KEY,
    NODE_NAME_KEY,
    NODE_VERSION_KEY,
    BACKEND_SELECTION_KEY,
    INPUT_VALIDATION_KEY,
    OUTPUT_FIELD_KEY,
    BOOTSTRAP_KEY,
    HEALTH_CHECK_KEY,
    EVENT_ID_KEY,
    TIMESTAMP_KEY,
    ONEX_TRACE_ENV_KEY,
)
from .registry.registry_node_manager import RegistryNodeManager
from omnibase.mixin.mixin_node_id_from_contract import MixinNodeIdFromContract

NODE_ONEX_YAML_PATH = Path(__file__).parent / NODE_METADATA_FILENAME

TRACE_MODE = os.environ.get("ONEX_TRACE") == "1"
_trace_mode_flag = None


def is_trace_mode():
    global _trace_mode_flag
    if _trace_mode_flag is not None:
        return _trace_mode_flag
    import sys

    _trace_mode_flag = TRACE_MODE or ("--debug-trace" in sys.argv)
    return _trace_mode_flag


class NodeManager(MixinNodeIdFromContract, NodeManagerIntrospection, ProtocolReducer):
    """
    Canonical ONEX reducer node_manager implementing ProtocolReducer.
    
    **ALL business logic must be delegated to protocol-typed helpers/tools.**
    This class is strictly an orchestrator: it wires together protocol-compliant tools, event bus, and scenario runner.
    No business logic, validation, or output computation should be implemented inline here.
    
    Dependency injection for tools follows the ONEX canonical pattern:
    - All tools are injected via the constructor, typed as their Protocol interfaces.
    - Defaults are set to canonical implementations.
    - This enables easy swapping/mocking and future migration to a registry/DI framework (e.g., Eye).
    - When a registry is available, update the constructor to resolve tools from the registry.
    - If 'registry' is provided, use it for all tool lookups (future-proof for full registry-driven DI).
    
    Maintainers: If you find business logic in this class, refactor it into a protocol-typed helper/tool.
    """

    def __init__(
        self,
        tool_bootstrap=None,
        tool_backend_selection=None,
        tool_health_check=None,
        input_validation_tool: InputValidationToolProtocol = None,
        output_field_tool: OutputFieldToolProtocol = None,
        event_bus: ProtocolEventBus = None,
        config=None,
        skip_subscribe: bool = False,
        registry: ProtocolNodeRegistry = None,
    ):
        node_id = self._load_node_id()
        node_dir = Path(__file__).parent
        node_onex_yaml = node_dir / NODE_METADATA_FILENAME
        with open(node_onex_yaml, "r") as f:
            metadata = NodeMetadataBlock.from_file_or_content(f.read())
        node_version = metadata.version
        # Canonical event bus instantiation logic (matches Kafka node)
        if registry is not None:
            # Registry-driven DI: resolve all tools from registry if present
            # (future-proof: registry_tools pattern)
            if hasattr(registry, 'get_tool'):
                tool_backend_selection = tool_backend_selection or registry.get_tool(BACKEND_SELECTION_KEY)
                input_validation_tool = input_validation_tool or registry.get_tool(INPUT_VALIDATION_KEY)
                output_field_tool = output_field_tool or registry.get_tool(OUTPUT_FIELD_KEY)
                tool_bootstrap = tool_bootstrap or registry.get_tool(BOOTSTRAP_KEY)
                tool_health_check = tool_health_check or registry.get_tool(HEALTH_CHECK_KEY)
        # Fallback to canonical defaults if not provided
        if input_validation_tool is None:
            input_validation_tool = ToolInputValidation(
                NodeManagerInputState, NodeManagerOutputState, ModelNodeManagerOutputField, node_id="node_manager"
            )
        if output_field_tool is None:
            output_field_tool = tool_compute_output_field
        if event_bus is None:
            from omnibase.model.model_event_bus_config import ModelEventBusConfig
            if config is None:
                config = ModelEventBusConfig.default()
            if tool_backend_selection is not None:
                event_bus = tool_backend_selection.select_event_bus(config)
            else:
                from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
                event_bus = get_event_bus(config=config)
        super().__init__(node_id=node_id, event_bus=event_bus)
        self.tool_bootstrap = tool_bootstrap
        self.tool_backend_selection = tool_backend_selection
        self.tool_health_check = tool_health_check
        self.input_validation_tool: InputValidationToolProtocol = input_validation_tool
        self.output_field_tool: OutputFieldToolProtocol = output_field_tool
        self.config = config
        self.skip_subscribe = skip_subscribe
        self.node_version = node_version
        self.registry = registry  # Store for registry-driven DI
        # Canonical event bus integration point for event-driven nodes
        # EventDrivenNodeMixin sets up event handlers automatically
        # self.event_bus.subscribe(self.handle_event)  # Removed: handled by mixin
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"NodeManager instantiated",
                context=make_log_context(node_id=self.node_id),
            )

    def handle_event(self, event: OnexEvent):
        """
        Orchestrates event-driven scenario execution. All business logic is delegated to protocol-typed helpers/tools.
        This method should never implement scenario logic directly.
        """
        if event.event_type != OnexEventTypeEnum.TOOL_PROXY_INVOKE:
            return
        if event.node_id != self.node_id:
            return
        metadata = event.metadata or {}
        scenario_id = metadata.get(SCENARIO_ID_KEY)
        log_format = metadata.get(LOG_FORMAT_KEY, LogFormat.JSON.value)
        correlation_id = event.correlation_id
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[handle_event] Received TOOL_PROXY_INVOKE with scenario_id: {scenario_id}",
            context=make_log_context(
                node_id=self.node_id, correlation_id=correlation_id
            ),
        )
        try:
            if scenario_id:
                # Delegate to scenario runner
                scenarios_index_path = Path(__file__).parent / SCENARIOS_DIRNAME / SCENARIOS_INDEX_FILENAME
                with open(scenarios_index_path, "r") as f:
                    scenario_registry = yaml.safe_load(f)
                node_scenarios_dir = Path(__file__).parent / SCENARIOS_DIRNAME
                # Find the scenario entrypoint path
                scenario_entry = next((s for s in scenario_registry[SCENARIOS_KEY] if s[SCENARIO_ID_KEY] == scenario_id), None)
                if not scenario_entry:
                    emit_log_event_sync(
                        LogLevelEnum.ERROR,
                        f"[handle_event] Scenario id '{scenario_id}' not found in registry.",
                        context=make_log_context(node_id=self.node_id, correlation_id=correlation_id),
                    )
                    return
                scenario_path = node_scenarios_dir / Path(scenario_entry[ENTRYPOINT_KEY])
                # Compute and log scenario hash
                try:
                    with open(scenario_path, "rb") as sf:
                        scenario_bytes = sf.read()
                        import hashlib
                        scenario_hash = hashlib.sha256(scenario_bytes).hexdigest()
                    emit_log_event_sync(
                        LogLevelEnum.INFO,
                        f"Scenario hash: {scenario_hash}",
                        context={SCENARIO_ID_KEY: scenario_id, SCENARIO_PATH_KEY: str(scenario_path), SCENARIO_HASH_KEY: scenario_hash},
                    )
                except Exception as e:
                    emit_log_event_sync(
                        LogLevelEnum.ERROR,
                        f"[handle_event] Failed to compute scenario hash: {e}",
                        context={SCENARIO_ID_KEY: scenario_id, SCENARIO_PATH_KEY: str(scenario_path)},
                    )
                result, error = self.scenario_runner.run_scenario(
                    self,
                    scenario_id,
                    scenario_registry,
                    node_scenarios_dir=node_scenarios_dir,
                    correlation_id=correlation_id,
                )
                result_event = OnexEvent(
                    event_id=uuid.uuid4(),
                    timestamp=None,
                    node_id=self.node_id,
                    event_type=OnexEventTypeEnum.TOOL_PROXY_RESULT,
                    correlation_id=correlation_id,
                    metadata={
                        RESULT_KEY: result,
                        ERROR_KEY: error,
                        LOG_FORMAT_KEY: log_format,
                    },
                )
                self.event_bus.publish(result_event)
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[handle_event] Scenario complete for correlation_id: {correlation_id}",
                    context=make_log_context(
                        node_id=self.node_id, correlation_id=correlation_id
                    ),
                )
            else:
                emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"[handle_event] No scenario_id provided in TOOL_PROXY_INVOKE metadata.",
                    context=make_log_context(
                        node_id=self.node_id, correlation_id=correlation_id
                    ),
                )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[handle_event] Exception during scenario: {e}",
                context=make_log_context(
                    node_id=self.node_id, correlation_id=correlation_id
                ),
            )
            raise

    def run(self, input_state: NodeManagerInputState) -> NodeManagerOutputState:
        """
        Orchestrates scenario execution for direct invocation. Accepts a validated NodeManagerInputState model.
        All output computation and business logic must be delegated to protocol-typed helpers/tools.
        """
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"Entered run() with input_state: {input_state}",
                context=make_log_context(node_id=self.node_id),
            )
        semver = SemVerModel.parse(str(self.node_version))
        # Use protocol-compliant output field tool, but always wrap in ModelNodeManagerOutputField
        output_field_kwargs = self.output_field_tool(input_state, input_state.model_dump())
        if isinstance(output_field_kwargs, dict):
            output_field = ModelNodeManagerOutputField(**output_field_kwargs)
        elif isinstance(output_field_kwargs, ModelNodeManagerOutputField):
            output_field = ModelNodeManagerOutputField(result=str(output_field_kwargs))
        else:
            output_field = ModelNodeManagerOutputField(result=str(output_field_kwargs))
        # Ensure event_id and timestamp are always set
        event_id = getattr(input_state, EVENT_ID_KEY, None) or str(uuid.uuid4())
        timestamp = getattr(input_state, TIMESTAMP_KEY, None)
        if not timestamp:
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"Exiting run() with output_field: {output_field}, event_id: {event_id}, timestamp: {timestamp}",
                context=make_log_context(node_id=self.node_id),
            )
        return NodeManagerOutputState(
            version=semver,
            status=OnexStatus.SUCCESS,
            message="NodeManager ran successfully.",
            output_field=output_field,
            event_id=event_id,
            timestamp=timestamp,
            correlation_id=getattr(input_state, CORRELATION_ID_KEY, None),
            node_name=getattr(input_state, NODE_NAME_KEY, None),
            node_version=str(self.node_version),
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
        return NodeManagerInputState(
            version=SemVerModel(
                str(NodeMetadataBlock.from_file(NODE_ONEX_YAML_PATH).version)
            ),
            input_field="",
            optional_field=None,
        )

    def dispatch(self, state: StateModel, action: ActionModel) -> StateModel:
        """
        Intentionally minimal for the template node: returns the state unchanged.
        In production nodes, all business logic for state transitions should be delegated to protocol-typed helpers/tools.
        """
        return state

    def introspect(self):
        """
        Return a list of available scenarios for this node from scenarios/index.yaml.
        """
        scenarios_index_path = Path(__file__).parent / SCENARIOS_DIRNAME / SCENARIOS_INDEX_FILENAME
        if not scenarios_index_path.exists():
            return {SCENARIOS_KEY: []}
        with open(scenarios_index_path, "r") as f:
            data = yaml.safe_load(f)
        return data


def main(event_bus=None):
    from .tools.tool_backend_selection import StubBackendSelection
    from .models.state import NodeManagerInputState, NodeManagerOutputState, ModelNodeManagerOutputField
    from omnibase.tools.tool_input_validation import ToolInputValidation
    from omnibase.tools.tool_compute_output_field import tool_compute_output_field
    from .registry.registry_node_manager import RegistryNodeManager
    from omnibase.model.model_event_bus_config import ModelEventBusConfig

    config = ModelEventBusConfig.default()
    registry_node_manager = RegistryNodeManager()
    # Register canonical tools (stub backend selection, input validation, output field, etc.)
    registry_node_manager.register_tool(BACKEND_SELECTION_KEY, StubBackendSelection)
    registry_node_manager.register_tool(INPUT_VALIDATION_KEY, ToolInputValidation)
    registry_node_manager.register_tool(OUTPUT_FIELD_KEY, tool_compute_output_field)

    tool_backend_selection = StubBackendSelection(registry_node_manager)
    input_validation_tool = ToolInputValidation(
        input_model=NodeManagerInputState,
        output_model=NodeManagerOutputState,
        output_field_model=ModelNodeManagerOutputField,
        node_id="node_manager",
    )
    node = NodeManager(
        tool_backend_selection=tool_backend_selection,
        input_validation_tool=input_validation_tool,
        output_field_tool=tool_compute_output_field,
        event_bus=event_bus,
        config=config,
        skip_subscribe=False,
        registry=registry_node_manager,
    )
    parser = argparse.ArgumentParser(description="Node Manager CLI")
    parser.add_argument(SERVE_ARG, action=STORE_TRUE, help="Run the node event loop (sync)")
    parser.add_argument(DRY_RUN_ARG, action=STORE_TRUE, help="[Not applicable: this node has no side effects]")
    args, unknown = parser.parse_known_args()
    if args.dry_run:
        print("[DRY RUN] Not applicable: this node has no side effects to prevent. Exiting.")
        sys.exit(0)
    if args.serve:
        # Existing sync event loop logic (if any)
        pass
    return node


def get_introspection() -> dict:
    """Get introspection data for the node_manager node."""
    return NodeManagerIntrospection.get_introspection_response()
# Alias for standards-compliant import in tests and CLI


if __name__ == MAIN_MODULE_NAME:
    main()
