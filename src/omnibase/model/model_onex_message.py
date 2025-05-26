# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_onex_message.py
# version: 1.0.0
# uuid: 8d07b558-40d4-4c3d-8d36-f04e0994798a
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.166053
# last_modified_at: 2025-05-21T16:42:46.050730
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 62894a0bb6367ff204f2977531e6fa8656f75a29198e7365f732ad5116a26f97
# entrypoint: python@model_onex_message.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_onex_message
# meta_type: tool
# === /OmniNode:Metadata ===


from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from omnibase.enums import LogLevelEnum, SeverityLevelEnum
from omnibase.model.model_context import ContextModel
from omnibase.model.model_doc_link import DocLinkModel
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
