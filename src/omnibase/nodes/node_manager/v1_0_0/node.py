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
    get_log_format,
    log_level_emoji,
    make_log_context,
    set_log_format,
)
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus

from .introspection import get_node_introspection_response
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
from omnibase.nodes.node_logger.protocols.protocol_logger_emit_log_event import ProtocolLoggerEmitLogEvent
from omnibase.core.core_errors import OnexError, CoreErrorCode, RegistryErrorCode
from omnibase.runtimes.onex_runtime.v1_0_0.tools.tool_registry_resolver import registry_resolver_tool
from omnibase.protocol.protocol_registry_resolver import ProtocolRegistryResolver
from omnibase.mixin.mixin_node_setup import MixinNodeSetup
from omnibase.protocol.protocol_input_validation_tool import (
    InputValidationToolProtocol,
)
from omnibase.protocol.protocol_output_field_tool import (
    OutputFieldTool,
)
from omnibase.protocol.protocol_tool_backend_selection import (
    ToolBackendSelectionProtocol,
)
from omnibase.protocol.protocol_tool_bootstrap import (
    ToolBootstrapProtocol,
)
from omnibase.protocol.protocol_tool_health_check import (
    ToolHealthCheckProtocol,
)

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


class NodeManager(MixinNodeIdFromContract, MixinNodeSetup, ProtocolReducer):
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
        logger_tool: ProtocolLoggerEmitLogEvent,
        registry: RegistryNodeManager,
        tool_bootstrap: ToolBootstrapProtocol = None,
        tool_backend_selection: ToolBackendSelectionProtocol = None,
        tool_health_check: ToolHealthCheckProtocol = None,
        input_validation_tool: InputValidationToolProtocol = None,
        output_field_tool: OutputFieldTool = None,
        registry_resolver: ProtocolRegistryResolver = registry_resolver_tool,
        **kwargs,
    ):
        """
        Initialize NodeManager with protocol-pure dependency injection.
        All tools are injected via constructor parameters following standard ONEX pattern.
        """
        if logger_tool is None:
            raise OnexError("Logger tool must be provided via DI or registry (protocol-pure).", CoreErrorCode.MISSING_REQUIRED_PARAMETER)
        if registry is None:
            raise OnexError("Registry must be provided via DI (protocol-pure).", CoreErrorCode.MISSING_REQUIRED_PARAMETER)
        self.logger_tool = logger_tool
        self.tool_bootstrap = tool_bootstrap
        self.tool_backend_selection = tool_backend_selection
        self.tool_health_check = tool_health_check
        self.input_validation_tool = input_validation_tool
        self.output_field_tool = output_field_tool
        self.registry = registry
        self.registry_resolver = registry_resolver
        # Get scenario_runner from registry using protocol resolution
        scenario_runner_cls = self.registry.get_tool("scenario_runner")
        if scenario_runner_cls:
            self.scenario_runner = scenario_runner_cls()
        else:
            raise OnexError("scenario_runner tool not found in registry", RegistryErrorCode.TOOL_NOT_FOUND)
        # Initialize additional tools via registry resolution
        self._initialize_tools()
        # Load node metadata
        self._node_id = self._load_node_id()

    def _initialize_tools(self):
        """Initialize additional tools via registry resolution."""
        if not self.registry:
            raise OnexError("Registry required for tool initialization", CoreErrorCode.MISSING_REQUIRED_PARAMETER)
        
        # Get node-specific tools from registry
        template_engine_cls = self.registry.get_tool("TEMPLATE_ENGINE")
        if template_engine_cls:
            self.template_engine = template_engine_cls(logger_tool=self.logger_tool)
        else:
            raise OnexError("TEMPLATE_ENGINE tool not found in registry", RegistryErrorCode.TOOL_NOT_FOUND)
        
        contract_to_model_cls = self.registry.get_tool("CONTRACT_TO_MODEL")
        if contract_to_model_cls:
            self.contract_to_model = contract_to_model_cls
        else:
            raise OnexError("CONTRACT_TO_MODEL tool not found in registry", RegistryErrorCode.TOOL_NOT_FOUND)
        
        file_generator_cls = self.registry.get_tool("FILE_GENERATOR")
        if file_generator_cls:
            self.file_generator = file_generator_cls(logger_tool=self.logger_tool)
        else:
            raise OnexError("FILE_GENERATOR tool not found in registry", RegistryErrorCode.TOOL_NOT_FOUND)

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
        skip_preconditions = metadata.get("skip_preconditions", False)
        correlation_id = event.correlation_id
        self.logger_tool.emit_log_event_sync(
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
                    self.logger_tool.emit_log_event_sync(
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
                    self.logger_tool.emit_log_event_sync(
                        LogLevelEnum.INFO,
                        f"Scenario hash: {scenario_hash}",
                        context={SCENARIO_ID_KEY: scenario_id, SCENARIO_PATH_KEY: str(scenario_path), SCENARIO_HASH_KEY: scenario_hash},
                    )
                except Exception as e:
                    self.logger_tool.emit_log_event_sync(
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
                    skip_preconditions=skip_preconditions,
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
                self.logger_tool.emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[handle_event] Scenario complete for correlation_id: {correlation_id}",
                    context=make_log_context(
                        node_id=self.node_id, correlation_id=correlation_id
                    ),
                )
            else:
                self.logger_tool.emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"[handle_event] No scenario_id provided in TOOL_PROXY_INVOKE metadata.",
                    context=make_log_context(
                        node_id=self.node_id, correlation_id=correlation_id
                    ),
                )
        except Exception as e:
            self.logger_tool.emit_log_event_sync(
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
            self.logger_tool.emit_log_event_sync(
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
            self.logger_tool.emit_log_event_sync(
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
            node_version=semver,
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
    scenario_path = os.environ.get("ONEX_SCENARIO_PATH")
    fallback_tools = None
    if not (scenario_path and os.path.exists(scenario_path)):
        fallback_tools = {}  # Add any fallback tools if needed
    
    # Use registry resolver to get the registry (following Kafka node pattern)
    registry = registry_resolver_tool.resolve_registry(
        RegistryNodeManager, 
        scenario_path=scenario_path, 
        fallback_tools=fallback_tools
    )
    
    # Get logger tool from registry
    logger_tool_cls = registry.get_tool("tool_logger_emit_log_event")
    if logger_tool_cls:
        logger_tool = logger_tool_cls()
    else:
        raise OnexError("tool_logger_emit_log_event not found in registry", RegistryErrorCode.TOOL_NOT_FOUND)
    
    node = NodeManager(
        logger_tool=logger_tool,
        registry=registry,
        registry_resolver=registry_resolver_tool,
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
