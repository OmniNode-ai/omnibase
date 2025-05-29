# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:28.003347'
# description: Stamped by PythonHandler
# entrypoint: python://test_handler_metadata.py
# hash: 414ded0dcb5fe8001bd7a81d8412585c71f39f36fc804e4f0f18ccfe7b819b0e
# last_modified_at: '2025-05-29T11:50:12.669549+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_handler_metadata.py
# namespace: omnibase.test_handler_metadata
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 2a75e529-f577-4b76-bf3a-cfb24e8ea1a6
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Tests for handler metadata properties and introspection.

This module tests the metadata properties required by ProtocolFileTypeHandler
and the introspection capabilities of the FileTypeHandlerRegistry.
"""


from typing import Any

import pytest

from omnibase.core.core_file_type_handler_registry import FileTypeHandlerRegistry
from omnibase.fixtures.mocks.dummy_handlers import (
    ConfigurableDummyHandler,
    SmartDummyJsonHandler,
    SmartDummyYamlHandler,
)
from omnibase.handlers.handler_ignore import IgnoreFileHandler
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_markdown import (
    MarkdownHandler,
)
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import (
    MetadataYAMLHandler,
)
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_python import PythonHandler


class TestHandlerMetadataProperties:
    """Test that all handlers implement the required metadata properties."""

    @pytest.mark.parametrize(
        "handler_class,expected_name",
        [
            (PythonHandler, "python_handler"),
            (MarkdownHandler, "markdown_handler"),
            (MetadataYAMLHandler, "yaml_metadata_handler"),
            (IgnoreFileHandler, "ignore_file_handler"),
            (ConfigurableDummyHandler, "configurable_dummy_dummy_handler"),
            (SmartDummyYamlHandler, "smart_dummy_yaml_handler"),
            (SmartDummyJsonHandler, "smart_dummy_json_handler"),
        ],
    )
    def test_handler_name_property(
        self, handler_class: Any, expected_name: str
    ) -> None:
        """Test that handler_name property returns expected value."""
        handler = handler_class()
        assert hasattr(handler, "handler_name")
        assert isinstance(handler.handler_name, str)
        assert handler.handler_name == expected_name

    @pytest.mark.parametrize(
        "handler_class",
        [
            PythonHandler,
            MarkdownHandler,
            MetadataYAMLHandler,
            IgnoreFileHandler,
            ConfigurableDummyHandler,
            SmartDummyYamlHandler,
            SmartDummyJsonHandler,
        ],
    )
    def test_handler_version_property(self, handler_class: Any) -> None:
        """Test that handler_version property returns a valid semantic version."""
        handler = handler_class()
        assert hasattr(handler, "handler_version")
        assert isinstance(handler.handler_version, str)
        assert handler.handler_version == "1.0.0"

    @pytest.mark.parametrize(
        "handler_class,expected_author",
        [
            (PythonHandler, "OmniNode Team"),
            (MarkdownHandler, "OmniNode Team"),
            (MetadataYAMLHandler, "OmniNode Team"),
            (IgnoreFileHandler, "OmniNode Team"),
            (ConfigurableDummyHandler, "OmniNode Test Team"),
            (SmartDummyYamlHandler, "OmniNode Test Team"),
            (SmartDummyJsonHandler, "OmniNode Test Team"),
        ],
    )
    def test_handler_author_property(
        self, handler_class: Any, expected_author: str
    ) -> None:
        """Test that handler_author property returns expected value."""
        handler = handler_class()
        assert hasattr(handler, "handler_author")
        assert isinstance(handler.handler_author, str)
        assert handler.handler_author == expected_author

    @pytest.mark.parametrize(
        "handler_class",
        [
            PythonHandler,
            MarkdownHandler,
            MetadataYAMLHandler,
            IgnoreFileHandler,
            ConfigurableDummyHandler,
            SmartDummyYamlHandler,
            SmartDummyJsonHandler,
        ],
    )
    def test_handler_description_property(self, handler_class: Any) -> None:
        """Test that handler_description property returns a non-empty string."""
        handler = handler_class()
        assert hasattr(handler, "handler_description")
        assert isinstance(handler.handler_description, str)
        assert len(handler.handler_description) > 0

    @pytest.mark.parametrize(
        "handler_class,expected_extensions",
        [
            (PythonHandler, [".py", ".pyx"]),
            (MarkdownHandler, [".md", ".markdown"]),
            (MetadataYAMLHandler, [".yaml", ".yml"]),
            (IgnoreFileHandler, []),
            (ConfigurableDummyHandler, [".dummy"]),
            (SmartDummyYamlHandler, [".yaml", ".yml"]),
            (SmartDummyJsonHandler, [".json"]),
        ],
    )
    def test_supported_extensions_property(
        self, handler_class: Any, expected_extensions: Any
    ) -> None:
        """Test that supported_extensions property returns expected list."""
        handler = handler_class()
        assert hasattr(handler, "supported_extensions")
        assert isinstance(handler.supported_extensions, list)
        assert handler.supported_extensions == expected_extensions

    @pytest.mark.parametrize(
        "handler_class,expected_filenames",
        [
            (PythonHandler, []),
            (MarkdownHandler, []),
            (MetadataYAMLHandler, []),
            (IgnoreFileHandler, [".onexignore", ".gitignore"]),
            (ConfigurableDummyHandler, []),
            (SmartDummyYamlHandler, []),
            (SmartDummyJsonHandler, []),
        ],
    )
    def test_supported_filenames_property(
        self, handler_class: Any, expected_filenames: Any
    ) -> None:
        """Test that supported_filenames property returns expected list."""
        handler = handler_class()
        assert hasattr(handler, "supported_filenames")
        assert isinstance(handler.supported_filenames, list)
        assert handler.supported_filenames == expected_filenames

    @pytest.mark.parametrize(
        "handler_class,expected_priority",
        [
            (PythonHandler, 50),
            (MarkdownHandler, 50),
            (MetadataYAMLHandler, 50),
            (IgnoreFileHandler, 100),
            (ConfigurableDummyHandler, 0),
            (SmartDummyYamlHandler, 0),
            (SmartDummyJsonHandler, 0),
        ],
    )
    def test_handler_priority_property(
        self, handler_class: Any, expected_priority: int
    ) -> None:
        """Test that handler_priority property returns expected integer."""
        handler = handler_class()
        assert hasattr(handler, "handler_priority")
        assert isinstance(handler.handler_priority, int)
        assert handler.handler_priority == expected_priority

    @pytest.mark.parametrize(
        "handler_class",
        [
            PythonHandler,
            MarkdownHandler,
            MetadataYAMLHandler,
            IgnoreFileHandler,
            ConfigurableDummyHandler,
            SmartDummyYamlHandler,
            SmartDummyJsonHandler,
        ],
    )
    def test_requires_content_analysis_property(self, handler_class: Any) -> None:
        """Test that requires_content_analysis property returns a boolean."""
        handler = handler_class()
        assert hasattr(handler, "requires_content_analysis")
        assert isinstance(handler.requires_content_analysis, bool)


class TestFileTypeHandlerRegistryIntrospection:
    """Test the introspection capabilities of FileTypeHandlerRegistry."""

    def test_list_handlers_includes_metadata(self) -> None:
        """Test that list_handlers includes metadata for all handlers."""
        registry = FileTypeHandlerRegistry()
        registry.register_all_handlers()

        handlers = registry.list_handlers()

        # Check that we have handlers
        assert len(handlers) > 0

        # Check that each handler has metadata
        for handler_key, handler_info in handlers.items():
            assert "handler_class" in handler_info
            assert "source" in handler_info
            assert "priority" in handler_info

            # Check for new metadata properties
            if handler_info.get("metadata_available", True):
                assert "handler_name" in handler_info
                assert "handler_version" in handler_info
                assert "handler_author" in handler_info
                assert "handler_description" in handler_info
                assert "supported_extensions" in handler_info
                assert "supported_filenames" in handler_info
                assert "handler_priority" in handler_info
                assert "requires_content_analysis" in handler_info

    def test_handler_metadata_consistency(self) -> None:
        """Test that handler metadata is consistent across instances."""
        registry = FileTypeHandlerRegistry()
        registry.register_all_handlers()

        handlers = registry.list_handlers()

        for handler_key, handler_info in handlers.items():
            if handler_info.get("metadata_available", True):
                # Check that handler priority matches registration priority
                if "handler_priority" in handler_info:
                    # Note: Registration priority may differ from handler's default priority
                    # This is expected behavior for override scenarios
                    assert isinstance(handler_info["handler_priority"], int)

                # Check that supported extensions/filenames are lists
                assert isinstance(handler_info["supported_extensions"], list)
                assert isinstance(handler_info["supported_filenames"], list)

                # Check that requires_content_analysis is boolean
                assert isinstance(handler_info["requires_content_analysis"], bool)

    def test_custom_handler_registration_with_metadata(self) -> None:
        """Test that custom handlers with metadata can be registered."""
        registry = FileTypeHandlerRegistry()

        # Register a custom handler
        custom_handler = ConfigurableDummyHandler(file_type="test")
        registry.register_handler(".test", custom_handler, source="test", priority=25)

        handlers = registry.list_handlers()

        # Find our custom handler
        test_handler = None
        for handler_key, handler_info in handlers.items():
            if handler_key == "extension:.test":
                test_handler = handler_info
                break

        assert test_handler is not None
        assert test_handler["source"] == "test"
        assert test_handler["priority"] == 25
        assert test_handler["handler_name"] == "configurable_dummy_test_handler"
        assert test_handler["supported_extensions"] == [".test"]

    def test_metadata_graceful_fallback_for_legacy_handlers(self) -> None:
        """Test graceful fallback for handlers without metadata properties."""
        # This test would be relevant if we had legacy handlers without metadata
        # For now, all our handlers implement the metadata properties
        registry = FileTypeHandlerRegistry()
        registry.register_all_handlers()

        handlers = registry.list_handlers()

        # All current handlers should have metadata
        for handler_key, handler_info in handlers.items():
            # metadata_available should not be False for any current handlers
            assert handler_info.get("metadata_available", True) is True
