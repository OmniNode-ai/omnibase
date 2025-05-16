from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from omnibase.model.model_enum_log_level import LogLevelEnum, SeverityLevelEnum

# === OmniNode:Metadata ===
metadata_version = "0.1"
name = "model_unified_result"
namespace = "foundation.model"
version = "0.1.0"
type = "model"
entrypoint = "model_unified_result.py"
owner = "foundation-team"
# === /OmniNode:Metadata ===


class OnexStatus(str, Enum):
    success = "success"
    warning = "warning"
    error = "error"
    skipped = "skipped"
    fixed = "fixed"
    partial = "partial"
    info = "info"
    unknown = "unknown"


class UnifiedMessageModel(BaseModel):
    """
    Human-facing message for CLI, UI, or agent presentation.
    Supports linking to files, lines, context, and rich rendering.
    """

    summary: str = Field(..., description="Short summary of the message.")
    suggestions: Optional[List[str]] = None
    remediation: Optional[str] = None
    rendered_markdown: Optional[str] = None
    doc_link: Optional[str] = None
    level: LogLevelEnum = Field(
        LogLevelEnum.INFO, description="Message level: info, warning, error, etc."
    )
    file: Optional[str] = Field(None, description="File path related to the message.")
    line: Optional[int] = Field(
        None, description="Line number in the file, if applicable."
    )
    column: Optional[int] = None
    details: Optional[str] = Field(None, description="Detailed message or context.")
    severity: Optional[SeverityLevelEnum] = None
    code: Optional[str] = Field(None, description="Error or warning code, if any.")
    context: Optional[Dict[str, Any]] = Field(
        None, description="Additional context for the message."
    )
    timestamp: Optional[datetime] = Field(None, description="Timestamp of the message.")
    fixable: Optional[bool] = None
    origin: Optional[str] = None
    example: Optional[str] = None
    localized_text: Optional[Dict[str, str]] = None
    type: Optional[str] = Field(
        None, description="Type of message (error, warning, note, etc.)"
    )


class UnifiedSummaryModel(BaseModel):
    total: int
    passed: int
    failed: int
    skipped: int
    fixed: int
    warnings: int
    notes: Optional[List[str]] = None
    details: Optional[Dict[str, Any]] = None


class UnifiedVersionModel(BaseModel):
    protocol_version: str
    tool_version: Optional[str] = None
    schema_version: Optional[str] = None
    last_updated: Optional[datetime] = None


class UnifiedRunMetadataModel(BaseModel):
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    run_id: Optional[str] = None


class OnexResultModel(BaseModel):
    """
    Machine-consumable result for validation, tooling, or test execution.
    Supports recursive composition, extensibility, and protocol versioning.
    """

    status: OnexStatus
    target: Optional[str] = Field(
        None, description="Target file or resource validated."
    )
    messages: List[UnifiedMessageModel] = Field(default_factory=list)
    summary: Optional[UnifiedSummaryModel] = None
    metadata: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    diff: Optional[str] = None
    auto_fix_applied: Optional[bool] = None
    fixed_files: Optional[List[str]] = None
    failed_files: Optional[List[str]] = None
    version: Optional[UnifiedVersionModel] = None
    duration: Optional[float] = None
    exit_code: Optional[int] = None
    run_id: Optional[str] = None
    child_results: Optional[List["OnexResultModel"]] = None
    output_format: Optional[str] = None
    cli_args: Optional[List[str]] = None
    orchestrator_info: Optional[Dict[str, Any]] = None
    tool_name: Optional[str] = None
    skipped_reason: Optional[str] = None
    coverage: Optional[float] = None
    test_type: Optional[str] = None
    batch_id: Optional[str] = None
    parent_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "status": "success",
                "run_id": "abc123",
                "tool_name": "metadata_block",
                "target": "file.yaml",
                "messages": [
                    {
                        "summary": "All required metadata fields present.",
                        "level": "info",
                    }
                ],
                "version": "v1",
            }
        },
    )


class OnexBatchResultModel(BaseModel):
    results: List[OnexResultModel]
    messages: List[UnifiedMessageModel] = Field(default_factory=list)
    summary: Optional[UnifiedSummaryModel] = None
    status: Optional[OnexStatus] = None
    version: Optional[UnifiedVersionModel] = None
    run_metadata: Optional[UnifiedRunMetadataModel] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def export_schema(cls) -> Dict[str, Any]:
        """Export the JSONSchema for OnexBatchResultModel and all submodels."""
        print("export_schema called")  # Coverage debug
        return json.dumps(cls.model_json_schema(), indent=2)


OnexResultModel.model_rebuild()
