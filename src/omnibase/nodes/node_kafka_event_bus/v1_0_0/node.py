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
import logging
import glob
from typing import Union

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
    INPUT_FIELD_KEY,
    EVENT_TYPE_KEY,
    CORRELATION_ID_KEY,
    BOOTSTRAP_SERVERS_KEY,
    PUBLISH_ASYNC_METHOD,
    FIELD_REQUIRED_ERROR_MSG,
    ENTRYPOINT_KEY,
    STORE_TRUE,
    SERVE_ARG,
    SERVE_ASYNC_ARG,
    DRY_RUN_ARG,
    MAIN_MODULE_NAME,
    KAFKA_KEY,
    INMEMORY_KEY,
    SCENARIO_ID_KEY,
    OPTIONAL_FIELD_KEY,
    BOOTSTRAP_KEY,
    BACKEND_SELECTION_KEY,
    HEALTH_CHECK_KEY,
    INPUT_VALIDATION_KEY,
    OUTPUT_FIELD_KEY,
    GET_ACTIVE_REGISTRY_CONFIG_METHOD,
    NO_REGISTRY_TOOLS_ERROR_MSG,
)
from omnibase.enums.enum_registry_output_status import RegistryOutputStatusEnum
from omnibase.enums.log_level import LogLevelEnum
from omnibase.enums.onex_status import OnexStatus
from omnibase.mixin.event_driven_node_mixin import EventDrivenNodeMixin
from omnibase.mixin.mixin_node_setup import MixinNodeSetup
from omnibase.model.model_node_metadata import LogFormat, NodeMetadataBlock
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.model.model_output_field_utils import build_output_field_kwargs, compute_output_field, make_output_field
from omnibase.model.model_reducer import ActionModel, StateModel
from omnibase.model.model_semver import SemVerModel, parse_input_state_version
from omnibase.model.model_state_contract import load_state_contract_from_file
from omnibase.nodes.node_kafka_event_bus.constants import (
    DEBUG_ENTERED_RUN,
    NODE_KAFKA_EVENT_BUS_SUCCESS_EVENT_MSG,
    NODE_KAFKA_EVENT_BUS_SUCCESS_MSG,
    PROTOCOL_KAFKA,
    NODE_KAFKA_EVENT_BUS_ID,
)
from omnibase.constants import (
    TEST_DEGRADED,
    TEST_BOOTSTRAP,
    TEST_CHAIN,
    TEST_MULTI,
    TEST_INTROSPECT,
    TEST_HEALTH,
    TEST_ASYNC_HANDLER,
    TEST,
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
from omnibase.tools.tool_input_validation import ToolInputValidation
from .models.state import (
    NodeKafkaEventBusNodeInputState,
    NodeKafkaEventBusNodeOutputState,
    ModelEventBusOutputField,
)
from omnibase.model.model_event_bus_config import ModelEventBusConfig
# from omnibase.model.model_event_bus_output_field import ModelEventBusOutputField
from .registry.registry_kafka_event_bus import RegistryKafkaEventBus, CLI_COMMANDS_KEY
from .tools.tool_backend_selection import ToolBackendSelection
from .tools.tool_kafka_event_bus import KafkaEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.runtimes.onex_runtime.v1_0_0.tools.tool_registry_resolver import registry_resolver_tool
from omnibase.protocol.protocol_registry_resolver import ProtocolRegistryResolver
from .models.model_cli_command import ModelCliCommand
from .enums.enum_node_kafka_command import NodeKafkaCommandEnum
from .enums.enum_node_kafka_arg import NodeKafkaArgEnum
from omnibase.enums.enum_node_arg import NodeArgEnum
from .error_codes import NodeKafkaEventBusNodeErrorCode

TRACE_MODE = os.environ.get(ONEX_TRACE_ENV_KEY) == "1"
_trace_mode_flag = None

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
    If 'registry' is provided, use it for all tool lookups (future-proof for full registry-driven DI).
    """

    def __init__(
        self,
        tool_bootstrap: ToolBootstrapProtocol,
        tool_backend_selection: ToolBackendSelectionProtocol,
        tool_health_check: ToolHealthCheckProtocol,
        input_validation_tool: InputValidationToolProtocol,
        output_field_tool: OutputFieldTool = None,
        event_bus: ProtocolEventBus = None,
        config: ModelEventBusConfig = None,
        skip_subscribe: bool = False,
        registry: RegistryKafkaEventBus = None,
        registry_resolver: ProtocolRegistryResolver = registry_resolver_tool,
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
        self.registry = registry or RegistryKafkaEventBus()
        self.registry_resolver = registry_resolver
        self.cli_commands_tool = self.registry.get_tool(CLI_COMMANDS_KEY)()
        if is_trace_mode():
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                f"NodeKafkaEventBus instantiated",
                context=make_log_context(node_id=node_id),
            )

    def handle_event(self, event: OnexEvent):
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"[handle_event] Received event: {getattr(event, EVENT_TYPE_KEY, None)} correlation_id={getattr(event, CORRELATION_ID_KEY, None)}",
            context=make_log_context(node_id=self._node_id),
        )
        if event.event_type != OnexEventTypeEnum.TOOL_PROXY_INVOKE or event.node_id != self._node_id:
            emit_log_event_sync(
                LogLevelEnum.DEBUG,
                f"[handle_event] Ignored event type or node_id: {getattr(event, EVENT_TYPE_KEY, None)}",
                context=make_log_context(node_id=self._node_id),
            )
            return
        metadata = event.metadata or {}
        command_name = metadata.get("command_name")
        args = metadata.get(ARGS_KEY, [])
        cli_command = ModelCliCommand(command_name=command_name, args=args)
        exit_code = self.cli_commands_tool.run_command(cli_command)
        # Use exit_code to determine output/event emission as needed
        # ... rest of event handling ...

    def run(self, input_state: NodeKafkaEventBusNodeInputState) -> NodeKafkaEventBusNodeOutputState:
        # Extract CLI command and args from input_state
        command_name = getattr(input_state, "command_name", None)
        args = getattr(input_state, ARGS_KEY, [])
        cli_command = ModelCliCommand(command_name=command_name, args=args)
        exit_code = self.cli_commands_tool.run_command(cli_command)
        # Use exit_code to determine output as needed
        # ... rest of run logic ...

    def bind(self, *args, **kwargs):
        """
        Bind pattern stub. In ONEX, this is used for chaining nodes.
        """
        return self

    def initial_state(self) -> StateModel:
        """
        Return the initial state for the reducer. Override as needed.
        """
        return NodeKafkaEventBusNodeInputState(
            version=str(self.node_version), input_field="", optional_field=None
        )

    def dispatch(self, state: StateModel, action: ActionModel) -> StateModel:
        """
        Apply an action to the state and return the new state. Override as needed.
        """
        # For template, just return the state unchanged
        return state

    @classmethod
    def get_dependencies(cls) -> dict:
        """
        Declare required and optional tool dependencies for this node, with version constraints.
        All tool names must use canonical *_KEY constants (see standards rule: no string literals).
        """
        return {
            "tools": [
                BOOTSTRAP_KEY,
                BACKEND_SELECTION_KEY,
                HEALTH_CHECK_KEY,
                INPUT_VALIDATION_KEY,
            ],
            "optional": [
                OUTPUT_FIELD_KEY
            ],
            "versions": {
                # Example: BACKEND_SELECTION_KEY: ">=1.0.0,<2.0.0"
            }
        }

    def run_cli_command(self, cli_command: ModelCliCommand) -> int:
        """
        Delegate CLI command execution to the ToolCliCommands instance.
        """
        return self.cli_commands_tool.run_command(cli_command)

def get_introspection() -> dict:
    """Get introspection data for the template node."""
    return NodeKafkaEventBus.get_introspection_response()

def main(event_bus=None):
    import argparse
    import yaml
    from .tools.tool_bootstrap import tool_bootstrap
    from .tools.tool_health_check import tool_health_check
    from .tools.tool_compute_output_field import tool_compute_output_field
    from .models.state import NodeKafkaEventBusNodeInputState, NodeKafkaEventBusNodeOutputState, ModelEventBusOutputField
    from omnibase.tools.tool_input_validation import ToolInputValidation
    from .registry.registry_kafka_event_bus import RegistryKafkaEventBus
    from .tools.tool_backend_selection import ToolBackendSelection
    from omnibase.model.model_event_bus_config import ModelEventBusConfig
    from omnibase.constants import BACKEND_SELECTION_KEY, BOOTSTRAP_KEY, HEALTH_CHECK_KEY, INPUT_VALIDATION_KEY, OUTPUT_FIELD_KEY

    config = ModelEventBusConfig.default()
    scenario_path = os.environ.get("ONEX_SCENARIO_PATH")
    fallback_tools = None
    if not (scenario_path and os.path.exists(scenario_path)):
        from .tools.tool_kafka_event_bus import KafkaEventBus
        from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
        fallback_tools = {"kafka": KafkaEventBus, "inmemory": InMemoryEventBus}
    registry = registry_resolver_tool.resolve_registry(RegistryKafkaEventBus, scenario_path=scenario_path, fallback_tools=fallback_tools)

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
        event_bus=event_bus,
        config=config,
        skip_subscribe=False,
        registry=registry,
        registry_resolver=registry_resolver_tool,
    )
    parser = argparse.ArgumentParser(description="Kafka Event Bus Node CLI")
    parser.add_argument(SERVE_ARG, action=STORE_TRUE, help="Run the node event loop (sync)")
    parser.add_argument(SERVE_ASYNC_ARG, action=STORE_TRUE, help="[STUB] Run the node event loop (async, not yet implemented)")
    parser.add_argument(DRY_RUN_ARG, action=STORE_TRUE, help="[Not applicable: this node has no side effects]")
    parser.add_argument("--scenario", type=str, default=None, help="Path to scenario YAML for scenario-driven registry injection.")
    args, unknown = parser.parse_known_args()
    if args.scenario:
        os.environ["ONEX_SCENARIO_PATH"] = args.scenario
    if args.serve_async:
        logging.warning("[STUB] --serve-async is not yet implemented. Async CLI support is planned for a future milestone.")
        print("[STUB] --serve-async is not yet implemented. See README for details.")
        # TODO: Implement async event loop for node in future milestone
        return node
    if args.dry_run:
        print("[DRY RUN] Not applicable: this node has no side effects to prevent. Exiting.")
        sys.exit(0)
    if args.serve:
        # Existing sync event loop logic (if any)
        pass
    return node

if __name__ == MAIN_MODULE_NAME:
    main()
