"""
Template Node (ONEX Canonical)

Implements the reducer pattern with .run() and .bind() lifecycle. All business logic is delegated to inline handlers or runtime helpers.
"""

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
import datetime
from datetime import timezone
import warnings

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

from .introspection import NodeLoggerIntrospection
from .models.state import NodeLoggerInputState, NodeLoggerOutputState
from omnibase.nodes.node_template.protocols.input_validation_tool_protocol import InputValidationToolProtocol
from omnibase.nodes.node_template.protocols.output_field_tool_protocol import OutputFieldTool as OutputFieldToolProtocol
from omnibase.runtimes.onex_runtime.v1_0_0.protocol.tool_scenario_runner_protocol import ToolScenarioRunnerProtocol
from omnibase.runtimes.onex_runtime.v1_0_0.tools.tool_scenario_runner import ToolScenarioRunner
from omnibase.tools.tool_input_validation import ToolInputValidation
from omnibase.tools.tool_compute_output_field import tool_compute_output_field
from omnibase.mixin.mixin_node_id_from_contract import MixinNodeIdFromContract
from omnibase.mixin.mixin_introspect_from_contract import MixinIntrospectFromContract
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
    EVENT_ID_KEY,
    TIMESTAMP_KEY,
    ONEX_TRACE_ENV_KEY,
    CHAIN_KEY,
    INPUT_KEY,
    GET_ACTIVE_REGISTRY_CONFIG_METHOD,
    NO_REGISTRY_TOOLS_ERROR_MSG,
)
from .tools.tool_logger_engine import ToolLoggerEngine
from .tools.tool_context_aware_output_handler import ToolContextAwareOutputHandler, ToolEnhancedLogFormatter
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.core.errors import OnexError
from .error_codes import NodeLoggerNodeErrorCode

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


