# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_enum_log_level.py
# version: 1.0.0
# uuid: 299284c9-0012-4472-b859-e23afd82f823
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165202
# last_modified_at: 2025-05-21T16:42:46.054460
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: f9b90f8d4aa8bea3340eadc92ced4469df5dbee5af607ff2dbe9765c9d66f4da
# entrypoint: python@model_enum_log_level.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_enum_log_level
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
