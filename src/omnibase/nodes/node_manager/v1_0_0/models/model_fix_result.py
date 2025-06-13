from pydantic import BaseModel
from typing import List


class FixResultModel(BaseModel):
    """Result of template issue fixing operation"""
    fixed_count: int
    failed_fixes: List[str]
    success: bool
    node_name: str
    total_issues_processed: int 