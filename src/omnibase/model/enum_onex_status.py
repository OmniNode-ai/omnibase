# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: f11ac700-7af0-4aa8-84b7-c706b710080a
# name: enum_onex_status.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:54.438413
# last_modified_at: 2025-05-19T16:19:54.438417
# description: Stamped Python file: enum_onex_status.py
# state_contract: none
# lifecycle: active
# hash: 883def883c1944adf9d5c6e2bf2c106bfe3ddff58ef0dd0c4ee11633ff911362
# entrypoint: {'type': 'python', 'target': 'enum_onex_status.py'}
# namespace: onex.stamped.enum_onex_status.py
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
