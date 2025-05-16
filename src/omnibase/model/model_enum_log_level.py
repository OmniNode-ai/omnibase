from enum import Enum


class LogLevelEnum(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SeverityLevelEnum(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    CRITICAL = "critical"
    SUCCESS = "success"
    UNKNOWN = "unknown"
