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

import yaml
from pydantic import ValidationError

from omnibase.constants import (
    ARGS_KEY,
    BACKEND_KEY,
    BOOTSTRAP_ARG,
    BUS_ID_KEY,
    CONFIG_KEY,
    CONTRACT_FILENAME,
    CUSTOM_KEY,
    DEBUG_TRACE_ARG,
    DEFAULT_PROCESSED_VALUE,
    ENDPOINT_UNKNOWN,
    HEALTH_CHECK_ARG,
    HEALTH_CHECK_RESULT_PREFIX,
    INPUT_VALIDATION_SUCCEEDED_MSG,
    INTEGRATION_KEY,
    LOG_FORMAT_JSON,
    LOG_FORMAT_KEY,
    MESSAGE_KEY,
    NODE_ANNOUNCE_EVENT,
    NODE_METADATA_FILENAME,
    ONEX_TRACE_ENV_KEY,
    PROCESSED_KEY,
    RESULT_KEY,
    SCENARIOS_DIRNAME,
    SCENARIOS_INDEX_FILENAME,
    SCENARIOS_KEY,
    STATUS_KEY,
    STATUS_OK_VALUE,
    STRUCTURED_LOG_EVENT,
    TOOL_PROXY_INVOKE_EVENT,
    TOOL_PROXY_RESULT_EVENT,
    VERSION_KEY,
)
from omnibase.enums.enum_registry_output_status import RegistryOutputStatusEnum
from omnibase.enums.log_level import LogLevelEnum
from omnibase.enums.onex_status import OnexStatus
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from omnibase.mixin.mixin_node_setup import MixinNodeSetup
from omnibase.model.model_node_metadata import LogFormat, NodeMetadataBlock
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.model.model_output_field import OnexFieldModel
from omnibase.model.model_output_field_utils import build_output_field_kwargs, compute_output_field
from omnibase.model.model_reducer import ActionModel, StateModel
from omnibase.model.model_semver import SemVerModel, parse_input_state_version
from omnibase.model.model_state_contract import load_state_contract_from_file
from omnibase.nodes.node_kafka_event_bus.constants import (
    DEBUG_ENTERED_RUN,
    NODE_KAFKA_EVENT_BUS_SUCCESS_EVENT_MSG,
    NODE_KAFKA_EVENT_BUS_SUCCESS_MSG,
    PROTOCOL_KAFKA,
)
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
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import (
    ModelEventBusConfig,
    ModelEventBusInputState,
    ModelEventBusOutputField,
    ModelEventBusOutputState,
)
from omnibase.nodes.node_registry_node.v1_0_0.models.state import EventBusInfoModel
from omnibase.protocol.protocol_event_bus_types import ProtocolEventBus
from omnibase.protocol.protocol_reducer import ProtocolReducer
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import (
    MetadataYAMLHandler,
)
from omnibase.runtimes.onex_runtime.v1_0_0.tools.metadata_loader_tool import (
    metadata_loader_tool,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import (
    emit_log_event_sync,
    get_log_format,
    log_level_emoji,
    make_log_context,
    set_log_format,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.utils_trace_mode import is_trace_mode
from omnibase.mixin.mixin_node_id_from_contract import MixinNodeIdFromContract
from omnibase.mixin.mixin_introspect_from_contract import MixinIntrospectFromContract

TRACE_MODE = os.environ.get(ONEX_TRACE_ENV_KEY) == "1"
_trace_mode_flag = None


def is_trace_mode():
    global _trace_mode_flag
    if _trace_mode_flag is not None:
        return _trace_mode_flag
    import sys

    _trace_mode_flag = TRACE_MODE or ("--debug-trace" in sys.argv)
    return _trace_mode_flag


class NodeKafkaEventBus(
    MixinNodeIdFromContract,
    MixinIntrospectFromContract,
    EventDrivenNodeMixin,
    MixinNodeSetup,
    ProtocolReducer,
):
    """
    Canonical ONEX reducer node implementing ProtocolReducer.
    Handles all scenario-driven logic for smoke, error, output, and integration cases.
    Resolves event bus via protocol-pure factory; never instantiates backend directly.
    """

    def __init__(
        self,
        tool_bootstrap: ToolBootstrapProtocol,
        tool_backend_selection: ToolBackendSelectionProtocol,
        tool_health_check: ToolHealthCheckProtocol,
        input_validation_tool: InputValidationToolProtocol,
        output_field_tool: OutputFieldTool,
        event_bus: ProtocolEventBus = None,
        config: ModelEventBusConfig = None,
        skip_subscribe: bool = False,
    ):
        node_id = self._load_node_id()
        if event_bus is None:
            if config is None:
                config = ModelEventBusConfig.default()
            event_bus = tool_backend_selection.select_event_bus(config)
        super().__init__(node_id=node_id, event_bus=event_bus)
        self.config = config
        self.skip_subscribe = skip_subscribe
        self.tool_bootstrap = tool_bootstrap
        self.tool_backend_selection = tool_backend_selection
        self.tool_health_check = tool_health_check
        self.input_validation_tool = input_validation_tool
        self.output_field_tool = output_field_tool
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"NodeKafkaEventBus instantiated",
                context=make_log_context(node_id=node_id),
            )

    def handle_event(self, event: OnexEvent):
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[handle_event] Received event: {getattr(event, 'event_type', None)} correlation_id={getattr(event, 'correlation_id', None)}",
            make_log_context(node_id=self._node_id),
        )
        if event.event_type != OnexEventTypeEnum.TOOL_PROXY_INVOKE:
            return
        if event.node_id != self._node_id:
            return
        metadata = event.metadata or {}
        args = metadata.get(ARGS_KEY, [])
        log_format = metadata.get(LOG_FORMAT_KEY, LOG_FORMAT_JSON)
        correlation_id = event.correlation_id
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[handle_event] Received TOOL_PROXY_INVOKE with args: {args}",
            context=make_log_context(
                node_id=self._node_id, correlation_id=correlation_id
            ),
        )
        # For demo: just emit a log event and a result event
        log_event = OnexEvent(
            event_id=uuid.uuid4(),
            timestamp=None,
            node_id=self._node_id,
            event_type=OnexEventTypeEnum.STRUCTURED_LOG,
            correlation_id=correlation_id,
            metadata={
                MESSAGE_KEY: f"[node_kafka_event_bus] Received args: {args}",
                LOG_FORMAT_KEY: log_format,
            },
        )
        self.event_bus.publish(log_event)
        try:
            # Simulate running a scenario and emitting a result
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[handle_event] Running scenario for correlation_id: {correlation_id}",
                context=make_log_context(
                    node_id=self._node_id, correlation_id=correlation_id
                ),
            )
            result = ModelEventBusOutputState(
                version=self.node_version,
                status=OnexStatus.SUCCESS,
                message=NODE_KAFKA_EVENT_BUS_SUCCESS_EVENT_MSG,
            )
            result_event = OnexEvent(
                event_id=uuid.uuid4(),
                timestamp=None,
                node_id=self._node_id,
                event_type=OnexEventTypeEnum.TOOL_PROXY_RESULT,
                correlation_id=correlation_id,
                metadata={
                    RESULT_KEY: result.model_dump(),
                    LOG_FORMAT_KEY: log_format,
                },
            )
            self.event_bus.publish(result_event)
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[handle_event] Scenario complete for correlation_id: {correlation_id}",
                context=make_log_context(
                    node_id=self._node_id, correlation_id=correlation_id
                ),
            )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"[handle_event] Exception during scenario: {e}",
                context=make_log_context(
                    node_id=self._node_id, correlation_id=correlation_id
                ),
            )
            raise

    def run(self, input_state: dict) -> ModelEventBusOutputState:
        print(f"{DEBUG_ENTERED_RUN} NodeKafkaEventBus.run()", flush=True)
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"Entered run() with input_state: {input_state}",
                context=make_log_context(node_id=self._node_id),
            )
        # Validate and parse input
        fallback_version = SemVerModel.parse(str(self.node_version))
        version = parse_input_state_version(input_state, fallback=fallback_version)
        try:
            version = parse_input_state_version(input_state, fallback=fallback_version)
        except Exception as e:
            msg = f"ValidationError in run: {e}"
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                msg,
                context=make_log_context(node_id=self._node_id),
            )
            return ModelEventBusOutputState(
                version=version,
                status=OnexStatus.ERROR,
                message=msg,
                output_field=None,
            )
        # Modularization: Use protocol-compliant input validation tool (see checklist section 5)
        state, error_output = self.input_validation_tool.validate_input_state(
            input_state, version, self.event_bus
        )
        if error_output is not None:
            return error_output
        # Only proceed if input is valid
        output_field = self.output_field_tool(state, input_state)
        # Check for bootstrap argument
        args = input_state.get(ARGS_KEY, [])
        if BOOTSTRAP_ARG in args:
            config = None
            try:
                state = ModelEventBusInputState(**input_state)
                config = getattr(state, CONFIG_KEY, None)
            except Exception:
                config = input_state.get(CONFIG_KEY)
            if config is None:
                config = ModelEventBusConfig.default()
            # Modularization: Use protocol-compliant bootstrap tool (see checklist section 5)
            result = self.tool_bootstrap.bootstrap_kafka_cluster(config)
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[NodeKafkaEventBus] Kafka bootstrap result: {result}",
                context=make_log_context(node_id=self._node_id),
            )
            return ModelEventBusOutputState(
                version=self.node_version,
                status=(
                    OnexStatus.SUCCESS
                    if getattr(result, STATUS_KEY, None) == STATUS_OK_VALUE
                    else OnexStatus.ERROR
                ),
                message=f"Kafka bootstrap completed: {result}",
            )
        # Check for health check argument
        if HEALTH_CHECK_ARG in args:
            config = None
            try:
                state = ModelEventBusInputState(**input_state)
                config = getattr(state, CONFIG_KEY, None)
            except Exception:
                config = input_state.get(CONFIG_KEY)
            if config is None:
                config = ModelEventBusConfig.default()
            # Modularization: Use protocol-compliant health check tool (see checklist section 5)
            health_result = self.tool_health_check.health_check(config)
            emit_log_event_sync(
                LogLevelEnum.INFO,
                f"[NodeKafkaEventBus] Kafka health check result: {health_result}",
                context=make_log_context(node_id=self._node_id),
                event_bus=self.event_bus,
            )
            print("[HEALTH CHECK RESULT]", health_result, flush=True)
            return ModelEventBusOutputState(
                version=self.node_version,
                status=(
                    OnexStatus.SUCCESS
                    if getattr(health_result, STATUS_KEY, None) == STATUS_OK_VALUE
                    else OnexStatus.ERROR
                ),
                message=f"Kafka health check completed: {health_result}",
            )
        # Use metadata_loader_tool for node metadata loading
        node_metadata_block = metadata_loader_tool.load_node_metadata(
            Path(__file__).parent / NODE_METADATA_FILENAME, self.event_bus
        )
        node_version = str(node_metadata_block.version)
        # Parse config from state if present and re-instantiate event bus if needed
        config = None
        try:
            state = ModelEventBusInputState(**input_state)
            config = getattr(state, CONFIG_KEY, None)
        except Exception:
            config = input_state.get(CONFIG_KEY)
        # Coerce config to ModelEventBusConfig if needed
        if config is not None and not isinstance(config, ModelEventBusConfig):
            if isinstance(config, dict):
                config = ModelEventBusConfig(**config)
        if config and not isinstance(self.event_bus, ProtocolEventBus):
            # Re-instantiate with KafkaEventBus if config is present
            self.event_bus = get_event_bus(event_bus_type="kafka", config=config)
            emit_log_event_sync(
                LogLevelEnum.INFO,
                "[NodeKafkaEventBus] Switched to KafkaEventBus backend in run()",
                context=make_log_context(node_id=self._node_id),
            )
        try:
            state = ModelEventBusInputState(**input_state)
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    INPUT_VALIDATION_SUCCEEDED_MSG,
                    context=make_log_context(node_id=self._node_id),
                )
        except ValidationError as e:
            msg = str(e.errors()[0]["msg"]) if e.errors() else str(e)
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    f"Input validation failed: {msg}",
                    context=make_log_context(node_id=self._node_id),
                )
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"ValidationError in run: {msg}",
                context=make_log_context(node_id=self._node_id),
            )
            return ModelEventBusOutputState(
                version=resolve_version(input_state),
                status=OnexStatus.ERROR,
                message=msg,
                output_field=None,
            )
        except Exception as e:
            if is_trace_mode():
                emit_log_event_sync(
                    LogLevelEnum.TRACE,
                    f"Exception during input validation: {e}",
                    context=make_log_context(node_id=self._node_id),
                )
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Exception in run: {e}",
                context=make_log_context(node_id=self._node_id),
            )
            return ModelEventBusOutputState(
                version=resolve_version(input_state),
                status=OnexStatus.ERROR,
                message=str(e),
                output_field=None,
            )
        # Only use version as a string from here on
        output_field_kwargs = build_output_field_kwargs(input_state, self.event_bus)
        output_field = ModelEventBusOutputField(**output_field_kwargs)
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"About to return from run()",
                context=make_log_context(node_id=self._node_id),
            )
        return ModelEventBusOutputState(
            version=self.node_version,
            status=OnexStatus.SUCCESS,
            message=NODE_KAFKA_EVENT_BUS_SUCCESS_MSG,
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
        return ModelEventBusInputState(
            version=str(self.node_version), input_field="", optional_field=None
        )

    def dispatch(self, state: StateModel, action: ActionModel) -> StateModel:
        """
        Apply an action to the state and return the new state. Override as needed.
        """
        # For template, just return the state unchanged
        return state


def get_introspection() -> dict:
    """Get introspection data for the template node."""
    return NodeKafkaEventBus.get_introspection_response()
