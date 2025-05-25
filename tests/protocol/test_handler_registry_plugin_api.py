# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_handler_registry_plugin_api.py
# version: 1.0.0
# uuid: 26df51cd-d1e7-44f9-b8db-1db651c00f01
# author: OmniNode Team
# created_at: 2025-05-25T09:28:51.212005
# last_modified_at: 2025-05-25T16:00:39.946322
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 947ff6e0dac334c6dd9b47f98490e72d49edaf6b199264baf90c7a9554ad1525
# entrypoint: python@test_handler_registry_plugin_api.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_handler_registry_plugin_api
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Test suite for FileTypeHandlerRegistry plugin/override API.

Tests the enhanced handler registration system including:
- Runtime handler registration and override
- Priority-based conflict resolution
- Handler metadata and introspection
- Node-local handler extensions
"""

from pathlib import Path
from typing import Any, List, Optional

import pytest

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.model.enum_onex_status import OnexStatus
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler


class MockCustomHandler(ProtocolFileTypeHandler):
    """Mock custom handler for testing."""

    def __init__(self, name: str = "MockCustomHandler", **kwargs: Any) -> None:
        self.name = name
        self.kwargs = kwargs

    # Required metadata properties
    @property
    def handler_name(self) -> str:
        return self.name

    @property
    def handler_version(self) -> str:
        return "1.0.0"

    @property
    def handler_author(self) -> str:
        return "Test Suite"

    @property
    def handler_description(self) -> str:
        return f"Mock handler: {self.name}"

    @property
    def supported_extensions(self) -> List[str]:
        return [".mock", ".test"]

    @property
    def supported_filenames(self) -> List[str]:
        return ["mock_file.txt"]

    @property
    def handler_priority(self) -> int:
        return 0

    @property
    def requires_content_analysis(self) -> bool:
        return True

    def can_handle(self, path: Path, content: str) -> bool:
        return True

    def extract_block(self, path: Path, content: str) -> tuple[Optional[Any], str]:
        return None, content

    def serialize_block(self, meta: Any) -> str:
        return ""

    def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(path),
            messages=[],
            metadata={"handler": self.name},
        )

    def validate(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
        return OnexResultModel(
            status=OnexStatus.SUCCESS,
            target=str(path),
            messages=[],
            metadata={"validated": True},
        )

    def pre_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None

    def post_validate(
        self, path: Path, content: str, **kwargs: Any
    ) -> Optional[OnexResultModel]:
        return None


class TestHandlerRegistryPluginAPI:
    """Test suite for handler registry plugin/override API."""

    def test_enhanced_handler_registration(self) -> None:
        """Test enhanced handler registration with priority and source."""
        registry = FileTypeHandlerRegistry()
        handler = MockCustomHandler("TestHandler")

        # Test extension registration with metadata
        registry.register_handler(".test", handler, source="test", priority=20)

        # Verify registration
        retrieved = registry.get_handler(Path("test.test"))
        assert retrieved is handler
        assert ".test" in registry.handled_extensions()

    def test_named_handler_registration(self) -> None:
        """Test named handler registration."""
        registry = FileTypeHandlerRegistry()
        handler = MockCustomHandler("NamedHandler")

        # Register named handler
        registry.register_handler("my_processor", handler, source="test")

        # Verify named handler retrieval
        retrieved = registry.get_named_handler("my_processor")
        assert retrieved is handler
        assert "my_processor" in registry.handled_names()

    def test_handler_class_instantiation(self) -> None:
        """Test automatic handler class instantiation."""
        registry = FileTypeHandlerRegistry()

        # Register handler class (not instance)
        registry.register_handler(
            ".auto",
            MockCustomHandler,  # Class, not instance
            source="test",
            name="AutoHandler",
            custom_param="test_value",
        )

        # Verify handler was instantiated with kwargs
        handler = registry.get_handler(Path("test.auto"))
        assert handler is not None
        assert isinstance(handler, MockCustomHandler)
        assert handler.name == "AutoHandler"  # name is passed as positional arg
        assert handler.kwargs["custom_param"] == "test_value"

    def test_priority_based_conflict_resolution(self) -> None:
        """Test priority-based conflict resolution."""
        registry = FileTypeHandlerRegistry()

        low_priority_handler = MockCustomHandler("LowPriority")
        high_priority_handler = MockCustomHandler("HighPriority")

        # Register low priority handler first
        registry.register_handler(".conflict", low_priority_handler, priority=10)

        # Try to register high priority handler
        registry.register_handler(".conflict", high_priority_handler, priority=20)

        # High priority should win
        retrieved = registry.get_handler(Path("test.conflict"))
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == "HighPriority"

    def test_override_functionality(self) -> None:
        """Test handler override functionality."""
        registry = FileTypeHandlerRegistry()

        original_handler = MockCustomHandler("Original")
        override_handler = MockCustomHandler("Override")

        # Register original handler with high priority
        registry.register_handler(".override", original_handler, priority=50)

        # Try to override with lower priority (should fail without override=True)
        registry.register_handler(".override", override_handler, priority=10)

        # Original should still be there
        retrieved = registry.get_handler(Path("test.override"))
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == "Original"

        # Now override with override=True
        registry.register_handler(
            ".override", override_handler, priority=10, override=True
        )

        # Override should now be active
        retrieved = registry.get_handler(Path("test.override"))
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == "Override"

    def test_special_handler_registration(self) -> None:
        """Test special handler registration patterns."""
        registry = FileTypeHandlerRegistry()
        handler = MockCustomHandler("SpecialHandler")

        # Register special handler
        registry.register_special("special.config", handler, source="test", priority=30)

        # Verify special handler retrieval
        retrieved = registry.get_handler(Path("special.config"))
        assert retrieved is handler
        assert "special.config" in registry.handled_specials()

    def test_handler_metadata_listing(self) -> None:
        """Test handler metadata listing functionality."""
        registry = FileTypeHandlerRegistry()

        # Register various handlers
        registry.register_handler(
            ".ext1", MockCustomHandler(), source="core", priority=100
        )
        registry.register_handler(
            "named1", MockCustomHandler(), source="plugin", priority=5
        )
        registry.register_special(
            "special1", MockCustomHandler(), source="runtime", priority=50
        )

        # Get handler metadata
        handlers = registry.list_handlers()

        # Verify metadata structure
        assert "extension:.ext1" in handlers
        assert "named:named1" in handlers
        assert "special:special1" in handlers

        # Check metadata content
        ext_meta = handlers["extension:.ext1"]
        assert ext_meta["type"] == "extension"
        assert ext_meta["source"] == "core"
        assert ext_meta["priority"] == 100
        assert ext_meta["handler_class"] == "MockCustomHandler"

    def test_node_local_handlers_convenience_method(self) -> None:
        """Test convenience method for node-local handler registration."""
        registry = FileTypeHandlerRegistry()

        handlers = {
            ".custom": MockCustomHandler("Custom"),
            "processor": MockCustomHandler("Processor"),
            "special:.config": MockCustomHandler("Config"),
        }

        # Register all handlers at once
        registry.register_node_local_handlers(handlers)

        # Verify all handlers were registered
        custom_handler = registry.get_handler(Path("test.custom"))
        assert custom_handler is not None
        assert isinstance(custom_handler, MockCustomHandler)
        assert custom_handler.name == "Custom"

        processor_handler = registry.get_named_handler("processor")
        assert processor_handler is not None
        assert isinstance(processor_handler, MockCustomHandler)
        assert processor_handler.name == "Processor"

        config_handler = registry.get_handler(Path(".config"))
        assert config_handler is not None
        assert isinstance(config_handler, MockCustomHandler)
        assert config_handler.name == "Config"

    def test_canonical_handlers_with_priorities(self) -> None:
        """Test canonical handlers have correct priorities."""
        registry = FileTypeHandlerRegistry()
        registry.register_all_handlers()

        # Get handler metadata
        handlers = registry.list_handlers()

        # Verify core handlers have highest priority
        ignore_handler = next(
            (h for k, h in handlers.items() if ".onexignore" in k), None
        )
        assert ignore_handler is not None
        assert ignore_handler["source"] == "core"
        assert ignore_handler["priority"] == 100

        # Verify runtime handlers have medium priority
        py_handler = next((h for k, h in handlers.items() if ".py" in k), None)
        assert py_handler is not None
        assert py_handler["source"] == "runtime"
        assert py_handler["priority"] == 50

    def test_backward_compatibility(self) -> None:
        """Test backward compatibility with existing handler patterns."""
        registry = FileTypeHandlerRegistry()
        handler = MockCustomHandler("Legacy")

        # Use old-style registration (should still work)
        registry.register_handler(".legacy", handler)

        # Verify it works
        retrieved = registry.get_handler(Path("test.legacy"))
        assert retrieved is handler


if __name__ == "__main__":
    pytest.main([__file__])
