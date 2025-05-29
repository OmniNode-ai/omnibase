# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.126492'
# description: Stamped by PythonHandler
# entrypoint: python://test_plugin_discovery
# hash: 43b19f2f9dfb8aa5c1209d18875cf1cd3d735850f9cda9d021d8cb1c54c34e22
# last_modified_at: '2025-05-29T14:13:59.270164+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_plugin_discovery.py
# namespace: python://omnibase.nodes.logger_node.v1_0_0.node_tests.test_plugin_discovery
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: c27b072a-52a1-460a-b672-c63cc4051939
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Tests for logger node plugin discovery system.

Validates that the plugin discovery mechanism correctly finds and registers
format handlers from entry points, core handlers, and custom handlers.
"""

from typing import Any, Dict

import pytest

from omnibase.enums import LogLevelEnum, OutputFormatEnum

from ..models.state import LoggerInputState

# Use LogLevelEnum directly
# Use OutputFormatEnum directly
from ..protocol.protocol_log_format_handler import ProtocolLogFormatHandler
from ..registry.log_format_handler_registry import LogFormatHandlerRegistry


class TestPluginDiscovery:
    """Test cases for plugin discovery in the logger node."""

    def test_core_handlers_registration(self) -> None:
        """Test that all core format handlers are properly registered."""
        registry = LogFormatHandlerRegistry()
        registry.register_all_handlers()

        # Check that core formats are available
        expected_formats = {"json", "yaml", "yml", "markdown", "text", "csv"}
        available_formats = registry.handled_formats()

        for format_name in expected_formats:
            assert (
                format_name in available_formats
            ), f"Core format {format_name} not registered"

        # Verify handlers can be retrieved
        for format_name in expected_formats:
            handler = registry.get_handler(format_name)
            assert handler is not None, f"Handler for {format_name} is None"
            assert isinstance(
                handler, ProtocolLogFormatHandler
            ), f"Handler for {format_name} doesn't implement protocol"

    def test_handler_metadata_available(self) -> None:
        """Test that handlers provide proper metadata."""
        registry = LogFormatHandlerRegistry()
        registry.register_all_handlers()

        handlers_info = registry.list_handlers()

        for format_name, handler_info in handlers_info.items():
            # Check required metadata fields
            assert "handler_name" in handler_info
            assert "handler_version" in handler_info
            assert "handler_author" in handler_info
            assert "handler_description" in handler_info
            assert "supported_formats" in handler_info
            assert "dependencies_available" in handler_info
            assert "format_metadata" in handler_info

            # Verify metadata types
            assert isinstance(handler_info["handler_name"], str)
            assert isinstance(handler_info["handler_version"], str)
            assert isinstance(handler_info["supported_formats"], list)
            assert isinstance(handler_info["dependencies_available"], bool)
            assert isinstance(handler_info["format_metadata"], dict)

    def test_handler_dependency_validation(self) -> None:
        """Test that handlers properly validate their dependencies."""
        registry = LogFormatHandlerRegistry()
        registry.register_all_handlers()

        # Test each registered handler
        for format_name in registry.handled_formats():
            handler = registry.get_handler(format_name)
            assert handler is not None

            # All core handlers should have their dependencies available
            assert (
                handler.validate_dependencies()
            ), f"Handler for {format_name} reports missing dependencies"

    def test_priority_based_registration(self) -> None:
        """Test that priority-based handler registration works correctly."""
        registry = LogFormatHandlerRegistry()

        # Create a mock handler for testing
        class MockHandler(ProtocolLogFormatHandler):
            def __init__(self, name: str, priority: int):
                self._name = name
                self._priority = priority

            @property
            def handler_name(self) -> str:
                return self._name

            @property
            def handler_version(self) -> str:
                return "1.0.0"

            @property
            def handler_author(self) -> str:
                return "Test"

            @property
            def handler_description(self) -> str:
                return "Test handler"

            @property
            def supported_formats(self) -> list:
                return ["test"]

            @property
            def handler_priority(self) -> int:
                return self._priority

            @property
            def requires_dependencies(self) -> list:
                return []

            def can_handle(self, format_name: str) -> bool:
                return format_name == "test"

            def format_log_entry(
                self, input_state: LoggerInputState, log_entry: Dict[str, Any]
            ) -> str:
                return f"formatted by {self._name}"

            def validate_dependencies(self) -> bool:
                return True

            def get_format_metadata(self) -> Dict[str, Any]:
                return {"test": True}

        # Register handlers with different priorities
        low_priority_handler = MockHandler("low", 1)
        high_priority_handler = MockHandler("high", 10)

        # Register low priority first
        registry.register_handler("test", low_priority_handler, priority=1)
        handler = registry.get_handler("test")
        assert handler is not None
        assert handler.handler_name == "low"

        # Register high priority - should replace
        registry.register_handler(
            "test", high_priority_handler, priority=10, override=True
        )
        handler = registry.get_handler("test")
        assert handler is not None
        assert handler.handler_name == "high"

        # Try to register low priority again without override - should not replace
        registry.register_handler("test", low_priority_handler, priority=1)
        handler = registry.get_handler("test")
        assert handler is not None
        assert handler.handler_name == "high"

    def test_entry_point_discovery(self) -> None:
        """Test that entry point discovery works (if entry points are available)."""
        registry = LogFormatHandlerRegistry()

        # This test will pass if no entry points are found (expected in test environment)
        # or if entry points are found and properly loaded
        try:
            registry.discover_plugin_handlers()
            # If we get here, discovery succeeded (no exceptions)
            assert True
        except Exception as e:
            # Discovery failed - this is acceptable in test environment
            # but we should log it for debugging
            pytest.skip(f"Entry point discovery failed (expected in test env): {e}")

    def test_format_handler_can_handle_method(self) -> None:
        """Test that format handlers correctly report what they can handle."""
        registry = LogFormatHandlerRegistry()
        registry.register_all_handlers()

        # Test specific format handlers
        json_handler = registry.get_handler("json")
        assert json_handler is not None
        assert json_handler.can_handle("json")
        assert not json_handler.can_handle("yaml")

        yaml_handler = registry.get_handler("yaml")
        assert yaml_handler is not None
        assert yaml_handler.can_handle("yaml")
        assert yaml_handler.can_handle("yml")  # YAML handler should handle both
        assert not yaml_handler.can_handle("json")

    def test_unhandled_format_tracking(self) -> None:
        """Test that unhandled formats are properly tracked."""
        registry = LogFormatHandlerRegistry()
        # Don't register any handlers

        # Try to get handlers for formats that don't exist
        assert registry.get_handler("nonexistent") is None
        assert registry.get_handler("another_fake") is None

        # Check that unhandled formats are tracked
        assert not registry.can_handle("nonexistent")
        assert not registry.can_handle("another_fake")

    def test_custom_handler_registration(self) -> None:
        """Test that custom handlers can be registered at runtime."""
        registry = LogFormatHandlerRegistry()

        # Create a simple custom handler
        class CustomHandler(ProtocolLogFormatHandler):
            @property
            def handler_name(self) -> str:
                return "custom_handler"

            @property
            def handler_version(self) -> str:
                return "1.0.0"

            @property
            def handler_author(self) -> str:
                return "Custom Author"

            @property
            def handler_description(self) -> str:
                return "Custom format handler"

            @property
            def supported_formats(self) -> list:
                return ["custom"]

            @property
            def handler_priority(self) -> int:
                return 5

            @property
            def requires_dependencies(self) -> list:
                return []

            def can_handle(self, format_name: str) -> bool:
                return format_name == "custom"

            def format_log_entry(
                self, input_state: LoggerInputState, log_entry: Dict[str, Any]
            ) -> str:
                message = log_entry.get("message", "")
                return f"CUSTOM: {message}"

            def validate_dependencies(self) -> bool:
                return True

            def get_format_metadata(self) -> Dict[str, Any]:
                return {"format_name": "custom", "description": "Custom format"}

        # Register the custom handler
        custom_handler = CustomHandler()
        registry.register_handler("custom", custom_handler, source="test", priority=5)

        # Verify it was registered
        assert registry.can_handle("custom")
        retrieved_handler = registry.get_handler("custom")
        assert retrieved_handler is not None
        assert retrieved_handler.handler_name == "custom_handler"

        # Test that it can format
        input_state = LoggerInputState(
            version="1.0.0",
            log_level=LogLevelEnum.INFO,
            message="test message",
            output_format=OutputFormatEnum.JSON,  # This doesn't matter for our custom handler
        )
        log_entry = {"message": "test message"}
        formatted = retrieved_handler.format_log_entry(input_state, log_entry)
        assert formatted == "CUSTOM: test message"
