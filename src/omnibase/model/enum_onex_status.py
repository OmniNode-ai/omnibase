# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: enum_onex_status.py
# version: 1.0.0
# uuid: 0846476c-4ef9-47b3-9417-4881768fe156
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.164553
# last_modified_at: 2025-05-21T16:42:46.066695
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 4dcb3630304a4cbd602b78cc3107fc290551445b125378fd2c67f0d9903f233e
# entrypoint: python@enum_onex_status.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.enum_onex_status
# meta_type: tool
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
