from pydantic import BaseModel
from typing import List

from .model_validation_issue import ValidationIssueModel


class TemplateValidationResultModel(BaseModel):
    """Result of template validation with comprehensive metrics"""
    issues: List[ValidationIssueModel]
    error_count: int
    warning_count: int
    info_count: int
    total_files_checked: int
    node_name: str
    validation_passed: bool 