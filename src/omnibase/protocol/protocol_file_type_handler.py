# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: <to-be-generated>
# name: protocol_file_type_handler.py
# version: 1.0.0
# author: OmniNode Team
# created_at: <to-be-generated>
# last_modified_at: <to-be-generated>
# description: Protocol interface for file type handlers in the ONEX stamper engine.
# state_contract: none
# lifecycle: active
# hash: 0000000000000000000000000000000000000000000000000000000000000000
# entrypoint: {'type': 'python', 'target': 'protocol_file_type_handler.py'}
# namespace: onex.stamped.protocol_file_type_handler.py
# meta_type: tool
# === /OmniNode:Metadata ===

from pathlib import Path
from typing import Any, Optional, Protocol

from omnibase.model.model_onex_result import OnexResultModel


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
