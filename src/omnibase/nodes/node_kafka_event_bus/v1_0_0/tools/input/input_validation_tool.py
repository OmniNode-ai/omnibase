from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync, make_log_context
from pydantic import ValidationError
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models.state import NodeKafkaEventBusInputState, NodeKafkaEventBusOutputState
from omnibase.enums.onex_status import OnexStatus
from omnibase.model.model_semver import SemVerModel
from omnibase.nodes.node_kafka_event_bus.protocols.input_validation_tool_protocol import InputValidationToolProtocol
from typing import Optional, Tuple
from omnibase.model.model_output_field import OnexFieldModel

class InputValidationTool(InputValidationToolProtocol):
    def validate_input_state(
        self,
        input_state: dict,
        semver: SemVerModel,
        event_bus,
        correlation_id: str = None
    ) -> Tuple[Optional[NodeKafkaEventBusInputState], Optional[NodeKafkaEventBusOutputState]]:
        """
        Validates the input_state dict against NodeKafkaEventBusInputState.
        Returns (state, None) if valid, or (None, error_output) if invalid.
        Emits log events for validation success/failure.
        """
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"Input state before validation: {input_state}",
            context=make_log_context(node_id="node_kafka_event_bus", correlation_id=correlation_id),
        )
        try:
            emit_log_event_sync(LogLevelEnum.DEBUG, f"About to instantiate NodeKafkaEventBusInputState with: {input_state}", make_log_context(node_id="node_kafka_event_bus", correlation_id=correlation_id))
            state = NodeKafkaEventBusInputState(**input_state)
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                "Input validation succeeded",
                context=make_log_context(node_id="node_kafka_event_bus", correlation_id=correlation_id),
            )
            return state, None
        except ValidationError as e:
            # Compose a more specific error message for missing required fields
            if e.errors():
                first_error = e.errors()[0]
                if first_error.get('type') == 'missing' and 'loc' in first_error:
                    loc = first_error['loc']
                    if isinstance(loc, (list, tuple)) and len(loc) > 1:
                        # Handle nested missing fields, e.g., version.major
                        missing_field = loc[-1]
                        msg = f"Input should have required field '{missing_field}'"
                    else:
                        missing_field = loc[0] if isinstance(loc, (list, tuple)) else loc
                        msg = f"Input should have required field '{missing_field}'"
                elif first_error.get('type') == 'missing':
                    msg = "Input is missing a required field"
                else:
                    msg = str(first_error.get('msg', str(e)))
            else:
                msg = str(e)
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"ValidationError in run: {msg}",
                context=make_log_context(node_id="node_kafka_event_bus", correlation_id=correlation_id),
            )
            return None, NodeKafkaEventBusOutputState(
                version=semver,
                status=OnexStatus.ERROR,
                message=msg,
                output_field=OnexFieldModel(data={}),
            )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Exception in run: {e}",
                context=make_log_context(node_id="node_kafka_event_bus", correlation_id=correlation_id),
            )
            return None, NodeKafkaEventBusOutputState(
                version=semver,
                status=OnexStatus.ERROR,
                message=str(e),
                output_field=OnexFieldModel(data={}),
            )

# Instantiate for use
input_validation_tool = InputValidationTool() 