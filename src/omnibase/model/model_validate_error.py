# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.102429'
# description: Stamped by PythonHandler
# entrypoint: python://model_validate_error.py
# hash: d01fd0c2ad45f7ed634e112f47e59286b5ac39483803c81f48de00fe9c679742
# last_modified_at: '2025-05-29T11:50:11.088290+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_validate_error.py
# namespace: omnibase.model_validate_error
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: 120a665f-4735-4e7f-9bb9-0ecd4afa33ec
# version: 1.0.0
# === /OmniNode:Metadata ===


import datetime
import hashlib
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from omnibase.enums import OnexStatus, SeverityLevelEnum
from omnibase.model.model_base_error import BaseErrorModel


class ValidateMessageModel(BaseErrorModel):
    file: Optional[str] = None
    line: Optional[int] = None
    severity: SeverityLevelEnum = Field(
        default=SeverityLevelEnum.ERROR,
        description="error|warning|info|debug|critical|success|unknown",
    )
    code: str = "unknown"
    context: Optional[Dict[str, Any]] = None
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hash: Optional[str] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    # message is inherited from BaseErrorModel and must always be str (not Optional)
    # All instantiations must provide a non-None str for message

    def compute_hash(self) -> str:
        # Compute a hash of the message content for integrity
        h = hashlib.sha256()
        h.update(self.message.encode("utf-8"))
        if self.file:
            h.update(self.file.encode("utf-8"))
        if self.code:
            h.update(self.code.encode("utf-8"))
        h.update(self.severity.value.encode("utf-8"))
        if self.context:
            h.update(str(self.context).encode("utf-8"))
        return h.hexdigest()

    def with_hash(self) -> "ValidateMessageModel":
        self.hash = self.compute_hash()
        return self

    def to_json(self) -> str:
        """Return the message as a JSON string."""
        return self.model_dump_json()

    def to_text(self) -> str:
        """Return the message as a plain text string."""
        parts = [f"[{self.severity.value.upper()}] {self.message}"]
        if self.file:
            parts.append(f"File: {self.file}")
        if self.line is not None:
            parts.append(f"Line: {self.line}")
        if self.code:
            parts.append(f"Code: {self.code}")
        if self.context:
            parts.append(f"Context: {self.context}")
        parts.append(f"UID: {self.uid}")
        parts.append(f"Hash: {self.hash or self.compute_hash()}")
        parts.append(f"Timestamp: {self.timestamp}")
        return " | ".join(parts)

    def to_ci(self) -> str:
        """Return a CI-friendly string (e.g., for GitHub Actions annotations)."""
        loc = (
            f"file={self.file},line={self.line}"
            if self.file and self.line is not None
            else ""
        )
        return f"::{self.severity.value} {loc}::{self.message}"


class ValidateResultModel(BaseModel):
    messages: List[ValidateMessageModel]
    status: OnexStatus = Field(
        default=OnexStatus.ERROR,
        description="success|warning|error|skipped|fixed|partial|info|unknown",
    )
    summary: Optional[str] = None
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hash: Optional[str] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    def compute_hash(self) -> str:
        h = hashlib.sha256()
        for msg in self.messages:
            h.update(
                msg.hash.encode("utf-8") if msg.hash else msg.message.encode("utf-8")
            )
        h.update(self.status.value.encode("utf-8"))
        if self.summary:
            h.update(self.summary.encode("utf-8"))
        return h.hexdigest()

    def with_hash(self) -> "ValidateResultModel":
        self.hash = self.compute_hash()
        return self

    def to_json(self) -> str:
        """Return the result as a JSON string."""
        return self.model_dump_json()

    def to_text(self) -> str:
        """Return the result as a plain text string."""
        lines = [
            f"Status: {self.status.value}",
            f"Summary: {self.summary or ''}",
            f"UID: {self.uid}",
            f"Hash: {self.hash or self.compute_hash()}",
            f"Timestamp: {self.timestamp}",
        ]
        for msg in self.messages:
            lines.append(msg.to_text())
        return "\n".join(lines)

    def to_ci(self) -> str:
        """Return a CI-friendly string for the result."""
        return "\n".join(msg.to_ci() for msg in self.messages)


def insert_template_marker(
    output: str, marker: str = "# TEMPLATE: validator.v0.1"
) -> str:
    """Insert a template marker at the top of the output string if not present."""
    lines = output.splitlines()
    if lines and lines[0].startswith("# TEMPLATE:"):
        return output
    return f"{marker}\n" + output


# ValidateError replaced with OnexError for centralized error handling
# Use OnexError with CoreErrorCode.VALIDATION_ERROR instead


# TODO: Implement formatters for JSON, plain text, and CI-compatible output
# TODO: Implement marker placement logic for output files
