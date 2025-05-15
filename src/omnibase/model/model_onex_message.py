from pydantic import BaseModel, Field
from typing import Optional, List
from omnibase.model.model_enum_log_level import LogLevelEnum, SeverityLevelEnum
from omnibase.model.model_doc_link import DocLinkModel
from omnibase.model.model_file_reference import FileReferenceModel
from omnibase.model.model_context import ContextModel

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
    level: LogLevelEnum = Field(LogLevelEnum.INFO, description="Message level: info, warning, error, etc.")
    severity: Optional[SeverityLevelEnum] = None
    code: Optional[str] = None  # Consider using an Enum or CodeModel if needed
    context: Optional[ContextModel] = None
    timestamp: Optional[str] = None
    fixable: Optional[bool] = None
    origin: Optional[str] = None  # Consider using an Enum if fixed set
    example: Optional[str] = None
    localized_text: Optional[dict] = None
    type: Optional[str] = None  # Consider using an Enum if fixed set 