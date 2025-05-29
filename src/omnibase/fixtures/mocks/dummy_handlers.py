# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.528031'
# description: Stamped by PythonHandler
# entrypoint: python://dummy_handlers
# hash: 4a967b8aef76ac66d39770e4d41ad694824523060cee3830a1892f63f7f02c53
# last_modified_at: '2025-05-29T14:13:58.626977+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: dummy_handlers.py
# namespace: python://omnibase.fixtures.mocks.dummy_handlers
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 68962e35-aaa1-485d-8c4c-1e66631f991a
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Consolidated dummy handlers for testing.

This module provides configurable dummy handlers that can be used across
different test scenarios, replacing the duplicate implementations that
were previously scattered across node-local test files.
"""

from pathlib import Path
from typing import Any, Callable, Optional, Tuple

from omnibase.enums import LogLevelEnum, OnexStatus
from omnibase.model.model_onex_message_result import OnexMessageModel, OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler


class ConfigurableDummyHandler(ProtocolFileTypeHandler):
    """
    A configurable dummy handler that can be customized for different test scenarios.

    This handler can be configured with:
    - Custom status/message providers (functions or static values)
    - File type identification
    - Custom behavior for different methods
    """

    def __init__(
        self,
        file_type: str = "dummy",
        status_provider: Optional[Callable[[], OnexStatus]] = None,
        message_provider: Optional[Callable[[], str]] = None,
        static_status: Optional[OnexStatus] = None,
        static_message: Optional[str] = None,
        can_handle_predicate: Optional[Callable[[Path, str], bool]] = None,
        hash_value: str = "dummy_hash",
    ):
        """
        Initialize the configurable dummy handler.

        Args:
            file_type: The file type this handler claims to support
            status_provider: Function that returns the status to use
            message_provider: Function that returns the message to use
            static_status: Static status to always return (overrides provider)
            static_message: Static message to always return (overrides provider)
            can_handle_predicate: Custom predicate for can_handle method
            hash_value: Hash value to return from compute_hash
        """
        self.file_type = file_type
        self.status_provider = status_provider
        self.message_provider = message_provider
        self.static_status = static_status
        self.static_message = static_message
        self.can_handle_predicate = can_handle_predicate
        self.hash_value = hash_value

    def _get_status(self) -> OnexStatus:
        """Get the status to use for results."""
        if self.static_status is not None:
            return self.static_status
        if self.status_provider is not None:
            return self.status_provider()
        return OnexStatus.SUCCESS

    def _get_message(self) -> str:
        """Get the message to use for results."""
        if self.static_message is not None:
            return self.static_message
        if self.message_provider is not None:
            return self.message_provider()
        return f"Dummy {self.file_type} handler result"

    def can_handle(self, path: Path, content: str) -> bool:
        """Determine if this handler can process the given file."""
        if self.can_handle_predicate is not None:
            return self.can_handle_predicate(path, content)
        return True

    def extract_block(self, path: Path, content: str) -> Tuple[Optional[Any], str]:
        """Extract metadata block from content."""
        return None, content

    def serialize_block(self, meta: Any) -> str:
        """Serialize metadata block."""
        return ""

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """Stamp the file with metadata."""
        status = self._get_status()
        message = self._get_message()

        return OnexResultModel(
            status=status,
            target=str(path),
            messages=[
                OnexMessageModel(
                    summary=message,
                    level=(
                        LogLevelEnum.INFO
                        if status == OnexStatus.SUCCESS
                        else LogLevelEnum.ERROR
                    ),
                    file=str(path),
                    line=0,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
                )
            ],
            metadata={},
        )

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        """Validate the file."""
        status = self._get_status()
        message = self._get_message()

        return OnexResultModel(
            status=status,
            target=str(path),
            messages=[
                OnexMessageModel(
                    summary=message,
                    level=(
                        LogLevelEnum.INFO
                        if status == OnexStatus.SUCCESS
                        else LogLevelEnum.ERROR
                    ),
                    file=str(path),
                    line=0,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
                )
            ],
            metadata={},
        )

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        """Pre-validation hook."""
        return None

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        """Post-validation hook."""
        return None

    def compute_hash(self, path: Path, content: str, **kwargs: Any) -> Optional[str]:
        """Compute hash for the file."""
        return self.hash_value

    # Handler metadata properties (required by ProtocolFileTypeHandler)
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return f"configurable_dummy_{self.file_type}_handler"

    @property
    def handler_version(self) -> str:
        """Version of this handler implementation."""
        return "1.0.0"

    @property
    def handler_author(self) -> str:
        """Author or team responsible for this handler."""
        return "OmniNode Test Team"

    @property
    def handler_description(self) -> str:
        """Brief description of what this handler does."""
        return f"Configurable dummy handler for {self.file_type} files (testing only)"

    @property
    def supported_extensions(self) -> list[str]:
        """List of file extensions this handler supports."""
        return [f".{self.file_type}"]

    @property
    def supported_filenames(self) -> list[str]:
        """List of specific filenames this handler supports."""
        return []  # Dummy handler works with extensions

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler."""
        return 0  # Test/plugin handler priority (lowest)

    @property
    def requires_content_analysis(self) -> bool:
        """Whether this handler needs to analyze file content."""
        return bool(self.can_handle_predicate)  # Only if custom predicate is provided


