# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: af95daff-ca20-46c4-ba59-347e979a1447
# name: model_validate_error.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:19:52.165050
# last_modified_at: 2025-05-19T16:19:52.165057
# description: Stamped Python file: model_validate_error.py
# state_contract: none
# lifecycle: active
# hash: 551b777ed3c74bbc678e3ebafcfdc11f4ae09a5e9a12c55ed20a18d93479b705
# entrypoint: {'type': 'python', 'target': 'model_validate_error.py'}
# namespace: onex.stamped.model_validate_error.py
# meta_type: tool
# === /OmniNode:Metadata ===

import datetime
import hashlib
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from omnibase.model.model_base_error import BaseErrorModel
from omnibase.model.model_enum_log_level import SeverityLevelEnum
from omnibase.model.model_onex_message_result import OnexStatus


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
        default=OnexStatus.error,
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


class ValidateError(Exception):
    """Custom exception for all validation errors in the new validation system."""

    pass


# TODO: Implement formatters for JSON, plain text, and CI-compatible output
# TODO: Implement marker placement logic for output files
