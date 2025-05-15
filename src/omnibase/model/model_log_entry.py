from pydantic import BaseModel
from src.omnibase.model.model_enum_log_level import LogLevelEnum
from src.omnibase.model.model_base_error import BaseErrorModel

class LogEntryModel(BaseErrorModel):
    message: str
    level: LogLevelEnum = LogLevelEnum.INFO 