class DummyYamlHandler(ConfigurableDummyHandler):
    """Dummy YAML handler for testing."""

    def __init__(self, **kwargs: Any):
        super().__init__(file_type="yaml", **kwargs)


class DummyJsonHandler(ConfigurableDummyHandler):
    """Dummy JSON handler for testing."""

    def __init__(self, **kwargs: Any):
        super().__init__(file_type="json", **kwargs)


class SmartDummyYamlHandler(ProtocolFileTypeHandler):
    """
    Smart dummy YAML handler with content-aware behavior.

    This handler provides more realistic behavior based on content:
    - Returns ERROR for None content (file doesn't exist)
    - Returns WARNING for empty content
    - Returns WARNING for other content (semantic validation failed)
    """

    file_type = "yaml"

    # Handler metadata properties (required by ProtocolFileTypeHandler)
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "smart_dummy_yaml_handler"

    @property
    def handler_version(self) -> str:
        """Version of this handler implementation."""
        return "1.0.0"

    @property
    def handler_author(self) -> str:
        """Author or team responsible for this handler."""
        return "OmniNode Test Team"

    @property
    def handler_description(self) -> str:
        """Brief description of what this handler does."""
        return "Smart dummy YAML handler with content-aware behavior (testing only)"

    @property
    def supported_extensions(self) -> list[str]:
        """List of file extensions this handler supports."""
        return [".yaml", ".yml"]

    @property
    def supported_filenames(self) -> list[str]:
        """List of specific filenames this handler supports."""
        return []  # YAML handler works with extensions

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler."""
        return 0  # Test/plugin handler priority (lowest)

    @property
    def requires_content_analysis(self) -> bool:
        """Whether this handler needs to analyze file content."""
        return True  # Smart handler analyzes content for behavior

    def can_handle(self, path: Path, content: str) -> bool:
        return True

    def extract_block(self, path: Path, content: str) -> Tuple[Optional[Any], str]:
        return None, content

    def serialize_block(self, meta: Any) -> str:
        return ""

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        if content is None:
            return OnexResultModel(
                status=OnexStatus.ERROR,
                target=str(path),
                messages=[
                    OnexMessageModel(
                        summary="File does not exist",
                        level=LogLevelEnum.ERROR,
                        file=str(path),
                        line=0,
                        details=None,
                        code=None,
                        context=None,
                        timestamp=None,
                        type=None,
                    )
                ],
                metadata={},
            )
        if content == "" or content == {} or content == []:
            return OnexResultModel(
                status=OnexStatus.WARNING,
                target=str(path),
                messages=[
                    OnexMessageModel(
                        summary="Empty file",
                        level=LogLevelEnum.WARNING,
                        file=str(path),
                        line=0,
                        details=None,
                        code=None,
                        context=None,
                        timestamp=None,
                        type=None,
                    )
                ],
                metadata={"trace_hash": "dummyhash"},
            )
        return OnexResultModel(
            status=OnexStatus.WARNING,
            target=str(path),
            messages=[
                OnexMessageModel(
                    summary="Semantic validation failed",
                    level=LogLevelEnum.WARNING,
                    file=str(path),
                    line=0,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
                )
            ],
            metadata={},
        )

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        return OnexResultModel(
            status=OnexStatus.WARNING,
            target=str(path),
            messages=[
                OnexMessageModel(
                    summary="Validation dummy",
                    level=LogLevelEnum.WARNING,
                    file=str(path),
                    line=0,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
                )
            ],
            metadata={},
        )

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def compute_hash(self, path: Path, content: str, **kwargs: Any) -> Optional[str]:
        return "dummy_hash"


class SmartDummyJsonHandler(ProtocolFileTypeHandler):
    """
    Smart dummy JSON handler with content-aware behavior.

    Similar to SmartDummyYamlHandler but for JSON files.
    """

    file_type = "json"

    # Handler metadata properties (required by ProtocolFileTypeHandler)
    @property
    def handler_name(self) -> str:
        """Unique name for this handler."""
        return "smart_dummy_json_handler"

    @property
    def handler_version(self) -> str:
        """Version of this handler implementation."""
        return "1.0.0"

    @property
    def handler_author(self) -> str:
        """Author or team responsible for this handler."""
        return "OmniNode Test Team"

    @property
    def handler_description(self) -> str:
        """Brief description of what this handler does."""
        return "Smart dummy JSON handler with content-aware behavior (testing only)"

    @property
    def supported_extensions(self) -> list[str]:
        """List of file extensions this handler supports."""
        return [".json"]

    @property
    def supported_filenames(self) -> list[str]:
        """List of specific filenames this handler supports."""
        return []  # JSON handler works with extensions

    @property
    def handler_priority(self) -> int:
        """Default priority for this handler."""
        return 0  # Test/plugin handler priority (lowest)

    @property
    def requires_content_analysis(self) -> bool:
        """Whether this handler needs to analyze file content."""
        return True  # Smart handler analyzes content for behavior

    def can_handle(self, path: Path, content: str) -> bool:
        return True

    def extract_block(self, path: Path, content: str) -> Tuple[Optional[Any], str]:
        return None, content

    def serialize_block(self, meta: Any) -> str:
        return ""

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        if content is None:
            return OnexResultModel(
                status=OnexStatus.ERROR,
                target=str(path),
                messages=[
                    OnexMessageModel(
                        summary="File does not exist",
                        level=LogLevelEnum.ERROR,
                        file=str(path),
                        line=0,
                        details=None,
                        code=None,
                        context=None,
                        timestamp=None,
                        type=None,
                    )
                ],
                metadata={},
            )
        if content == "" or content == {} or content == []:
            return OnexResultModel(
                status=OnexStatus.WARNING,
                target=str(path),
                messages=[
                    OnexMessageModel(
                        summary="Empty file",
                        level=LogLevelEnum.WARNING,
                        file=str(path),
                        line=0,
                        details=None,
                        code=None,
                        context=None,
                        timestamp=None,
                        type=None,
                    )
                ],
                metadata={"trace_hash": "dummyhash"},
            )
        return OnexResultModel(
            status=OnexStatus.WARNING,
            target=str(path),
            messages=[
                OnexMessageModel(
                    summary="Semantic validation failed",
                    level=LogLevelEnum.WARNING,
                    file=str(path),
                    line=0,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
                )
            ],
            metadata={},
        )

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        return OnexResultModel(
            status=OnexStatus.WARNING,
            target=str(path),
            messages=[
                OnexMessageModel(
                    summary="Validation dummy",
                    level=LogLevelEnum.WARNING,
                    file=str(path),
                    line=0,
                    details=None,
                    code=None,
                    context=None,
                    timestamp=None,
                    type=None,
                )
            ],
            metadata={},
        )

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def compute_hash(self, path: Path, content: str, **kwargs: Any) -> Optional[str]:
        return "dummy_hash"


# Global variables for backward compatibility with existing tests
# These can be set by tests that need to control the behavior
CURRENT_EXPECTED_STATUS: Optional[OnexStatus] = None
CURRENT_EXPECTED_MESSAGE: Optional[str] = None


def get_global_status() -> OnexStatus:
    """Get the global expected status."""
    return CURRENT_EXPECTED_STATUS or OnexStatus.SUCCESS


def get_global_message() -> str:
    """Get the global expected message."""
    return CURRENT_EXPECTED_MESSAGE or "Global dummy handler result"


# Backward-compatible handlers that use global variables
class GlobalDummyYamlHandler(ConfigurableDummyHandler):
    """Dummy YAML handler that uses global variables for status/message."""

    def __init__(self, **kwargs: Any):
        super().__init__(
            file_type="yaml",
            status_provider=get_global_status,
            message_provider=get_global_message,
            **kwargs,
        )


class GlobalDummyJsonHandler(ConfigurableDummyHandler):
    """Dummy JSON handler that uses global variables for status/message."""

    def __init__(self, **kwargs: Any):
        super().__init__(
            file_type="json",
            status_provider=get_global_status,
            message_provider=get_global_message,
            **kwargs,
        )
