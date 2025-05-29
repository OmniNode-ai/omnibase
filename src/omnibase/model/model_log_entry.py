# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-29T07:58:05.060441'
# description: Stamped by PythonHandler
# entrypoint: python://model_log_entry.py
# hash: 36f792cf039facc9f5e1e8deca04b1b838fced08888f7970242a2b0aad24294d
# last_modified_at: '2025-05-29T11:58:47.856680+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_log_entry.py
# namespace: omnibase.model_log_entry
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 51fc28d7-354b-4edb-b855-60ab4e467a01
# version: 1.0.0
# === /OmniNode:Metadata ===


from omnibase.enums import LogLevelEnum
from omnibase.model.model_base_error import BaseErrorModel


class LogEntryModel(BaseErrorModel):
    message: str
    level: LogLevelEnum = LogLevelEnum.INFO
