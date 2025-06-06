from pathlib import Path
from typing import Optional, Tuple

from pydantic import ValidationError

from omnibase.constants import (
    BACKEND_ERROR_VALUE,
    BACKEND_KEY,
    ERROR_LOC_KEY,
    ERROR_MSG_KEY,
    ERROR_TYPE_KEY,
)
from omnibase.enums.log_level import LogLevelEnum
from omnibase.enums.onex_status import OnexStatus
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_output_field import OnexFieldModel
from omnibase.model.model_output_field_utils import make_output_field
from omnibase.model.model_semver import SemVerModel, parse_input_state_version
from omnibase.nodes.node_kafka_event_bus.constants import (
    INPUT_MISSING_REQUIRED_FIELD_ERROR,
    INPUT_REQUIRED_FIELD_ERROR_TEMPLATE,
    INPUT_VALIDATION_SUCCEEDED_MSG,
    NODE_KAFKA_EVENT_BUS_ID,
)
from omnibase.nodes.node_kafka_event_bus.protocols.input_validation_tool_protocol import (
    InputValidationToolProtocol,
)
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import (
    ModelKafkaEventBusInputState,
    ModelKafkaEventBusOutputField,
    ModelKafkaEventBusOutputState,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import (
    emit_log_event_sync,
    make_log_context,
)


class InputValidationTool(InputValidationToolProtocol):
    def validate_input_state(
        self, input_state: dict, semver, event_bus, correlation_id: str = None
    ) -> Tuple[
        Optional[ModelKafkaEventBusInputState], Optional[ModelKafkaEventBusOutputState]
    ]:
        """
        Validates the input_state dict against ModelKafkaEventBusInputState.
        Returns (state, None) if valid, or (None, error_output) if invalid.
        Emits log events for validation success/failure.
        """
        from omnibase.model.model_node_metadata import NodeMetadataBlock
        from omnibase.model.model_semver import SemVerModel

        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"Input state before validation: {input_state}",
            context=make_log_context(
                node_id=NODE_KAFKA_EVENT_BUS_ID, correlation_id=correlation_id
            ),
        )
        try:
            emit_log_event_sync(
                LogLevelEnum.DEBUG,
                f"About to instantiate ModelKafkaEventBusInputState with: {input_state}",
                make_log_context(
                    node_id=NODE_KAFKA_EVENT_BUS_ID, correlation_id=correlation_id
                ),
            )
            state = ModelKafkaEventBusInputState(**input_state)
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                INPUT_VALIDATION_SUCCEEDED_MSG,
                context=make_log_context(
                    node_id=NODE_KAFKA_EVENT_BUS_ID, correlation_id=correlation_id
                ),
            )
            return state, None
        except ValidationError as e:
            # Compose a more specific error message for missing required fields
            if e.errors():
                first_error = e.errors()[0]
                if (
                    first_error.get(ERROR_TYPE_KEY) == "missing"
                    and ERROR_LOC_KEY in first_error
                ):
                    loc = first_error[ERROR_LOC_KEY]
                    if isinstance(loc, (list, tuple)) and len(loc) > 1:
                        # Handle nested missing fields, e.g., version.major
                        missing_field = loc[-1]
                        msg = INPUT_REQUIRED_FIELD_ERROR_TEMPLATE.format(
                            missing_field=missing_field
                        )
                    else:
                        missing_field = (
                            loc[0] if isinstance(loc, (list, tuple)) else loc
                        )
                        msg = INPUT_REQUIRED_FIELD_ERROR_TEMPLATE.format(
                            missing_field=missing_field
                        )
                elif first_error.get(ERROR_TYPE_KEY) == "missing":
                    msg = INPUT_MISSING_REQUIRED_FIELD_ERROR
                else:
                    msg = str(first_error.get(ERROR_MSG_KEY, str(e)))
            else:
                msg = str(e)
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"ValidationError in run: {msg}",
                context=make_log_context(
                    node_id=NODE_KAFKA_EVENT_BUS_ID, correlation_id=correlation_id
                ),
            )
            return None, ModelKafkaEventBusOutputState(
                version=parse_input_state_version(input_state, semver),
                status=OnexStatus.ERROR,
                message=msg,
                output_field=make_output_field(
                    {BACKEND_KEY: BACKEND_ERROR_VALUE}, ModelKafkaEventBusOutputField
                ),
            )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Exception in run: {e}",
                context=make_log_context(
                    node_id=NODE_KAFKA_EVENT_BUS_ID, correlation_id=correlation_id
                ),
            )
            return None, ModelKafkaEventBusOutputState(
                version=parse_input_state_version(input_state, semver),
                status=OnexStatus.ERROR,
                message=str(e),
                output_field=make_output_field(
                    {BACKEND_KEY: BACKEND_ERROR_VALUE}, ModelKafkaEventBusOutputField
                ),
            )


# Instantiate for use
input_validation_tool = InputValidationTool()
