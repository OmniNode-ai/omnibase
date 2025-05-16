from omnibase.model.model_base_error import BaseErrorModel
from omnibase.model.model_enum_log_level import LogLevelEnum


class LogEntryModel(BaseErrorModel):
    message: str
    level: LogLevelEnum = LogLevelEnum.INFO
