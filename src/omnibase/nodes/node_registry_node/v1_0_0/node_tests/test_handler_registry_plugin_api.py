# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:28.025545'
# description: Stamped by PythonHandler
# entrypoint: python://test_handler_registry_plugin_api.py
# hash: 9180ad8b679cd46d38cb01749dd4e4c29b1f93806210c1fe598451e42c075695
# last_modified_at: '2025-05-29T13:51:23.685004+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_handler_registry_plugin_api.py
# namespace: py://omnibase.tests.protocol.test_handler_registry_plugin_api_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: b4ed8a69-c639-4c05-b20e-07d65fbe7583
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Test suite for FileTypeHandlerRegistry plugin/override API (event-driven refactor).

Tests the enhanced handler registration system including:
- Runtime handler registration and override
- Priority-based conflict resolution
- Handler metadata and introspection
- Node-local handler extensions

All tests use the event_driven_registry fixture for protocol-compliant, event-driven registration.
"""

from pathlib import Path
from typing import Any, List, Optional

import pytest

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.enums import OnexStatus
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from .node_registry_test_cases import NODE_REGISTRY_TEST_CASES
from omnibase.model.model_enum_metadata import NodeMetadataField
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.nodes.node_constants import (
    TEST_HANDLER_NAME, NAMED_HANDLER_NAME, AUTO_HANDLER_NAME, LOW_PRIORITY_HANDLER, HIGH_PRIORITY_HANDLER,
    ORIGINAL_HANDLER, OVERRIDE_HANDLER, SPECIAL_HANDLER, TEST_EXTENSION, AUTO_EXTENSION, CONFLICT_EXTENSION,
    SPECIAL_CONFIG, MY_PROCESSOR, NAMED1, SPECIAL1,
    SOURCE_TEST, SOURCE_CORE, SOURCE_PLUGIN, SOURCE_RUNTIME,
    HANDLER_ARG_CUSTOM_PARAM, HANDLER_ARG_TEST_VALUE,
    HANDLER_TYPE_EXTENSION, HANDLER_TYPE_NAMED, HANDLER_TYPE_SPECIAL
)

# Helper: Event-driven handler registration
class MockCustomHandler(ProtocolFileTypeHandler):
    """Mock custom handler for testing."""
    def __init__(self, name: str = TEST_HANDLER_NAME, **kwargs: Any) -> None:
        self.name = name
        self.kwargs = kwargs
    @property
    def handler_name(self) -> str: return self.name
    @property
    def handler_version(self) -> str: return "1.0.0"
    @property
    def handler_author(self) -> str: return "Test Suite"
    @property
    def handler_description(self) -> str: return f"Mock handler: {self.name}"
    @property
    def supported_extensions(self) -> List[str]: return [".mock", ".test"]
    @property
    def supported_filenames(self) -> List[str]: return ["mock_file.txt"]
    @property
    def handler_priority(self) -> int: return 0
    @property
    def requires_content_analysis(self) -> bool: return True
    def can_handle(self, path: Path, content: str) -> bool: return True
    def extract_block(self, path: Path, content: str) -> tuple[Optional[Any], str]: return None, content
    def serialize_block(self, meta: Any) -> str: return ""
    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        return OnexResultModel(status=OnexStatus.SUCCESS, target=str(path), messages=[], metadata={"handler": self.name})
    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        return OnexResultModel(status=OnexStatus.SUCCESS, target=str(path), messages=[], metadata={"validated": True})
    def pre_validate(self, path: Path, content: str, **kwargs: Any) -> Optional[OnexResultModel]: return None
    def post_validate(self, path: Path, content: str, **kwargs: Any) -> Optional[OnexResultModel]: return None

class TestHandlerRegistryPluginAPI:
    def test_enhanced_handler_registration(self, handler_registry):
        handler_registry.clear_registry()
        handler = MockCustomHandler(TEST_HANDLER_NAME)
        handler_registry.register_handler(TEST_EXTENSION, handler, source=SOURCE_TEST, priority=20)
        retrieved = handler_registry.get_handler(Path(f"test{TEST_EXTENSION}"))
        assert retrieved is handler
        assert TEST_EXTENSION in handler_registry.handled_extensions()

    def test_named_handler_registration(self, handler_registry):
        handler_registry.clear_registry()
        handler = MockCustomHandler(NAMED_HANDLER_NAME)
        handler_registry.register_handler(MY_PROCESSOR, handler, source=SOURCE_TEST)
        retrieved = handler_registry.get_named_handler(MY_PROCESSOR)
        assert retrieved is handler
        assert MY_PROCESSOR in handler_registry.handled_names()

    def test_handler_class_instantiation(self, handler_registry):
        handler_registry.clear_registry()
        handler_registry.register_handler(
            AUTO_EXTENSION,
            MockCustomHandler,  # Class, not instance
            source=SOURCE_TEST,
            name=AUTO_HANDLER_NAME,
            **{HANDLER_ARG_CUSTOM_PARAM: HANDLER_ARG_TEST_VALUE},
        )
        handler = handler_registry.get_handler(Path(f"test{AUTO_EXTENSION}"))
        assert handler is not None
        assert isinstance(handler, MockCustomHandler)
        assert handler.name == AUTO_HANDLER_NAME
        assert handler.kwargs[HANDLER_ARG_CUSTOM_PARAM] == HANDLER_ARG_TEST_VALUE

    def test_priority_based_conflict_resolution(self, handler_registry):
        handler_registry.clear_registry()
        low_priority_handler = MockCustomHandler(LOW_PRIORITY_HANDLER)
        high_priority_handler = MockCustomHandler(HIGH_PRIORITY_HANDLER)
        handler_registry.register_handler(CONFLICT_EXTENSION, low_priority_handler, priority=10)
        handler_registry.register_handler(CONFLICT_EXTENSION, high_priority_handler, priority=20)
        retrieved = handler_registry.get_handler(Path(f"test{CONFLICT_EXTENSION}"))
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == HIGH_PRIORITY_HANDLER

    def test_override_functionality(self, handler_registry):
        handler_registry.clear_registry()
        original_handler = MockCustomHandler(ORIGINAL_HANDLER)
        override_handler = MockCustomHandler(OVERRIDE_HANDLER)
        handler_registry.register_handler(CONFLICT_EXTENSION, original_handler, priority=50)
        handler_registry.register_handler(CONFLICT_EXTENSION, override_handler, priority=10)
        retrieved = handler_registry.get_handler(Path(f"test{CONFLICT_EXTENSION}"))
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == ORIGINAL_HANDLER
        handler_registry.register_handler(
            CONFLICT_EXTENSION, override_handler, priority=10, override=True
        )
        retrieved = handler_registry.get_handler(Path(f"test{CONFLICT_EXTENSION}"))
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == OVERRIDE_HANDLER

    def test_special_handler_registration(self, handler_registry):
        handler_registry.clear_registry()
        handler = MockCustomHandler(SPECIAL_HANDLER)
        handler_registry.register_special(SPECIAL_CONFIG, handler, source=SOURCE_TEST, priority=30)
        retrieved = handler_registry.get_handler(Path(SPECIAL_CONFIG))
        assert retrieved is handler
        assert SPECIAL_CONFIG in handler_registry.handled_specials()

    def test_handler_metadata_listing(self, handler_registry):
        handler_registry.clear_registry()
        handler_registry.register_handler(
            TEST_EXTENSION, MockCustomHandler(), source=SOURCE_CORE, priority=100
        )
        handler_registry.register_handler(
            NAMED1, MockCustomHandler(), source=SOURCE_PLUGIN, priority=5
        )
        handler_registry.register_special(
            SPECIAL1, MockCustomHandler(), source=SOURCE_RUNTIME, priority=50
        )
        handlers = handler_registry.list_handlers()
        assert any(h["type"] == HANDLER_TYPE_EXTENSION for h in handlers.values())
        assert any(h["type"] == HANDLER_TYPE_NAMED for h in handlers.values())
        assert any(h["type"] == HANDLER_TYPE_SPECIAL for h in handlers.values())

    # ... Repeat for all other tests, using handler_registry fixture ...

    # ... existing code ... 

@pytest.mark.parametrize("case", NODE_REGISTRY_TEST_CASES, ids=lambda c: c.id)
def test_handler_registry_cases(case, handler_registry):
    """
    Canonical registry-driven handler registry test runner.
    Each test case is executed with the injected handler_registry fixture.
    """
    case.run(handler_registry)

def test_enum_matches_model():
    """
    Ensure NodeMetadataField Enum and NodeMetadataBlock model fields are always in sync.
    """
    model_fields = set(NodeMetadataBlock.model_fields.keys())
    enum_fields = set(f.value for f in NodeMetadataField)
    assert model_fields == enum_fields 