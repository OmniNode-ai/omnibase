# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: protocol_file_type_handler.py
# version: 1.0.0
# uuid: f29ed083-7005-4119-9103-81ad31c1e64c
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.167134
# last_modified_at: 2025-05-21T16:42:46.070284
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a7f4d67be896d2f08e9d9cc629e56cb596109d867717d5952fae9621b4998798
# entrypoint: {'type': 'python', 'target': 'protocol_file_type_handler.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_file_type_handler
# meta_type: tool
# === /OmniNode:Metadata ===

from pathlib import Path
from typing import Any, Optional, Protocol

from omnibase.model.model_onex_message_result import OnexResultModel


class ProtocolFileTypeHandler(Protocol):
    """
    Protocol for file type handlers in the ONEX stamper engine.
    Each handler is responsible for stamping, validation, and hash computation for its file type/role.
    All methods must use canonical result models (OnexResultModel) per typing_and_protocols rule.
    """

    def can_handle(self, path: Path, content: str) -> bool:
        """Return True if this handler can process the given file."""
        ...

    def extract_block(self, path: Path, content: str) -> tuple[Optional[Any], str]: ...

    def serialize_block(self, meta: Any) -> str: ...

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """Stamp the file and return the canonical result model (OnexResultModel)."""
        ...

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel: ...

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        """Optional: Validate before stamping. Return OnexResultModel or None."""
        ...

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        """Optional: Validate after stamping. Return OnexResultModel or None."""
        ...
