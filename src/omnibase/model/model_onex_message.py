# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 7f5df8cd-da26-4a24-aaf9-13e611678762
# name: model_onex_message.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:58.353096
# last_modified_at: 2025-05-19T16:19:58.353098
# description: Stamped Python file: model_onex_message.py
# state_contract: none
# lifecycle: active
# hash: e6061cbe25b682e64a6aa63031380d55292c2e058aaeefa4ff72c50764030535
# entrypoint: {'type': 'python', 'target': 'model_onex_message.py'}
# namespace: onex.stamped.model_onex_message.py
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from omnibase.model.model_context import ContextModel
from omnibase.model.model_doc_link import DocLinkModel
from omnibase.model.model_enum_log_level import LogLevelEnum, SeverityLevelEnum
from omnibase.model.model_file_reference import FileReferenceModel

__all__ = ["LogLevelEnum", "SeverityLevelEnum", "OnexMessageModel"]


class OnexMessageModel(BaseModel):
    summary: str = Field(..., description="Short summary of the message.")
    suggestions: Optional[List[str]] = None
    remediation: Optional[str] = None
    rendered_markdown: Optional[str] = None
    doc_link: Optional[DocLinkModel] = None
    file: Optional[FileReferenceModel] = None
    line: Optional[int] = None
    column: Optional[int] = None
    details: Optional[str] = None
    level: LogLevelEnum = Field(
        LogLevelEnum.INFO, description="Message level: info, warning, error, etc."
    )
    severity: Optional[SeverityLevelEnum] = None
    code: Optional[str] = None  # Consider using an Enum or CodeModel if needed
    context: Optional[ContextModel] = None
    timestamp: Optional[str] = None
    fixable: Optional[bool] = None
    origin: Optional[str] = None  # Consider using an Enum if fixed set
    example: Optional[str] = None
    localized_text: Optional[Dict[str, str]] = None  # Localized text by language code
    type: Optional[str] = None  # Consider using an Enum if fixed set
