# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.169382'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_file_type_handler.py
# hash: 8873db07feeccee6c61bb0232749cf8dfdaba42f3b786c1c8e53b3118cd9b476
# last_modified_at: '2025-05-29T11:50:12.116754+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_file_type_handler.py
# namespace: omnibase.protocol_file_type_handler
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 4e1063a3-c759-42a8-8a3f-2d05489e0ea4
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Any, List, Optional, Protocol

from omnibase.model.model_onex_message_result import OnexResultModel


class ProtocolFileTypeHandler(Protocol):
    """
    Protocol for file type handlers in the ONEX stamper engine.
    Each handler is responsible for stamping, validation, and hash computation for its file type/role.
    All methods must use canonical result models (OnexResultModel) per typing_and_protocols rule.

    All handlers must declare metadata properties for introspection and plugin management.
    """

    # Required metadata properties for handler introspection
    @property
    def handler_name(self) -> str:
        """Unique name for this handler (e.g., 'python_handler', 'yaml_metadata_handler')."""
        ...

    @property
    def handler_version(self) -> str:
        """Version of this handler implementation (e.g., '1.0.0')."""
        ...

    @property
    def handler_author(self) -> str:
        """Author or team responsible for this handler (e.g., 'OmniNode Team')."""
        ...

    @property
    def handler_description(self) -> str:
        """Brief description of what this handler does."""
        ...

    @property
    def supported_extensions(self) -> List[str]:
        """List of file extensions this handler supports (e.g., ['.py', '.pyx'])."""
        ...

    @property
    def supported_filenames(self) -> List[str]:
        """List of specific filenames this handler supports (e.g., ['.onexignore', 'Dockerfile'])."""
        ...

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler (higher wins conflicts). Core=100, Runtime=50, Node-local=10, Plugin=0."""
        ...

    @property
    def requires_content_analysis(self) -> bool:
        """Whether this handler needs to analyze file content to determine if it can handle the file."""
        ...

    # Core handler methods
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
