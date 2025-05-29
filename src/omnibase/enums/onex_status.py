# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:07.792634'
# description: Stamped by PythonHandler
# entrypoint: python://onex_status.py
# hash: 86bf176ee8aedb75bd63eb6c8062ddc0f395e80e6ac77864ef7b410a793678b3
# last_modified_at: '2025-05-29T11:50:10.770813+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: onex_status.py
# namespace: omnibase.onex_status
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 071d0cf7-cba8-404c-b30c-00d52b6d3c1a
# version: 1.0.0
# === /OmniNode:Metadata ===


from enum import Enum


class OnexStatus(str, Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    SKIPPED = "skipped"
    FIXED = "fixed"
    PARTIAL = "partial"
    INFO = "info"
    UNKNOWN = "unknown"
