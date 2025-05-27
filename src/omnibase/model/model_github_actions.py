# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: model_github_actions.py
# version: 1.0.0
# uuid: a21ca199-2d29-44f9-9494-0878891b5770
# author: OmniNode Team
# created_at: 2025-05-27T17:12:45.966507
# last_modified_at: 2025-05-27T21:27:00.936113
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: ec76dce33b474c1d73d2c7815bd512c88c9ac1ccf967c652d8593c7d2cece08e
# entrypoint: python@model_github_actions.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_github_actions
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Pydantic models for GitHub Actions workflows.

This module defines the structure for GitHub Actions workflow files (.github/workflows/*.yml)
to enable proper validation, serialization, and formatting.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class TriggerEvent(str, Enum):
    """GitHub Actions trigger events."""

    PUSH = "push"
    PULL_REQUEST = "pull_request"
    SCHEDULE = "schedule"
    WORKFLOW_DISPATCH = "workflow_dispatch"
    RELEASE = "release"
    ISSUES = "issues"
    ISSUE_COMMENT = "issue_comment"


class RunnerOS(str, Enum):
    """GitHub Actions runner operating systems."""

    UBUNTU_LATEST = "ubuntu-latest"
    UBUNTU_20_04 = "ubuntu-20.04"
    UBUNTU_22_04 = "ubuntu-22.04"
    WINDOWS_LATEST = "windows-latest"
    WINDOWS_2019 = "windows-2019"
    WINDOWS_2022 = "windows-2022"
    MACOS_LATEST = "macos-latest"
    MACOS_11 = "macos-11"
    MACOS_12 = "macos-12"


class PushTrigger(BaseModel):
    """Push trigger configuration."""

    branches: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    paths: Optional[List[str]] = None
    paths_ignore: Optional[List[str]] = Field(None, alias="paths-ignore")


class PullRequestTrigger(BaseModel):
    """Pull request trigger configuration."""

    branches: Optional[List[str]] = None
    types: Optional[List[str]] = None
    paths: Optional[List[str]] = None
    paths_ignore: Optional[List[str]] = Field(None, alias="paths-ignore")


class ScheduleTrigger(BaseModel):
    """Schedule trigger configuration."""

    cron: str


class WorkflowTriggers(BaseModel):
    """Workflow trigger configuration."""

    push: Optional[PushTrigger] = None
    pull_request: Optional[PullRequestTrigger] = None
    schedule: Optional[List[ScheduleTrigger]] = None
    workflow_dispatch: Optional[Dict[str, Any]] = None
    release: Optional[Dict[str, Any]] = None
    issues: Optional[Dict[str, Any]] = None
    issue_comment: Optional[Dict[str, Any]] = None


class StepWith(BaseModel):
    """Step 'with' parameters."""

    model_config = {"extra": "allow"}  # Allow any additional fields


class Step(BaseModel):
    """GitHub Actions workflow step."""

    name: Optional[str] = None
    uses: Optional[str] = None
    run: Optional[str] = None
    with_: Optional[Union[StepWith, Dict[str, Any]]] = Field(None, alias="with")
    env: Optional[Dict[str, str]] = None
    if_: Optional[str] = Field(None, alias="if")
    continue_on_error: Optional[bool] = Field(None, alias="continue-on-error")
    timeout_minutes: Optional[int] = Field(None, alias="timeout-minutes")
    working_directory: Optional[str] = Field(None, alias="working-directory")


class Job(BaseModel):
    """GitHub Actions workflow job."""

    runs_on: Union[str, List[str]] = Field(..., alias="runs-on")
    steps: List[Step]
    name: Optional[str] = None
    needs: Optional[Union[str, List[str]]] = None
    if_: Optional[str] = Field(None, alias="if")
    env: Optional[Dict[str, str]] = None
    timeout_minutes: Optional[int] = Field(None, alias="timeout-minutes")
    strategy: Optional[Dict[str, Any]] = None
    continue_on_error: Optional[bool] = Field(None, alias="continue-on-error")
    container: Optional[Union[str, Dict[str, Any]]] = None
    services: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, str]] = None


class GitHubActionsWorkflow(BaseModel):
    """GitHub Actions workflow model."""

    name: str
    on: WorkflowTriggers
    jobs: Dict[str, Job]
    env: Optional[Dict[str, str]] = None
    defaults: Optional[Dict[str, Any]] = None
    concurrency: Optional[Union[str, Dict[str, Any]]] = None
    permissions: Optional[Union[str, Dict[str, Any]]] = None

    def to_serializable_dict(self) -> Dict[str, Any]:
        """
        Convert to a serializable dictionary with proper field names.
        """

        def serialize_value(val: Any) -> Any:
            if hasattr(val, "to_serializable_dict"):
                return val.to_serializable_dict()
            elif isinstance(val, BaseModel):
                return val.model_dump(by_alias=True, exclude_none=True)
            elif isinstance(val, Enum):
                return val.value
            elif isinstance(val, list):
                return [serialize_value(v) for v in val]
            elif isinstance(val, dict):
                return {k: serialize_value(v) for k, v in val.items()}
            else:
                return val

        return {
            k: serialize_value(getattr(self, k))
            for k in self.model_fields
            if getattr(self, k) is not None
        }

    @classmethod
    def from_serializable_dict(cls, data: Dict[str, Any]) -> "GitHubActionsWorkflow":
        """
        Create from a serializable dictionary.
        """
        return cls(**data)
