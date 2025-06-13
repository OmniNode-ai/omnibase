from pydantic import BaseModel

from omnibase.enums.log_level import SeverityLevelEnum
from ..enums.enum_issue_type import EnumIssueType


class ValidationIssueModel(BaseModel):
    """Represents a template validation issue with proper typing"""
    file_path: str
    line_number: int
    issue_type: EnumIssueType
    description: str
    severity: SeverityLevelEnum
    suggested_fix: str = "" 