class NodeLogger(MixinNodeIdFromContract, MixinIntrospectFromContract, NodeLoggerIntrospection, ProtocolReducer):
    """
    Canonical ONEX reducer node implementing ProtocolReducer.
    
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
        # Registry-driven DI: resolve all tools from registry if present
        def resolve_tool(tool_name, optional=False):
            if registry is not None and hasattr(registry, 'get_tool'):
                tool = registry.get_tool(tool_name)
                if tool is not None:
                    return tool
                if optional:
                    warnings.warn(f"[NodeLogger] Optional tool '{tool_name}' not found in registry; continuing without it.")
                    return None
                raise OnexError(NodeLoggerNodeErrorCode.HANDLER_NOT_FOUND, f"[NodeLogger] Required tool '{tool_name}' not found in registry for this scenario. All dependencies must be specified in registry_tools.")
            raise OnexError(NodeLoggerNodeErrorCode.MISSING_REQUIRED_PARAMETER, f"[NodeLogger] No registry provided; cannot resolve tool '{tool_name}'.")

        tool_backend_selection = tool_backend_selection or resolve_tool('backend_selection')
        input_validation_tool = input_validation_tool or resolve_tool('input_validation')
        output_field_tool = output_field_tool or resolve_tool('output_field')
        tool_bootstrap = tool_bootstrap or resolve_tool('bootstrap', optional=True)
        tool_health_check = tool_health_check or resolve_tool('health_check', optional=True)
        self.logger_engine = resolve_tool('logger_engine')
        self.context_aware_output_handler = resolve_tool('context_aware_output_handler', optional=True)
        # Fallbacks to canonical defaults if not provided
        if input_validation_tool is None:
            warnings.warn(NODELOGGER_INPUT_VALIDATION_TOOL_NOT_PROVIDED_USING_CANONICAL_DEFAULT)
            input_validation_tool = ToolInputValidation(
                NodeLoggerInputState, NodeLoggerOutputState, OnexFieldModel, node_id=NODE_ID_KEY
            )
        if output_field_tool is None:
            warnings.warn(NODELOGGER_OUTPUT_FIELD_TOOL_NOT_PROVIDED_USING_CANONICAL_DEFAULT)
            output_field_tool = tool_compute_output_field
        if event_bus is None:
            from omnibase.model.model_event_bus_config import ModelEventBusConfig
            if config is None:
                config = ModelEventBusConfig.default()
            if tool_backend_selection is not None:
                event_bus = tool_backend_selection.select_event_bus(config)
            else:
                raise OnexError(NodeLoggerNodeErrorCode.BACKEND_UNAVAILABLE, NODELOGGER_NO_BACKEND_SELECTION_TOOL_PROVIDED_IN_REGISTRY_TOOLS_CANNOT_SELECT_EVENT_BUS_ALL_SCENARIOS_MUST_SPECIFY_BACKEND_SELECTION_AND_INMEMORY_OR_DESIRED_BACKEND_IN_REGISTRY_TOOL)
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
                fNODELOGGER_INSTANTIATED,
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
        log_format = metadata.get(LOG_FORMAT_KEY, "json")
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
                scenarios_index_path = Path(__file__).parent / "scenarios" / SCENARIOS_INDEX_FILENAME
                with open(scenarios_index_path, "r") as f:
                    scenario_registry = yaml.safe_load(f)
                node_scenarios_dir = Path(__file__).parent / "scenarios"
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

    def run(self, input_state: NodeLoggerInputState) -> NodeLoggerOutputState:
        """
        Orchestrates scenario execution for direct invocation. Accepts a validated NodeTemplateInputState model.
        All output computation and business logic must be delegated to protocol-typed helpers/tools.
        """
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"Entered run() with input_state: {input_state}",
                context=make_log_context(node_id=self.node_id),
            )
        semver = SemVerModel.parse(str(self.node_version))
        # Use protocol-compliant output field tool, but always wrap in NodeLoggerOutputState
        output_field_kwargs = self.output_field_tool(input_state, input_state.model_dump())
        if isinstance(output_field_kwargs, dict):
            output_field = NodeLoggerOutputState(**output_field_kwargs)
        elif isinstance(output_field_kwargs, NodeLoggerOutputState):
            output_field = output_field_kwargs
        else:
            output_field = NodeLoggerOutputState(result=str(output_field_kwargs))
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
        return NodeLoggerOutputState(
            version=semver,
            status=OnexStatus.SUCCESS,
            message=NODELOGGER_RAN_SUCCESSFULLY,
            formatted_log="...",  # Replace with actual formatted log
            output_format="json",  # Replace with actual output format
            timestamp=timestamp,
            log_level=input_state.log_level,
            entry_size=0,  # Replace with actual entry size
        )

    def bind(self, *args, **kwargs):
        """
        Bind pattern stub. In ONEX, this is used for chaining nodes.
        """
        return self

    def initial_state(self) -> StateModel:
        """
        Return the initial state for the logger node reducer. Override as needed.
        """
        return NodeLoggerInputState(
            version=SemVerModel(
                str(NodeMetadataBlock.from_file(NODE_ONEX_YAML_PATH).version)
            ),
            log_level=LogLevelEnum.INFO,
            message=INITIAL_LOG_MESSAGE,
            output_format="json",
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
        scenarios_index_path = Path(__file__).parent / "scenarios" / SCENARIOS_INDEX_FILENAME
        if not scenarios_index_path.exists():
            return {SCENARIOS_KEY: []}
        with open(scenarios_index_path, "r") as f:
            data = yaml.safe_load(f)
        return data


def main(event_bus=None):
    if event_bus is None:
        event_bus = get_event_bus()
    parser = argparse.ArgumentParser(description="ONEX Logger Node")
    parser.add_argument(
        "--introspect", action="store_true", help="Show node introspection"
    )
    parser.add_argument("--run-scenario", type=str, help="Run a scenario by ID")
    parser.add_argument("--input", type=str, help="Input JSON for direct execution")
    parser.add_argument(
        "--debug-trace",
        action="store_true",
        help="Enable trace-level logging for demo/debug",
    )
    parser.add_argument(
        "--log-format",
        type=str,
        choices=[f.value for f in LogFormat],
        default=LogFormat.JSON.value,
        help="Log output format (json, text, key-value, markdown, yaml, csv)",
    )
    args = parser.parse_args()

    # Set trace mode flag if --debug-trace is present
    global _trace_mode_flag
    if args.debug_trace:
        _trace_mode_flag = True
    try:
        log_format_enum = LogFormat(args.log_format.lower())
    except ValueError:
        log_format_enum = LogFormat.JSON
    set_log_format(log_format_enum)
    emit_log_event_sync(
        LogLevelEnum.DEBUG,
        f"[main] set_log_format to {get_log_format()}",
        make_log_context(node_id=NODE_ID_KEY),
    )

    if args.introspect:
        NodeLoggerIntrospection.handle_introspect_command()
        return

    if args.run_scenario:
        scenario_id = args.run_scenario
        scenarios = NodeLoggerIntrospection.get_scenarios()
        scenario = next((s for s in scenarios if s["id"] == scenario_id), None)
        if not scenario:
            sys.exit(1)
        entrypoint = scenario.get(ENTRYPOINT_KEY)
        if not entrypoint:
            sys.exit(1)
        try:
            scenario_path = Path(__file__).parent / entrypoint
            with open(scenario_path, "r") as f:
                scenario_yaml = yaml.safe_load(f)
            input_data = scenario_yaml[CHAIN_KEY][0][INPUT_KEY]
            # === SCENARIO-DRIVEN REGISTRY INJECTION ===
            registry_tools = None
            if GET_ACTIVE_REGISTRY_CONFIG_METHOD in dir(scenario_yaml) and getattr(scenario_yaml, 'registry_configs', None):
                registry_tools = scenario_yaml.get_active_registry_config().tools
            elif getattr(scenario_yaml, 'registry_tools', None):
                registry_tools = scenario_yaml.registry_tools
            else:
                raise OnexError(NodeLoggerNodeErrorCode.MISSING_REQUIRED_PARAMETER, NO_REGISTRY_TOOLS_ERROR_MSG)
            from src.omnibase.nodes.node_logger.registry.registry_node_logger import LogFormatHandlerRegistry
            registry_node_logger = LogFormatHandlerRegistry(event_bus=event_bus)
            for tool_name, tool_ref in registry_tools.items():
                # tool_ref is a class or instance loaded by YAML !!python/name
                registry_node_logger.register_handler(tool_name, tool_ref, source='scenario', priority=100)
            node = NodeLogger(event_bus=event_bus, registry=registry_node_logger)
        except Exception as e:
            print(f"[main] Error loading scenario or registry: {e}")
            sys.exit(1)
        try:
            result = node.run(input_data)
        except Exception as e:
            print(f"[main] Error running node: {e}")
            sys.exit(1)
        return

    if args.input:
        try:
            input_data = json.loads(args.input)
            # For direct input, require explicit registry_tools via env or config (not supported here)
            raise OnexError(NodeLoggerNodeErrorCode.UNSUPPORTED_OPERATION, DIRECT_INPUT_EXECUTION_IS_NOT_SUPPORTED_WITHOUT_SCENARIO_DRIVEN_REGISTRY_TOOLS)
        except Exception as e:
            print(f"[main] Error: {e}")
            sys.exit(1)
        return

    sys.exit(1)


def get_introspection() -> dict:
    """Get introspection data for the logger node."""
    return NodeLoggerIntrospection.get_introspection_response()


if __name__ == MAIN_MODULE_NAME:
    node = NodeLogger()
    import time

    while True:
        time.sleep(1)
