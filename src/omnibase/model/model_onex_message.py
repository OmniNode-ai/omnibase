# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.000948'
# description: Stamped by PythonHandler
# entrypoint: python://model_onex_message.py
# hash: 0b44ad584eb8fca7e6e774347dd4bdc26e05785963fc7af739265412bb848c99
# last_modified_at: '2025-05-29T11:50:11.015724+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_onex_message.py
# namespace: omnibase.model_onex_message
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 9acab5df-2004-4ed4-9f4f-e5c02c6b7de9
# version: 1.0.0
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
