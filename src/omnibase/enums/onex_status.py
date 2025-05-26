# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: onex_status.py
# version: 1.0.0
# uuid: 0846476c-4ef9-47b3-9417-4881768fe156
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.164553
# last_modified_at: 2025-05-26T18:58:45.709363
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 3f58cba1abbb25d1410147030d64fa031965590b0bd40e6a7c533cc1da62ea59
# entrypoint: python@onex_status.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.onex_status
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
