# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 45ca5715-6ce8-4513-a460-d1589ce71051
# name: protocol_file_type_handler.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:38:44.524748
# last_modified_at: 2025-05-19T16:38:44.524751
# description: Stamped Python file: protocol_file_type_handler.py
# state_contract: none
# lifecycle: active
# hash: e637f626591aba76684152863bceefe3b8631e5cc3c986b9c96fc3f90aa732fe
# entrypoint: {'type': 'python', 'target': 'protocol_file_type_handler.py'}
# namespace: onex.stamped.protocol_file_type_handler.py
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

    def compute_hash(self, path: Path, content: str, **kwargs: Any) -> Optional[str]:
        """Optional: Compute canonical hash for the file content."""
        ...
