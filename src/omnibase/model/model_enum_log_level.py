# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 885b8374-a255-4651-a68f-80037f0e34e0
# name: model_enum_log_level.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:58.383541
# last_modified_at: 2025-05-19T16:19:58.383546
# description: Stamped Python file: model_enum_log_level.py
# state_contract: none
# lifecycle: active
# hash: 8b7b4c5da31736ab0ca58c4dd7f042bd880938997331099e10f646d2b2b8dd54
# entrypoint: {'type': 'python', 'target': 'model_enum_log_level.py'}
# namespace: onex.stamped.model_enum_log_level.py
# meta_type: tool
# === /OmniNode:Metadata ===

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
