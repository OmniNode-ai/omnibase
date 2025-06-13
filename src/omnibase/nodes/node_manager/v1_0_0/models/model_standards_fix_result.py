from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from pathlib import Path

from omnibase.enums.log_level import SeverityLevelEnum
from omnibase.nodes.node_manager.v1_0_0.enums.enum_issue_type import EnumIssueType


class ModelStandardsFixOperation(BaseModel):
    """Model representing a single standards compliance fix operation."""
    
    issue_type: EnumIssueType = Field(description="Type of standards issue being fixed")
    severity: SeverityLevelEnum = Field(description="Severity level of the issue")
    file_path: Path = Field(description="Path to the file being fixed")
    description: str = Field(description="Description of the fix operation")
    old_value: Optional[str] = Field(default=None, description="Original value before fix")
    new_value: Optional[str] = Field(default=None, description="New value after fix")
    backup_created: bool = Field(default=False, description="Whether a backup was created")
    backup_path: Optional[Path] = Field(default=None, description="Path to backup file if created")


class ModelStandardsFixResult(BaseModel):
    """Model representing the result of standards compliance fix operations."""
    
    success: bool = Field(description="Whether all fix operations completed successfully")
    total_fixes_attempted: int = Field(description="Total number of fixes attempted")
    fixes_successful: int = Field(description="Number of fixes that completed successfully")
    fixes_failed: int = Field(description="Number of fixes that failed")
    fixes_skipped: int = Field(description="Number of fixes that were skipped")
    
    operations: List[ModelStandardsFixOperation] = Field(
        default_factory=list,
        description="List of all fix operations performed"
    )
    
    errors: List[str] = Field(
        default_factory=list,
        description="List of error messages for failed operations"
    )
    
    warnings: List[str] = Field(
        default_factory=list,
        description="List of warning messages"
    )
    
    summary: str = Field(description="Human-readable summary of fix results")
    
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the fix operation"
    )
    
    dry_run: bool = Field(default=False, description="Whether this was a dry run (no actual changes)") 