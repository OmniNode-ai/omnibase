# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 395add0e-bfe8-4e8b-b6ff-0e8f94101eb2
# name: model_onex_result.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:56.741010
# last_modified_at: 2025-05-19T16:19:56.741014
# description: Stamped Python file: model_onex_result.py
# state_contract: none
# lifecycle: active
# hash: 82b107eaf2c3c7f2114394fa017f1c2f898bc4549fbeec646cc6590a4fd45961
# entrypoint: {'type': 'python', 'target': 'model_onex_result.py'}
# namespace: onex.stamped.model_onex_result.py
# meta_type: tool
# === /OmniNode:Metadata ===

from typing import Any, Dict, List, Optional

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
    summary: Optional[Dict[str, Any]] = (
        None  # Use a dedicated model if available; else Dict[str, Any] for extensibility
    )
    metadata: Optional[Dict[str, Any]] = None  # Arbitrary metadata, extensible
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
    orchestrator_info: Optional[Dict[str, Any]] = None  # Arbitrary orchestrator info
    tool_name: Optional[str] = None
    skipped_reason: Optional[str] = None
    coverage: Optional[float] = None
    test_type: Optional[str] = None
    batch_id: Optional[str] = None
    parent_id: Optional[str] = None
    timestamp: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
