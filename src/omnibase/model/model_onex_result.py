from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from omnibase.model.enum_onex_status import OnexStatus
from omnibase.model.model_onex_message import OnexMessageModel


class OnexResultModel(BaseModel):
    """
    Machine-consumable result for validation, tooling, or test execution.
    Supports recursive composition, extensibility, and protocol versioning.
    """

    status: OnexStatus
    target: Optional[str] = Field(
        None, description="Target file or resource validated."
    )
    messages: List[OnexMessageModel] = Field(default_factory=list)
    summary: Optional[dict] = None  # Consider a strongly typed model if needed
    metadata: Optional[Dict[str, str]] = None
    suggestions: Optional[List[str]] = None
    diff: Optional[str] = None
    auto_fix_applied: Optional[bool] = None
    fixed_files: Optional[List[str]] = None
    failed_files: Optional[List[str]] = None
    version: Optional[str] = None
    duration: Optional[float] = None
    exit_code: Optional[int] = None
    run_id: Optional[str] = None
    child_results: Optional[List["OnexResultModel"]] = None
    output_format: Optional[str] = None
    cli_args: Optional[List[str]] = None
    orchestrator_info: Optional[Dict[str, str]] = None
    tool_name: Optional[str] = None
    skipped_reason: Optional[str] = None
    coverage: Optional[float] = None
    test_type: Optional[str] = None
    batch_id: Optional[str] = None
    parent_id: Optional[str] = None
    timestamp: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
