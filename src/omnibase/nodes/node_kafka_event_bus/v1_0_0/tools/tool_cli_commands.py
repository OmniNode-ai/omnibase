from omnibase.protocol.protocol_cli_commands import ProtocolCliCommands
from ..models.model_cli_command import ModelCliCommand, MessageArgument, GroupIdArgument, TopicArgument
from ..enums.enum_node_kafka_command import NodeKafkaCommandEnum
from ..enums.enum_node_kafka_arg import NodeKafkaArgEnum
from omnibase.enums.enum_node_arg import NodeArgEnum
from ..models.state import KafkaEventBusOutputState, ModelEventBusOutputField
from omnibase.enums.onex_status import OnexStatus
from ...constants import NODE_KAFKA_EVENT_BUS_SUCCESS_MSG, NODE_KAFKA_EVENT_BUS_SUCCESS_EVENT_MSG, INPUT_VALIDATION_SUCCEEDED_MSG, INPUT_REQUIRED_FIELD_ERROR_TEMPLATE, INPUT_MISSING_REQUIRED_FIELD_ERROR
from ..error_codes import NodeKafkaEventBusNodeErrorCode
from typing import Union, Any
import uuid

class ToolCliCommands(ProtocolCliCommands):
    """
    Canonical CLI commands tool for the kafka node.
    Implements the ProtocolCliCommands interface with kafka-specific logic.
    """

    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    def run_command(self, command: ModelCliCommand) -> KafkaEventBusOutputState:
        """
        Execute a CLI command and return the output state.
        Uses secure typed arguments for validation.
        """
        try:
            if command.command_name == NodeKafkaCommandEnum.SEND:
                return self._handle_send_command(command)
            elif command.command_name == NodeKafkaCommandEnum.CLEANUP:
                return self._handle_cleanup_command(command)
            elif command.command_name == NodeKafkaCommandEnum.LIST_GROUPS:
                return self._handle_list_groups_command(command)
            elif command.command_name == NodeKafkaCommandEnum.DELETE_GROUP:
                return self._handle_delete_group_command(command)
            elif command.command_name == NodeKafkaCommandEnum.LIST_TOPICS:
                return self._handle_list_topics_command(command)
            elif command.command_name == NodeKafkaCommandEnum.DELETE_TOPIC:
                return self._handle_delete_topic_command(command)
            elif command.command_name == NodeKafkaCommandEnum.HEALTH_CHECK:
                return self._handle_health_check_command(command)
            else:
                return KafkaEventBusOutputState(
                    version="1.0.0",
                    status=OnexStatus.ERROR,
                    message=f"Unknown command: {command.command_name}",
                    output_field=ModelEventBusOutputField(
                        backend="None",
                        processed=None,
                        integration=None,
                        custom=None
                    ),
                )
        except Exception as e:
            return KafkaEventBusOutputState(
                version="1.0.0",
                status=OnexStatus.ERROR,
                message=f"Error executing command: {str(e)}",
                output_field=ModelEventBusOutputField(
                    backend="None",
                    processed=None,
                    integration=None,
                    custom=None
                ),
            )

    def _handle_send_command(self, command: ModelCliCommand) -> KafkaEventBusOutputState:
        """Handle send command with secure message extraction."""
        try:
            # Extract message from typed_args securely
            message = None
            for typed_arg in command.typed_args:
                if isinstance(typed_arg, MessageArgument):
                    message = typed_arg.value
                    break
            
            if not message:
                return KafkaEventBusOutputState(
                    version="1.0.0",
                    status=OnexStatus.ERROR,
                    message="No message provided for SEND command",
                    output_field=ModelEventBusOutputField(
                        backend="None",
                        processed=None,
                        integration=None,
                        custom=None
                    ),
                )

            if self.event_bus:
                # Create event with proper correlation ID
                from omnibase.model.model_onex_event import OnexEvent
                from omnibase.enums.enum_onex_event_type import OnexEventTypeEnum
                from omnibase.model.model_onex_event_metadata import OnexEventMetadataModel
                from datetime import datetime, timezone

                correlation_id = str(uuid.uuid4())
                event = OnexEvent(
                    node_id="cli",
                    event_type=OnexEventTypeEnum.TOOL_PROXY_INVOKE,
                    correlation_id=correlation_id,
                    timestamp=datetime.now(timezone.utc),
                    metadata=OnexEventMetadataModel(
                        command_name="send",
                        args=[f"--message={message}"],  # Secure: only validated message
                        log_format="json"
                    )
                )

                # Publish event
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                loop.run_until_complete(self.event_bus.publish_async(event))
                
                return KafkaEventBusOutputState(
                    version="1.0.0",
                    status=OnexStatus.SUCCESS,
                    message=f"Message sent successfully: {message[:50]}..." if len(message) > 50 else f"Message sent: {message}",
                    output_field=ModelEventBusOutputField(
                        backend="KafkaEventBus",
                        processed=True,
                        integration="kafka",
                        custom={"correlation_id": correlation_id, "message_length": len(message)}
                    ),
                )
            else:
                return KafkaEventBusOutputState(
                    version="1.0.0",
                    status=OnexStatus.ERROR,
                    message="No event bus available for SEND command",
                    output_field=ModelEventBusOutputField(
                        backend="None",
                        processed=None,
                        integration=None,
                        custom=None
                    ),
                )
        except Exception as e:
            return KafkaEventBusOutputState(
                version="1.0.0",
                status=OnexStatus.ERROR,
                message=f"Error in SEND command: {str(e)}",
                output_field=ModelEventBusOutputField(
                    backend="None",
                    processed=None,
                    integration=None,
                    custom=None
                ),
            )

    def _handle_cleanup_command(self, command: ModelCliCommand) -> KafkaEventBusOutputState:
        """Handle cleanup of Kafka resources."""
        try:
            # Get event bus instance if available
            if hasattr(self, 'event_bus') and self.event_bus:
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Use the new cleanup_resources method if available
                if hasattr(self.event_bus, 'cleanup_resources'):
                    cleanup_summary = loop.run_until_complete(self.event_bus.cleanup_resources())
                    return KafkaEventBusOutputState(
                        version="1.0.0",
                        status=OnexStatus.SUCCESS,
                        message=f"Cleanup completed: {cleanup_summary}",
                        output_field=ModelEventBusOutputField(
                            backend="KafkaEventBus",
                            processed=True,
                            integration="kafka",
                            custom=cleanup_summary
                        ),
                    )
                else:
                    return KafkaEventBusOutputState(
                        version="1.0.0",
                        status=OnexStatus.ERROR,
                        message="Event bus does not support cleanup operations",
                        output_field=ModelEventBusOutputField(
                            backend="None",
                            processed=None,
                            integration=None,
                            custom=None
                        ),
                    )
            else:
                return KafkaEventBusOutputState(
                    version="1.0.0",
                    status=OnexStatus.ERROR,
                    message="No event bus available for CLEANUP command",
                    output_field=ModelEventBusOutputField(
                        backend="None",
                        processed=None,
                        integration=None,
                        custom=None
                    ),
                )
        except Exception as e:
            return KafkaEventBusOutputState(
                version="1.0.0",
                status=OnexStatus.ERROR,
                message=f"Error in CLEANUP command: {str(e)}",
                output_field=ModelEventBusOutputField(
                    backend="None",
                    processed=None,
                    integration=None,
                    custom=None
                ),
            )

    def _handle_list_groups_command(self, command: ModelCliCommand) -> KafkaEventBusOutputState:
        """Handle listing consumer groups."""
        try:
            # Get event bus instance if available
            if hasattr(self, 'event_bus') and self.event_bus:
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Use the new list_consumer_groups method
                if hasattr(self.event_bus, 'list_consumer_groups'):
                    groups_info = loop.run_until_complete(self.event_bus.list_consumer_groups())
                    return KafkaEventBusOutputState(
                        version="1.0.0",
                        status=OnexStatus.SUCCESS,
                        message=f"Listed {len(groups_info)} consumer groups",
                        output_field=ModelEventBusOutputField(
                            backend="KafkaEventBus",
                            processed=True,
                            integration="kafka",
                            custom={"consumer_groups": groups_info}
                        ),
                    )
                else:
                    return KafkaEventBusOutputState(
                        version="1.0.0",
                        status=OnexStatus.ERROR,
                        message="Event bus does not support list_consumer_groups operation",
                        output_field=ModelEventBusOutputField(
                            backend="None",
                            processed=None,
                            integration=None,
                            custom=None
                        ),
                    )
            else:
                return KafkaEventBusOutputState(
                    version="1.0.0",
                    status=OnexStatus.ERROR,
                    message="No event bus available for LIST_GROUPS command",
                    output_field=ModelEventBusOutputField(
                        backend="None",
                        processed=None,
                        integration=None,
                        custom=None
                    ),
                )
        except Exception as e:
            return KafkaEventBusOutputState(
                version="1.0.0",
                status=OnexStatus.ERROR,
                message=f"Error in LIST_GROUPS command: {str(e)}",
                output_field=ModelEventBusOutputField(
                    backend="None",
                    processed=None,
                    integration=None,
                    custom=None
                ),
            )

    def _handle_delete_group_command(self, command: ModelCliCommand) -> KafkaEventBusOutputState:
        """Handle deleting a consumer group."""
        try:
            # Extract group_id from command arguments
            group_id = None
            for arg in command.arguments:
                if hasattr(arg, 'value') and isinstance(arg, GroupIdArgument):
                    group_id = arg.value
                    break
            
            if not group_id:
                return KafkaEventBusOutputState(
                    version="1.0.0",
                    status=OnexStatus.ERROR,
                    message="DELETE_GROUP command requires --group-id argument",
                    output_field=ModelEventBusOutputField(
                        backend="None",
                        processed=None,
                        integration=None,
                        custom=None
                    ),
                )
            
            # Get event bus instance if available
            if hasattr(self, 'event_bus') and self.event_bus:
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Use the new delete_consumer_group method
                if hasattr(self.event_bus, 'delete_consumer_group'):
                    success = loop.run_until_complete(self.event_bus.delete_consumer_group(group_id))
                    if success:
                        return KafkaEventBusOutputState(
                            version="1.0.0",
                            status=OnexStatus.SUCCESS,
                            message=f"Successfully deleted consumer group: {group_id}",
                            output_field=ModelEventBusOutputField(
                                backend="KafkaEventBus",
                                processed=True,
                                integration="kafka",
                                custom={"deleted_group": group_id}
                            ),
                        )
                    else:
                        return KafkaEventBusOutputState(
                            version="1.0.0",
                            status=OnexStatus.ERROR,
                            message=f"Failed to delete consumer group: {group_id}",
                            output_field=ModelEventBusOutputField(
                                backend="KafkaEventBus",
                                processed=False,
                                integration="kafka",
                                custom=None
                            ),
                        )
                else:
                    return KafkaEventBusOutputState(
                        version="1.0.0",
                        status=OnexStatus.ERROR,
                        message="Event bus does not support delete_consumer_group operation",
                        output_field=ModelEventBusOutputField(
                            backend="None",
                            processed=None,
                            integration=None,
                            custom=None
                        ),
                    )
            else:
                return KafkaEventBusOutputState(
                    version="1.0.0",
                    status=OnexStatus.ERROR,
                    message="No event bus available for DELETE_GROUP command",
                    output_field=ModelEventBusOutputField(
                        backend="None",
                        processed=None,
                        integration=None,
                        custom=None
                    ),
                )
        except Exception as e:
            return KafkaEventBusOutputState(
                version="1.0.0",
                status=OnexStatus.ERROR,
                message=f"Error in DELETE_GROUP command: {str(e)}",
                output_field=ModelEventBusOutputField(
                    backend="None",
                    processed=None,
                    integration=None,
                    custom=None
                ),
            )

    def _handle_list_topics_command(self, command: ModelCliCommand) -> KafkaEventBusOutputState:
        """Handle listing topics."""
        try:
            # Get event bus instance if available
            if hasattr(self, 'event_bus') and self.event_bus:
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Use the new list_topics method
                if hasattr(self.event_bus, 'list_topics'):
                    topics_info = loop.run_until_complete(self.event_bus.list_topics())
                    return KafkaEventBusOutputState(
                        version="1.0.0",
                        status=OnexStatus.SUCCESS,
                        message=f"Listed {len(topics_info)} topics",
                        output_field=ModelEventBusOutputField(
                            backend="KafkaEventBus",
                            processed=True,
                            integration="kafka",
                            custom={"topics": topics_info}
                        ),
                    )
                else:
                    return KafkaEventBusOutputState(
                        version="1.0.0",
                        status=OnexStatus.ERROR,
                        message="Event bus does not support list_topics operation",
                        output_field=ModelEventBusOutputField(
                            backend="None",
                            processed=None,
                            integration=None,
                            custom=None
                        ),
                    )
            else:
                return KafkaEventBusOutputState(
                    version="1.0.0",
                    status=OnexStatus.ERROR,
                    message="No event bus available for LIST_TOPICS command",
                    output_field=ModelEventBusOutputField(
                        backend="None",
                        processed=None,
                        integration=None,
                        custom=None
                    ),
                )
        except Exception as e:
            return KafkaEventBusOutputState(
                version="1.0.0",
                status=OnexStatus.ERROR,
                message=f"Error in LIST_TOPICS command: {str(e)}",
                output_field=ModelEventBusOutputField(
                    backend="None",
                    processed=None,
                    integration=None,
                    custom=None
                ),
            )

    def _handle_delete_topic_command(self, command: ModelCliCommand) -> KafkaEventBusOutputState:
        """Handle deleting a topic."""
        try:
            # Extract topic from command arguments
            topic_name = None
            for arg in command.arguments:
                if hasattr(arg, 'value') and isinstance(arg, TopicArgument):
                    topic_name = arg.value
                    break
            
            if not topic_name:
                return KafkaEventBusOutputState(
                    version="1.0.0",
                    status=OnexStatus.ERROR,
                    message="DELETE_TOPIC command requires --topic argument",
                    output_field=ModelEventBusOutputField(
                        backend="None",
                        processed=None,
                        integration=None,
                        custom=None
                    ),
                )
            
            # Get event bus instance if available
            if hasattr(self, 'event_bus') and self.event_bus:
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Use the new delete_topic method
                if hasattr(self.event_bus, 'delete_topic'):
                    success = loop.run_until_complete(self.event_bus.delete_topic(topic_name))
                    if success:
                        return KafkaEventBusOutputState(
                            version="1.0.0",
                            status=OnexStatus.SUCCESS,
                            message=f"Successfully deleted topic: {topic_name}",
                            output_field=ModelEventBusOutputField(
                                backend="KafkaEventBus",
                                processed=True,
                                integration="kafka",
                                custom={"deleted_topic": topic_name}
                            ),
                        )
                    else:
                        return KafkaEventBusOutputState(
                            version="1.0.0",
                            status=OnexStatus.ERROR,
                            message=f"Failed to delete topic: {topic_name}",
                            output_field=ModelEventBusOutputField(
                                backend="KafkaEventBus",
                                processed=False,
                                integration="kafka",
                                custom=None
                            ),
                        )
                else:
                    return KafkaEventBusOutputState(
                        version="1.0.0",
                        status=OnexStatus.ERROR,
                        message="Event bus does not support delete_topic operation",
                        output_field=ModelEventBusOutputField(
                            backend="None",
                            processed=None,
                            integration=None,
                            custom=None
                        ),
                    )
            else:
                return KafkaEventBusOutputState(
                    version="1.0.0",
                    status=OnexStatus.ERROR,
                    message="No event bus available for DELETE_TOPIC command",
                    output_field=ModelEventBusOutputField(
                        backend="None",
                        processed=None,
                        integration=None,
                        custom=None
                    ),
                )
        except Exception as e:
            return KafkaEventBusOutputState(
                version="1.0.0",
                status=OnexStatus.ERROR,
                message=f"Error in DELETE_TOPIC command: {str(e)}",
                output_field=ModelEventBusOutputField(
                    backend="None",
                    processed=None,
                    integration=None,
                    custom=None
                ),
            )

    def _handle_health_check_command(self, command: ModelCliCommand) -> KafkaEventBusOutputState:
        """Handle health check."""
        try:
            if hasattr(self, 'event_bus') and self.event_bus:
                # Check if event bus is connected
                is_connected = getattr(self.event_bus, 'connected', False)
                return KafkaEventBusOutputState(
                    version="1.0.0",
                    status=OnexStatus.SUCCESS if is_connected else OnexStatus.ERROR,
                    message=f"Event bus health: {'Connected' if is_connected else 'Disconnected'}",
                    output_field=ModelEventBusOutputField(
                        backend="KafkaEventBus",
                        processed=True,
                        integration="kafka",
                        custom={"connected": is_connected}
                    ),
                )
            else:
                return KafkaEventBusOutputState(
                    version="1.0.0",
                    status=OnexStatus.ERROR,
                    message="No event bus available for health check",
                    output_field=ModelEventBusOutputField(
                        backend="None",
                        processed=None,
                        integration=None,
                        custom=None
                    ),
                )
        except Exception as e:
            return KafkaEventBusOutputState(
                version="1.0.0",
                status=OnexStatus.ERROR,
                message=f"Error in HEALTH_CHECK command: {str(e)}",
                output_field=ModelEventBusOutputField(
                    backend="None",
                    processed=None,
                    integration=None,
                    custom=None
                ),
            ) 