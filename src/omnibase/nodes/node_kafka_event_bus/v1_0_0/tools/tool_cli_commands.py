from omnibase.protocol.protocol_cli_commands import ProtocolCliCommands
from ..models.model_cli_command import ModelCliCommand
from ..enums.enum_node_kafka_command import NodeKafkaCommandEnum
from ..enums.enum_node_kafka_arg import NodeKafkaArgEnum
from omnibase.enums.enum_node_arg import NodeArgEnum
from ..models.state import NodeKafkaEventBusNodeOutputState, ModelEventBusOutputField
from omnibase.enums.onex_status import OnexStatus
from ...constants import NODE_KAFKA_EVENT_BUS_SUCCESS_MSG, NODE_KAFKA_EVENT_BUS_SUCCESS_EVENT_MSG, INPUT_VALIDATION_SUCCEEDED_MSG, INPUT_REQUIRED_FIELD_ERROR_TEMPLATE, INPUT_MISSING_REQUIRED_FIELD_ERROR
from ..error_codes import NodeKafkaEventBusNodeErrorCode
from typing import Union, Any

class ToolCliCommands(ProtocolCliCommands):
    """
    Implements ProtocolCliCommands for CLI command operations in the kafka node.
    Handles execution of CLI commands using canonical models and enums.
    """
    def run_command(self, command: Union[ModelCliCommand, Any]) -> NodeKafkaEventBusNodeOutputState:
        """
        Run a CLI command with the given arguments.
        Args:
            command (Union[ModelCliCommand, Any]): The command model to run.
        Returns:
            NodeKafkaEventBusNodeOutputState: The output state of the command.
        """
        # Example: handle RUN and BOOTSTRAP commands
        if command.command_name == NodeKafkaCommandEnum.RUN:
            # Simulate output field creation and success
            output_field = ModelEventBusOutputField(
                backend="KafkaEventBus",
                processed="test",
                integration=None,
                custom=None
            )
            output = NodeKafkaEventBusNodeOutputState(
                version="1.0.0",
                status=OnexStatus.SUCCESS,
                message=NODE_KAFKA_EVENT_BUS_SUCCESS_MSG,
                output_field=output_field,
            )
            return output
        elif command.command_name == NodeKafkaCommandEnum.BOOTSTRAP:
            output_field = ModelEventBusOutputField(
                backend="KafkaEventBus",
                processed="bootstrap",
                integration=None,
                custom=None
            )
            output = NodeKafkaEventBusNodeOutputState(
                version="1.0.0",
                status=OnexStatus.SUCCESS,
                message="Kafka bootstrap completed: bootstrap successful.",
                output_field=output_field,
            )
            return output
        elif command.command_name == NodeKafkaCommandEnum.SEND:
            # Extract message argument
            message = None
            for arg in command.args:
                if isinstance(arg, str) and arg.startswith("--message="):
                    message = arg.split("=", 1)[1]
                elif hasattr(arg, 'value') and str(arg).startswith("--message"):
                    message = getattr(arg, 'value', None)
            if not message:
                output = NodeKafkaEventBusNodeOutputState(
                    version="1.0.0",
                    status=OnexStatus.ERROR,
                    message="SEND command missing --message argument",
                    output_field=None,
                )
                return output
            from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
            from omnibase.enums.log_level import LogLevelEnum
            from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync, make_log_context
            try:
                from ..constants import NODE_KAFKA_EVENT_BUS_ID
                node_id = NODE_KAFKA_EVENT_BUS_ID
            except ImportError:
                node_id = "node_kafka_event_bus"
            emit_log_event_sync(LogLevelEnum.DEBUG, f"[ToolCliCommands] Using node_id for event: {node_id}", context=make_log_context(node_id="ToolCliCommands"))
            emit_log_event_sync(LogLevelEnum.DEBUG, f"[ToolCliCommands] Preparing to send event with message: {message}", context=make_log_context(node_id="ToolCliCommands"))
            # Construct event
            event_metadata = {
                "command_name": "send",
                "args": [f"--message={message}"]
            }
            event = OnexEvent(
                node_id=node_id,
                event_type=OnexEventTypeEnum.TOOL_PROXY_INVOKE,
                correlation_id=None,
                metadata=event_metadata,
            )
            try:
                # Publish event to event bus (assume self.event_bus is available)
                if hasattr(self, 'event_bus') and self.event_bus:
                    import asyncio
                    if hasattr(self.event_bus, 'publish_async'):
                        try:
                            loop = asyncio.get_event_loop()
                        except RuntimeError:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                        if loop.is_running():
                            coro = self.event_bus.publish_async(event)
                            task = asyncio.ensure_future(coro, loop=loop)
                            loop.run_until_complete(asyncio.gather(task))
                        else:
                            loop.run_until_complete(self.event_bus.publish_async(event))
                    else:
                        self.event_bus.publish(event)
                    emit_log_event_sync(LogLevelEnum.INFO, f"[ToolCliCommands] Event sent successfully", context=make_log_context(node_id="ToolCliCommands"))
                    output = NodeKafkaEventBusNodeOutputState(
                        version="1.0.0",
                        status=OnexStatus.SUCCESS,
                        message="Event sent successfully",
                        output_field=None,
                    )
                    return output
                else:
                    emit_log_event_sync(LogLevelEnum.ERROR, f"[ToolCliCommands] No event bus available for SEND command", context=make_log_context(node_id="ToolCliCommands"))
                    output = NodeKafkaEventBusNodeOutputState(
                        version="1.0.0",
                        status=OnexStatus.ERROR,
                        message="No event bus available for SEND command",
                        output_field=None,
                    )
                    return output
            except Exception as exc:
                emit_log_event_sync(LogLevelEnum.ERROR, f"[ToolCliCommands] Exception during SEND: {exc}", context=make_log_context(node_id="ToolCliCommands"))
                output = NodeKafkaEventBusNodeOutputState(
                    version="1.0.0",
                    status=OnexStatus.ERROR,
                    message=f"Exception during SEND: {exc}",
                    output_field=None,
                )
                return output
        else:
            # Return a model with error status
            output = NodeKafkaEventBusNodeOutputState(
                version="1.0.0",
                status=OnexStatus.ERROR,
                message=f"Unknown command: {command.command_name}",
                output_field=None,
            )
            return output 