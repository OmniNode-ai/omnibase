# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_file_type_handler.py
# version: 1.0.0
# uuid: 3a45b9c0-6155-4f59-82bf-7f130f53aab1
# author: OmniNode Team
# created_at: 2025-05-22T14:03:21.904957
# last_modified_at: 2025-05-22T20:50:39.725147
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 69d0b3f0f26533aee6af6180208fd467e1928e4106db9be5150ed68d25440d5f
# entrypoint: python@protocol_file_type_handler.py
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
