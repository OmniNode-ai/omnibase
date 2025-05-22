# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_log_entry.py
# version: 1.0.0
# uuid: 33c569d2-b8c0-4fd8-8213-07928a002ad9
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165637
# last_modified_at: 2025-05-21T16:42:46.093689
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 16bf340b2888976180d92e6883b02dcb5cdbda4e9d18d6216a7d988b22ff38bc
# entrypoint: python@model_log_entry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_log_entry
# meta_type: tool
# === /OmniNode:Metadata ===


from omnibase.model.model_base_error import BaseErrorModel
from omnibase.model.model_enum_log_level import LogLevelEnum


class LogEntryModel(BaseErrorModel):
    message: str
    level: LogLevelEnum = LogLevelEnum.INFO
