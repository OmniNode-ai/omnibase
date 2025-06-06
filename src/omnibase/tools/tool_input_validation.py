from typing import Any, Callable, Dict, Optional, Tuple, Type

from pydantic import ValidationError, BaseModel

from omnibase.constants import (
    BACKEND_ERROR_VALUE,
    BACKEND_KEY,
    ERROR_LOC_KEY,
    ERROR_MSG_KEY,
    ERROR_TYPE_KEY,
    INPUT_MISSING_REQUIRED_FIELD_ERROR,
    INPUT_REQUIRED_FIELD_ERROR_TEMPLATE,
    INPUT_VALIDATION_SUCCEEDED_MSG,
)
from omnibase.enums.log_level import LogLevelEnum
from omnibase.enums.onex_status import OnexStatus
from omnibase.model.model_output_field_utils import make_output_field
from omnibase.model.model_semver import parse_input_state_version
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import (
    emit_log_event_sync,
    make_log_context,
)

class ToolInputValidation:
    def __init__(
        self,
        input_model: Type[BaseModel],
        output_model: Type[BaseModel],
        output_field_model: Type[BaseModel],
        node_id: str,
        make_output_field_fn: Callable = make_output_field,
        input_validation_succeeded_msg: str = INPUT_VALIDATION_SUCCEEDED_MSG,
        input_required_field_error_template: str = INPUT_REQUIRED_FIELD_ERROR_TEMPLATE,
        input_missing_required_field_error: str = INPUT_MISSING_REQUIRED_FIELD_ERROR,
    ):
        self.input_model = input_model
        self.output_model = output_model
        self.output_field_model = output_field_model
        self.node_id = node_id
        self.make_output_field_fn = make_output_field_fn
        self.input_validation_succeeded_msg = input_validation_succeeded_msg
        self.input_required_field_error_template = input_required_field_error_template
        self.input_missing_required_field_error = input_missing_required_field_error

    def validate_input_state(
        self, input_state: dict, semver, event_bus=None, correlation_id: str = None
    ) -> Tuple[Optional[BaseModel], Optional[BaseModel]]:
        """
        Validates the input_state dict against the provided input_model.
        Returns (state, None) if valid, or (None, error_output) if invalid.
        Emits log events for validation success/failure.
        """
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"Input state before validation: {input_state}",
            context=make_log_context(
                node_id=self.node_id, correlation_id=correlation_id
            ),
        )
        try:
            emit_log_event_sync(
                LogLevelEnum.DEBUG,
                f"About to instantiate {self.input_model.__name__} with: {input_state}",
                make_log_context(
                    node_id=self.node_id, correlation_id=correlation_id
                ),
            )
            state = self.input_model(**input_state)
            emit_log_event_sync(
                LogLevelEnum.TRACE,
                self.input_validation_succeeded_msg,
                context=make_log_context(
                    node_id=self.node_id, correlation_id=correlation_id
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
                        msg = self.input_required_field_error_template.format(
                            missing_field=missing_field
                        )
                    else:
                        missing_field = (
                            loc[0] if isinstance(loc, (list, tuple)) else loc
                        )
                        msg = self.input_required_field_error_template.format(
                            missing_field=missing_field
                        )
                elif first_error.get(ERROR_TYPE_KEY) == "missing":
                    msg = self.input_missing_required_field_error
                else:
                    msg = str(first_error.get(ERROR_MSG_KEY, str(e)))
            else:
                msg = str(e)
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"ValidationError in run: {msg}",
                context=make_log_context(
                    node_id=self.node_id, correlation_id=correlation_id
                ),
            )
            version = parse_input_state_version(input_state, semver)
            return None, self.output_model(
                version=version,
                status=OnexStatus.ERROR,
                message=msg,
                output_field=self.make_output_field_fn(
                    {BACKEND_KEY: BACKEND_ERROR_VALUE}, self.output_field_model
                ),
            )
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.ERROR,
                f"Exception in run: {e}",
                context=make_log_context(
                    node_id=self.node_id, correlation_id=correlation_id
                ),
            )
            version = parse_input_state_version(input_state, semver)
            return None, self.output_model(
                version=version,
                status=OnexStatus.ERROR,
                message=str(e),
                output_field=self.make_output_field_fn(
                    {BACKEND_KEY: BACKEND_ERROR_VALUE}, self.output_field_model
                ),
            ) 