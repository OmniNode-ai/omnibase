# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.772489'
# description: Stamped by PythonHandler
# entrypoint: python://log_level.py
# hash: 41ee08f4f6d6a7ea3ae2bf207d499a18e9eb3811db15127fffb11414289a2b4a
# last_modified_at: '2025-05-29T11:50:10.759851+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: log_level.py
# namespace: omnibase.log_level
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 56bbeb2e-89f8-4bde-a006-09a645eb73e0
# version: 1.0.0
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
