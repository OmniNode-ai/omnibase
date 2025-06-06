# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-29T07:58:05.060441'
# description: Stamped by PythonHandler
# entrypoint: python://model_log_entry
# hash: e76f7fbe0601e86b8dc99d7c1d58db54d3152767aecea5d68805fb66787b2d16
# last_modified_at: '2025-05-29T14:13:58.798345+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_log_entry.py
# namespace: python://omnibase.model.model_log_entry
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 51fc28d7-354b-4edb-b855-60ab4e467a01
# version: 1.0.0
# === /OmniNode:Metadata ===


from typing import Optional

from pydantic import BaseModel

from omnibase.enums import LogLevelEnum
from omnibase.model.model_base_error import BaseErrorModel


class LogContextModel(BaseModel):
    """
    Strongly typed context for ONEX structured log events.
    """

    calling_module: str
    calling_function: str
    calling_line: int
    timestamp: str
    node_id: Optional[str] = None
    correlation_id: Optional[str] = None


class LogEntryModel(BaseErrorModel):
    message: str
    level: LogLevelEnum = LogLevelEnum.INFO
    context: LogContextModel


class LogMarkdownRowModel(BaseModel):
    """
    Represents a single row in a Markdown log table for aligned output.
    """

    level_emoji: str
    message: str
    function: str
    line: int
    timestamp: str
