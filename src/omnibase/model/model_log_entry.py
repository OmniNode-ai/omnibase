# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 20862238-a094-4a5d-bd7d-3d0590c094e2
# name: model_log_entry.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:56.173812
# last_modified_at: 2025-05-19T16:19:56.173815
# description: Stamped Python file: model_log_entry.py
# state_contract: none
# lifecycle: active
# hash: 0b29ecda6c8be1418c4939d28877e9f1d8e1af48b9401fe96887a757205b3e6d
# entrypoint: {'type': 'python', 'target': 'model_log_entry.py'}
# namespace: onex.stamped.model_log_entry.py
# meta_type: tool
# === /OmniNode:Metadata ===

from omnibase.model.model_base_error import BaseErrorModel
from omnibase.model.model_enum_log_level import LogLevelEnum


class LogEntryModel(BaseErrorModel):
    message: str
    level: LogLevelEnum = LogLevelEnum.INFO
