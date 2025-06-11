from omnibase.protocol.protocol_cli_commands import ProtocolCliCommands
from ..models.model_cli_command import ModelCliCommand
from ..enums.enum_node_kafka_command import NodeKafkaCommandEnum
from ..enums.enum_node_kafka_arg import NodeKafkaArgEnum
from omnibase.enums.enum_node_arg import NodeArgEnum
from ..models.state import NodeKafkaEventBusNodeOutputState, ModelEventBusOutputField
from omnibase.enums.onex_status import OnexStatus
from ...constants import NODE_KAFKA_EVENT_BUS_SUCCESS_MSG, NODE_KAFKA_EVENT_BUS_SUCCESS_EVENT_MSG, INPUT_VALIDATION_SUCCEEDED_MSG, INPUT_REQUIRED_FIELD_ERROR_TEMPLATE, INPUT_MISSING_REQUIRED_FIELD_ERROR
from ..error_codes import NodeKafkaEventBusNodeErrorCode

class ToolCliCommands(ProtocolCliCommands):
    """
    Implements ProtocolCliCommands for CLI command operations in the kafka node.
    Handles execution of CLI commands using canonical models and enums.
    """
    def run_command(self, command: ModelCliCommand) -> NodeKafkaEventBusNodeOutputState:
        """
        Run a CLI command with the given arguments.
        Args:
            command (ModelCliCommand): The command model to run.
        Returns:
            NodeKafkaEventBusNodeOutputState: The output state of the command.
        """
        # Example: handle RUN and BOOTSTRAP commands
        if command.command_name == NodeKafkaCommandEnum.RUN:
            # Simulate output field creation and success
            print(f"[ToolCliCommands] Running kafka node with args: {command.args}")
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
            print(output.model_dump())
            return output
        elif command.command_name == NodeKafkaCommandEnum.BOOTSTRAP:
            print(f"[ToolCliCommands] Bootstrapping kafka node with args: {command.args}")
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
            print(output.model_dump())
            return output
        else:
            print(f"[ToolCliCommands] Unknown command: {command.command_name} [ErrorCode: {NodeKafkaEventBusNodeErrorCode.UNSUPPORTED_OPERATION.value}]")
            # Return a model with error status
            output = NodeKafkaEventBusNodeOutputState(
                version="1.0.0",
                status=OnexStatus.ERROR,
                message=f"Unknown command: {command.command_name}",
                output_field=None,
            )
            return output 