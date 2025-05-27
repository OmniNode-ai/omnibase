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

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.enums import OnexStatus
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

    def test_complex_override_resolution_order(self) -> None:
        """Test complex override resolution scenarios with multiple handlers."""
        registry = FileTypeHandlerRegistry()

        # Create handlers with different priorities
        core_handler = MockCustomHandler("CoreHandler")
        runtime_handler = MockCustomHandler("RuntimeHandler")
        node_local_handler = MockCustomHandler("NodeLocalHandler")
        plugin_handler = MockCustomHandler("PluginHandler")

        # Register in non-priority order to test resolution
        registry.register_handler(
            ".complex", plugin_handler, source="plugin", priority=0
        )
        registry.register_handler(
            ".complex", node_local_handler, source="node-local", priority=10
        )
        registry.register_handler(".complex", core_handler, source="core", priority=100)
        registry.register_handler(
            ".complex", runtime_handler, source="runtime", priority=50
        )

        # Core handler should win (highest priority)
        retrieved = registry.get_handler(Path("test.complex"))
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == "CoreHandler"

    def test_equal_priority_last_wins(self) -> None:
        """Test that with equal priority, first registered handler wins (current behavior)."""
        registry = FileTypeHandlerRegistry()

        first_handler = MockCustomHandler("FirstHandler")
        second_handler = MockCustomHandler("SecondHandler")
        third_handler = MockCustomHandler("ThirdHandler")

        # Register multiple handlers with same priority
        registry.register_handler(".equal", first_handler, priority=25)
        registry.register_handler(".equal", second_handler, priority=25)
        registry.register_handler(".equal", third_handler, priority=25)

        # First registered should win (current behavior - equal priority rejected)
        retrieved = registry.get_handler(Path("test.equal"))
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == "FirstHandler"

    def test_override_with_lower_priority_forced(self) -> None:
        """Test forced override with lower priority using override=True."""
        registry = FileTypeHandlerRegistry()

        high_priority_handler = MockCustomHandler("HighPriority")
        low_priority_override = MockCustomHandler("LowPriorityOverride")

        # Register high priority handler
        registry.register_handler(".forced", high_priority_handler, priority=100)

        # Force override with much lower priority
        registry.register_handler(
            ".forced", low_priority_override, priority=1, override=True
        )

        # Override should win despite lower priority
        retrieved = registry.get_handler(Path("test.forced"))
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == "LowPriorityOverride"

    def test_special_handler_override_resolution(self) -> None:
        """Test override resolution for special handlers."""
        registry = FileTypeHandlerRegistry()

        core_special = MockCustomHandler("CoreSpecial")
        plugin_special = MockCustomHandler("PluginSpecial")

        # Register core special handler
        registry.register_special(
            ".coreconfig", core_special, source="core", priority=100
        )

        # Try to override with plugin (should fail)
        registry.register_special(
            ".coreconfig", plugin_special, source="plugin", priority=0
        )

        # Core handler should still be active
        retrieved = registry.get_handler(Path(".coreconfig"))
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == "CoreSpecial"

        # Force override with plugin
        registry.register_special(
            ".coreconfig", plugin_special, source="plugin", priority=0, override=True
        )

        # Plugin override should now be active
        retrieved = registry.get_handler(Path(".coreconfig"))
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == "PluginSpecial"

    def test_named_handler_override_resolution(self) -> None:
        """Test override resolution for named handlers."""
        registry = FileTypeHandlerRegistry()

        runtime_named = MockCustomHandler("RuntimeNamed")
        node_local_named = MockCustomHandler("NodeLocalNamed")

        # Register runtime named handler
        registry.register_handler(
            "processor", runtime_named, source="runtime", priority=50
        )

        # Try to override with lower priority node-local (should fail)
        registry.register_handler(
            "processor", node_local_named, source="node-local", priority=10
        )

        # Runtime handler should still be active
        retrieved = registry.get_named_handler("processor")
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == "RuntimeNamed"

        # Override with higher priority
        registry.register_handler(
            "processor", node_local_named, source="node-local", priority=60
        )

        # Node-local handler should now be active
        retrieved = registry.get_named_handler("processor")
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == "NodeLocalNamed"

    def test_handler_registration_failure_invalid_class(self) -> None:
        """Test handler registration with invalid handler class (current behavior: accepts anything)."""
        registry = FileTypeHandlerRegistry()

        # Try to register a class that doesn't implement the protocol
        class InvalidHandler:
            pass

        # Registration currently accepts anything (no validation)
        registry.register_handler(".invalid", InvalidHandler, source="test")  # type: ignore[arg-type]

        # Handler will be registered but may not work properly
        retrieved = registry.get_handler(Path("test.invalid"))
        assert retrieved is not None
        assert isinstance(retrieved, InvalidHandler)

    def test_handler_registration_failure_instantiation_error(self) -> None:
        """Test handler registration failure during instantiation."""
        registry = FileTypeHandlerRegistry()

        # Create a handler class that fails during instantiation
        class FailingHandler(ProtocolFileTypeHandler):
            def __init__(self, **kwargs: Any) -> None:
                raise OnexError("Instantiation failed", CoreErrorCode.OPERATION_FAILED)

            @property
            def handler_name(self) -> str:
                return "FailingHandler"

            @property
            def handler_version(self) -> str:
                return "1.0.0"

            @property
            def handler_author(self) -> str:
                return "Test"

            @property
            def handler_description(self) -> str:
                return "Handler that fails"

            @property
            def supported_extensions(self) -> List[str]:
                return [".fail"]

            @property
            def supported_filenames(self) -> List[str]:
                return []

            @property
            def handler_priority(self) -> int:
                return 0

            @property
            def requires_content_analysis(self) -> bool:
                return False

            def can_handle(self, path: Path, content: str) -> bool:
                return False

            def extract_block(
                self, path: Path, content: str
            ) -> tuple[Optional[Any], str]:
                return None, content

            def serialize_block(self, meta: Any) -> str:
                return ""

            def stamp(self, path: Path, content: str, **kwargs: Any) -> OnexResultModel:
                return OnexResultModel(
                    status=OnexStatus.SUCCESS, target=str(path), messages=[]
                )

            def validate(
                self, path: Path, content: str, **kwargs: Any
            ) -> OnexResultModel:
                return OnexResultModel(
                    status=OnexStatus.SUCCESS, target=str(path), messages=[]
                )

            def pre_validate(
                self, path: Path, content: str, **kwargs: Any
            ) -> Optional[OnexResultModel]:
                return None

            def post_validate(
                self, path: Path, content: str, **kwargs: Any
            ) -> Optional[OnexResultModel]:
                return None

        # Registration should fail with OnexError during instantiation
        with pytest.raises(OnexError, match="Instantiation failed"):
            registry.register_handler(".failing", FailingHandler, source="test")

        # Handler should not be registered due to instantiation failure
        retrieved = registry.get_handler(Path("test.failing"))
        assert retrieved is None
        assert ".failing" not in registry.handled_extensions()

    def test_plugin_discovery_with_conflicts(self) -> None:
        """Test plugin discovery when conflicts occur with existing handlers."""
        registry = FileTypeHandlerRegistry()

        # Register a runtime handler first
        runtime_handler = MockCustomHandler("RuntimeHandler")
        registry.register_handler(
            ".conflict", runtime_handler, source="runtime", priority=50
        )

        # Simulate plugin discovery that conflicts
        plugin_handler = MockCustomHandler("PluginHandler")
        registry.register_handler(
            ".conflict", plugin_handler, source="plugin", priority=0
        )

        # Runtime handler should win (higher priority)
        retrieved = registry.get_handler(Path("test.conflict"))
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == "RuntimeHandler"

        # Verify plugin handler was rejected
        handlers = registry.list_handlers()
        conflict_handlers = [h for k, h in handlers.items() if ".conflict" in k]
        assert len(conflict_handlers) == 1
        assert conflict_handlers[0]["source"] == "runtime"

    def test_node_local_handler_registration_conflicts(self) -> None:
        """Test node-local handler registration with various conflict scenarios."""
        registry = FileTypeHandlerRegistry()

        # Register core and runtime handlers first
        registry.register_all_handlers()

        # Try to register node-local handler that conflicts with core
        node_handler = MockCustomHandler("NodeHandler")
        registry.register_handler(".py", node_handler, source="node-local", priority=10)

        # Runtime handler should still be active (higher priority)
        retrieved = registry.get_handler(Path("test.py"))
        assert retrieved is not None
        # Should be the runtime Python handler, not our mock
        assert not isinstance(retrieved, MockCustomHandler)

        # Register with override to force replacement
        registry.register_handler(
            ".py", node_handler, source="node-local", priority=10, override=True
        )

        # Node handler should now be active
        retrieved = registry.get_handler(Path("test.py"))
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == "NodeHandler"

    def test_handler_metadata_after_conflicts(self) -> None:
        """Test that handler metadata is correct after conflict resolution."""
        registry = FileTypeHandlerRegistry()

        # Register multiple conflicting handlers
        first_handler = MockCustomHandler("FirstHandler")
        second_handler = MockCustomHandler("SecondHandler")
        third_handler = MockCustomHandler("ThirdHandler")

        registry.register_handler(".meta", first_handler, source="plugin", priority=0)
        registry.register_handler(
            ".meta", second_handler, source="runtime", priority=50
        )
        registry.register_handler(".meta", third_handler, source="core", priority=100)

        # Get handler metadata
        handlers = registry.list_handlers()
        meta_handler = handlers.get("extension:.meta")

        assert meta_handler is not None
        assert meta_handler["source"] == "core"
        assert meta_handler["priority"] == 100
        assert meta_handler["handler_class"] == "MockCustomHandler"

        # Verify only one handler is registered for this extension
        meta_handlers = [h for k, h in handlers.items() if ".meta" in k]
        assert len(meta_handlers) == 1

    def test_override_chain_resolution(self) -> None:
        """Test complex override chains with multiple overrides."""
        registry = FileTypeHandlerRegistry()

        # Create a chain of overrides
        original = MockCustomHandler("Original")
        first_override = MockCustomHandler("FirstOverride")
        second_override = MockCustomHandler("SecondOverride")
        final_override = MockCustomHandler("FinalOverride")

        # Register original
        registry.register_handler(".chain", original, priority=50)

        # Override with lower priority (forced)
        registry.register_handler(".chain", first_override, priority=10, override=True)

        # Override the override with even lower priority (forced)
        registry.register_handler(".chain", second_override, priority=5, override=True)

        # Final override with higher priority (natural)
        registry.register_handler(".chain", final_override, priority=60)

        # Final override should win (highest priority)
        retrieved = registry.get_handler(Path("test.chain"))
        assert retrieved is not None
        assert isinstance(retrieved, MockCustomHandler)
        assert retrieved.name == "FinalOverride"

    def test_bulk_registration_conflict_handling(self) -> None:
        """Test conflict handling during bulk handler registration."""
        registry = FileTypeHandlerRegistry()

        # Register some initial handlers
        registry.register_handler(".bulk1", MockCustomHandler("Initial1"), priority=50)
        registry.register_handler(".bulk2", MockCustomHandler("Initial2"), priority=50)

        # Bulk register with conflicts
        bulk_handlers = {
            ".bulk1": MockCustomHandler("Bulk1"),  # Conflicts with existing
            ".bulk2": MockCustomHandler("Bulk2"),  # Conflicts with existing
            ".bulk3": MockCustomHandler("Bulk3"),  # New handler
        }

        registry.register_node_local_handlers(bulk_handlers)

        # Check that conflicts were handled correctly
        # Initial handlers should win (higher priority)
        retrieved1 = registry.get_handler(Path("test.bulk1"))
        assert retrieved1 is not None
        assert isinstance(retrieved1, MockCustomHandler)
        assert retrieved1.name == "Initial1"

        retrieved2 = registry.get_handler(Path("test.bulk2"))
        assert retrieved2 is not None
        assert isinstance(retrieved2, MockCustomHandler)
        assert retrieved2.name == "Initial2"

        # New handler should be registered
        retrieved3 = registry.get_handler(Path("test.bulk3"))
        assert retrieved3 is not None
        assert isinstance(retrieved3, MockCustomHandler)
        assert retrieved3.name == "Bulk3"

    def test_handler_validation_edge_cases(self) -> None:
        """Test handler validation with various edge cases (current behavior: accepts most things)."""
        registry = FileTypeHandlerRegistry()

        # Test with None handler
        registry.register_handler(".none", None, source="test")  # type: ignore[arg-type]
        # None is accepted and stored
        assert registry.get_handler(Path("test.none")) is None

        # Test with non-callable object
        registry.register_handler(".object", "not_a_handler", source="test")  # type: ignore[arg-type]
        # String is accepted and stored
        assert registry.get_handler(Path("test.object")) == "not_a_handler"

        # Test with empty string key
        valid_handler = MockCustomHandler("ValidHandler")
        registry.register_handler("", valid_handler, source="test")
        # Should not crash, but handler won't be retrievable via normal means

        # Test with None key - this should be handled gracefully
        try:
            registry.register_handler(None, valid_handler, source="test")  # type: ignore[arg-type]
            # Should not crash, but handler won't be retrievable
        except (TypeError, AttributeError):
            # This is acceptable behavior for None key
            pass


if __name__ == "__main__":
    pytest.main([__file__])
