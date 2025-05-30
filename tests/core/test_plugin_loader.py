# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.869593'
# description: Stamped by PythonHandler
# entrypoint: python://test_plugin_loader.py
# hash: cfd3755bcdbfdc2c65b9bda105a705e626fc42376fa7640a5dfcd34d5a777aeb
# last_modified_at: '2025-05-29T13:51:23.046840+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_plugin_loader.py
# namespace: py://omnibase.tests.core.test_plugin_loader_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 1136a150-c5d1-48de-acf7-b8173a775a33
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Tests for the general plugin discovery and loading system.

This module tests the PluginLoader, PluginRegistry, and related components
following canonical testing standards with registry-driven test cases.
"""

import os
import tempfile
from enum import Enum
from typing import Any, Dict, Generator, List
from unittest.mock import Mock, patch

import pytest
import yaml

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_plugin_loader import (
    PluginLoader,
    PluginMetadata,
    PluginRegistry,
    PluginSource,
    PluginType,
    PluginValidationError,
    bootstrap_plugins,
    discover_plugins,
    get_plugin_loader,
    load_plugin,
)


class PluginTestContext(Enum):
    """Test execution contexts."""

    MOCK = "mock"
    INTEGRATION = "integration"


class PluginTestCase(Enum):
    """Plugin test case types."""

    VALID_HANDLER = "valid_handler"
    VALID_VALIDATOR = "valid_validator"
    VALID_TOOL = "valid_tool"
    INVALID_NO_BOOTSTRAP = "invalid_no_bootstrap"
    INVALID_IMPORT_ERROR = "invalid_import_error"
    CONFLICTING_PLUGINS = "conflicting_plugins"


# Mock plugin classes for testing
class MockValidPlugin:
    """Mock plugin that implements the required protocol."""

    def __init__(self) -> None:
        self.name = "MockValidPlugin"
        self.bootstrapped = False

    def bootstrap(self, registry: Any) -> None:
        """Bootstrap the plugin."""
        self.bootstrapped = True


class MockInvalidPlugin:
    """Mock plugin that does not implement the required protocol."""

    def __init__(self) -> None:
        self.name = "MockInvalidPlugin"


class MockFailingPlugin:
    """Mock plugin that fails during instantiation."""

    def __init__(self) -> None:
        raise OnexError("Plugin instantiation failed", CoreErrorCode.OPERATION_FAILED)


@pytest.fixture
def plugin_registry(protocol_event_bus) -> PluginRegistry:
    """Fixture providing a clean plugin registry."""
    return PluginRegistry(event_bus=protocol_event_bus)


@pytest.fixture
def plugin_loader(protocol_event_bus) -> PluginLoader:
    """Fixture providing a clean plugin loader."""
    return PluginLoader(event_bus=protocol_event_bus)


@pytest.fixture
def mock_entry_points() -> List[Mock]:
    """Fixture providing mock entry points."""
    mock_ep = Mock()
    mock_ep.name = "test_plugin"
    mock_ep.value = "test.module:MockValidPlugin"
    mock_ep.load.return_value = MockValidPlugin
    return [mock_ep]


@pytest.fixture
def plugin_config_file() -> Generator[str, None, None]:
    """Fixture providing a temporary plugin configuration file."""
    config_data = {
        "handlers": {
            "test_handler": {
                "module": "test.module",
                "class": "MockValidPlugin",
                "priority": 5,
                "description": "Test handler plugin",
                "version": "1.0.0",
            }
        },
        "validators": {
            "test_validator": {
                "module": "test.module",
                "class": "MockValidPlugin",
                "priority": 6,
                "description": "Test validator plugin",
            }
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        config_path = f.name

    yield config_path

    # Cleanup
    os.unlink(config_path)


@pytest.fixture
def plugin_env_vars() -> Dict[str, str]:
    """Fixture providing plugin environment variables."""
    env_vars = {
        "ONEX_PLUGIN_HANDLER_TEST": "test.module:MockValidPlugin",
        "ONEX_PLUGIN_VALIDATOR_SECURITY": "test.security:SecurityValidator",
        "ONEX_PLUGIN_TOOL_GENERATOR": "test.tools:CodeGenerator",
    }
    return env_vars


class TestPluginMetadata:
    """Test plugin metadata handling."""

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_plugin_metadata_creation(self, context: PluginTestContext) -> None:
        """Test plugin metadata creation with all fields."""
        metadata = PluginMetadata(
            name="test_plugin",
            plugin_type=PluginType.HANDLER,
            source=PluginSource.ENTRY_POINT,
            module_path="test.module",
            class_name="TestHandler",
            priority=5,
            description="Test plugin",
            version="1.0.0",
            entry_point_group="omnibase.handlers",
        )

        assert metadata.name == "test_plugin"
        assert metadata.plugin_type == PluginType.HANDLER
        assert metadata.source == PluginSource.ENTRY_POINT
        assert metadata.module_path == "test.module"
        assert metadata.class_name == "TestHandler"
        assert metadata.priority == 5
        assert metadata.description == "Test plugin"
        assert metadata.version == "1.0.0"
        assert metadata.entry_point_group == "omnibase.handlers"

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_plugin_metadata_defaults(self, context: PluginTestContext) -> None:
        """Test plugin metadata with default values."""
        metadata = PluginMetadata(
            name="minimal_plugin",
            plugin_type=PluginType.TOOL,
            source=PluginSource.CONFIG_FILE,
            module_path="minimal.module",
            class_name="MinimalTool",
        )

        assert metadata.priority == 0
        assert metadata.description == ""
        assert metadata.version == "unknown"
        assert metadata.entry_point_group is None
        assert metadata.config_path is None
        assert metadata.env_var is None


class TestPluginRegistry:
    """Test plugin registry functionality."""

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_register_plugin_success(
        self, plugin_registry: PluginRegistry, context: PluginTestContext, protocol_event_bus
    ) -> None:
        """Test successful plugin registration."""
        metadata = PluginMetadata(
            name="test_plugin",
            plugin_type=PluginType.HANDLER,
            source=PluginSource.ENTRY_POINT,
            module_path="test.module",
            class_name="TestHandler",
        )

        plugin_registry.register_plugin(metadata)

        retrieved = plugin_registry.get_plugin(PluginType.HANDLER, "test_plugin")
        assert retrieved is not None
        assert retrieved.name == "test_plugin"
        assert retrieved.plugin_type == PluginType.HANDLER

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_register_plugin_conflict_lower_priority(
        self, plugin_registry: PluginRegistry, context: PluginTestContext, protocol_event_bus
    ) -> None:
        """Test plugin registration conflict with lower priority."""
        # Register first plugin with higher priority
        high_priority = PluginMetadata(
            name="conflict_plugin",
            plugin_type=PluginType.HANDLER,
            source=PluginSource.CONFIG_FILE,
            module_path="high.module",
            class_name="HighPriorityHandler",
            priority=10,
        )
        plugin_registry.register_plugin(high_priority)

        # Try to register second plugin with lower priority
        low_priority = PluginMetadata(
            name="conflict_plugin",
            plugin_type=PluginType.HANDLER,
            source=PluginSource.ENTRY_POINT,
            module_path="low.module",
            class_name="LowPriorityHandler",
            priority=5,
        )
        plugin_registry.register_plugin(low_priority)

        # High priority plugin should remain
        retrieved = plugin_registry.get_plugin(PluginType.HANDLER, "conflict_plugin")
        assert retrieved is not None
        assert retrieved.module_path == "high.module"
        assert retrieved.priority == 10

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_register_plugin_conflict_higher_priority(
        self, plugin_registry: PluginRegistry, context: PluginTestContext, protocol_event_bus
    ) -> None:
        """Test plugin registration conflict with higher priority."""
        # Register first plugin with lower priority
        low_priority = PluginMetadata(
            name="conflict_plugin",
            plugin_type=PluginType.VALIDATOR,
            source=PluginSource.ENTRY_POINT,
            module_path="low.module",
            class_name="LowPriorityValidator",
            priority=5,
        )
        plugin_registry.register_plugin(low_priority)

        # Register second plugin with higher priority
        high_priority = PluginMetadata(
            name="conflict_plugin",
            plugin_type=PluginType.VALIDATOR,
            source=PluginSource.ENVIRONMENT,
            module_path="high.module",
            class_name="HighPriorityValidator",
            priority=10,
        )
        plugin_registry.register_plugin(high_priority)

        # High priority plugin should replace low priority
        retrieved = plugin_registry.get_plugin(PluginType.VALIDATOR, "conflict_plugin")
        assert retrieved is not None
        assert retrieved.module_path == "high.module"
        assert retrieved.priority == 10

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_get_plugins_by_type(
        self, plugin_registry: PluginRegistry, context: PluginTestContext, protocol_event_bus
    ) -> None:
        """Test getting plugins by type."""
        # Register plugins of different types
        handler_metadata = PluginMetadata(
            name="handler_plugin",
            plugin_type=PluginType.HANDLER,
            source=PluginSource.ENTRY_POINT,
            module_path="handler.module",
            class_name="HandlerClass",
        )
        validator_metadata = PluginMetadata(
            name="validator_plugin",
            plugin_type=PluginType.VALIDATOR,
            source=PluginSource.CONFIG_FILE,
            module_path="validator.module",
            class_name="ValidatorClass",
        )
        tool_metadata = PluginMetadata(
            name="tool_plugin",
            plugin_type=PluginType.TOOL,
            source=PluginSource.ENVIRONMENT,
            module_path="tool.module",
            class_name="ToolClass",
        )

        plugin_registry.register_plugin(handler_metadata)
        plugin_registry.register_plugin(validator_metadata)
        plugin_registry.register_plugin(tool_metadata)

        # Test getting handlers
        handlers = plugin_registry.get_plugins_by_type(PluginType.HANDLER)
        assert len(handlers) == 1
        assert handlers[0].name == "handler_plugin"

        # Test getting validators
        validators = plugin_registry.get_plugins_by_type(PluginType.VALIDATOR)
        assert len(validators) == 1
        assert validators[0].name == "validator_plugin"

        # Test getting tools
        tools = plugin_registry.get_plugins_by_type(PluginType.TOOL)
        assert len(tools) == 1
        assert tools[0].name == "tool_plugin"

        # Test getting non-existent type
        fixtures = plugin_registry.get_plugins_by_type(PluginType.FIXTURE)
        assert len(fixtures) == 0

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_list_plugins(
        self, plugin_registry: PluginRegistry, context: PluginTestContext, protocol_event_bus
    ) -> None:
        """Test listing all plugins."""
        # Register multiple plugins
        metadata1 = PluginMetadata(
            name="plugin1",
            plugin_type=PluginType.HANDLER,
            source=PluginSource.ENTRY_POINT,
            module_path="module1",
            class_name="Class1",
        )
        metadata2 = PluginMetadata(
            name="plugin2",
            plugin_type=PluginType.VALIDATOR,
            source=PluginSource.CONFIG_FILE,
            module_path="module2",
            class_name="Class2",
        )

        plugin_registry.register_plugin(metadata1)
        plugin_registry.register_plugin(metadata2)

        plugins = plugin_registry.list_plugins()
        assert len(plugins) == 2
        assert "handler:plugin1" in plugins
        assert "validator:plugin2" in plugins


class TestPluginLoader:
    """Test plugin loader functionality."""

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_discover_entry_point_plugins(
        self,
        plugin_loader: PluginLoader,
        mock_entry_points: List[Mock],
        context: PluginTestContext,
        protocol_event_bus
    ) -> None:
        """Test discovery of entry point plugins."""
        with patch("omnibase.core.core_plugin_loader.entry_points") as mock_eps:
            # Mock new API (Python 3.10+)
            mock_eps.return_value.select.return_value = mock_entry_points

            plugin_loader.discover_entry_point_plugins()

            # Verify plugin was discovered and registered
            plugins = plugin_loader.registry.list_plugins()
            assert len(plugins) >= 1

            # Check that the mock plugin was registered
            handler_plugins = plugin_loader.registry.get_plugins_by_type(
                PluginType.HANDLER
            )
            plugin_names = [p.name for p in handler_plugins]
            assert "test_plugin" in plugin_names

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_discover_config_file_plugins(
        self,
        plugin_loader: PluginLoader,
        plugin_config_file: str,
        context: PluginTestContext,
        protocol_event_bus
    ) -> None:
        """Test discovery of configuration file plugins."""
        plugin_loader.discover_config_file_plugins(plugin_config_file)

        # Verify plugins were discovered
        plugins = plugin_loader.registry.list_plugins()
        assert len(plugins) >= 2

        # Check handler plugin
        handler = plugin_loader.registry.get_plugin(PluginType.HANDLER, "test_handler")
        assert handler is not None
        assert handler.module_path == "test.module"
        assert handler.class_name == "MockValidPlugin"
        assert handler.priority == 5
        assert handler.description == "Test handler plugin"
        assert handler.version == "1.0.0"

        # Check validator plugin
        validator = plugin_loader.registry.get_plugin(
            PluginType.VALIDATOR, "test_validator"
        )
        assert validator is not None
        assert validator.module_path == "test.module"
        assert validator.class_name == "MockValidPlugin"
        assert validator.priority == 6

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_discover_environment_plugins(
        self,
        plugin_loader: PluginLoader,
        plugin_env_vars: Dict[str, str],
        context: PluginTestContext,
        protocol_event_bus
    ) -> None:
        """Test discovery of environment variable plugins."""
        with patch.dict(os.environ, plugin_env_vars):
            plugin_loader.discover_environment_plugins()

            # Verify plugins were discovered
            plugins = plugin_loader.registry.list_plugins()
            assert len(plugins) >= 3

            # Check handler plugin
            handler = plugin_loader.registry.get_plugin(PluginType.HANDLER, "test")
            assert handler is not None
            assert handler.module_path == "test.module"
            assert handler.class_name == "MockValidPlugin"
            assert handler.source == PluginSource.ENVIRONMENT
            assert handler.priority == 10  # Environment plugins have higher priority

            # Check validator plugin
            validator = plugin_loader.registry.get_plugin(
                PluginType.VALIDATOR, "security"
            )
            assert validator is not None
            assert validator.module_path == "test.security"
            assert validator.class_name == "SecurityValidator"

            # Check tool plugin
            tool = plugin_loader.registry.get_plugin(PluginType.TOOL, "generator")
            assert tool is not None
            assert tool.module_path == "test.tools"
            assert tool.class_name == "CodeGenerator"

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_discover_all_plugins(
        self, plugin_loader: PluginLoader, context: PluginTestContext, protocol_event_bus
    ) -> None:
        """Test discovery from all sources."""
        with (
            patch.object(plugin_loader, "discover_entry_point_plugins") as mock_entry,
            patch.object(plugin_loader, "discover_config_file_plugins") as mock_config,
            patch.object(plugin_loader, "discover_environment_plugins") as mock_env,
        ):

            plugin_loader.discover_all_plugins()

            # Verify all discovery methods were called
            mock_entry.assert_called_once()
            mock_config.assert_called_once()
            mock_env.assert_called_once()

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_get_discovery_report(
        self, plugin_loader: PluginLoader, context: PluginTestContext, protocol_event_bus
    ) -> None:
        """Test plugin discovery report generation."""
        # Register some test plugins
        metadata1 = PluginMetadata(
            name="handler1",
            plugin_type=PluginType.HANDLER,
            source=PluginSource.ENTRY_POINT,
            module_path="module1",
            class_name="Handler1",
        )
        metadata2 = PluginMetadata(
            name="validator1",
            plugin_type=PluginType.VALIDATOR,
            source=PluginSource.CONFIG_FILE,
            module_path="module2",
            class_name="Validator1",
        )

        plugin_loader.registry.register_plugin(metadata1)
        plugin_loader.registry.register_plugin(metadata2)

        report = plugin_loader.get_discovery_report()

        # Verify report structure
        assert "total_plugins" in report
        assert "plugins_by_type" in report
        assert "plugins_by_source" in report
        assert "discovered_sources" in report
        assert "plugins" in report

        # Verify counts
        assert report["total_plugins"] == 2
        assert report["plugins_by_type"]["handler"] == 1
        assert report["plugins_by_type"]["validator"] == 1
        assert report["plugins_by_source"]["entry_point"] == 1
        assert report["plugins_by_source"]["config_file"] == 1

        # Verify plugin details
        assert "handler:handler1" in report["plugins"]
        assert "validator:validator1" in report["plugins"]


class TestPluginValidation:
    """Test plugin validation and error handling."""

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_plugin_validation_error(self, context: PluginTestContext) -> None:
        """Test plugin validation error creation."""
        error = PluginValidationError("Test error message", "test_plugin")

        # OnexError includes error code in string representation
        assert "Test error message" in str(error)
        assert "VALIDATION_FAILED" in str(error)
        assert error.plugin_name == "test_plugin"
        assert error.error_code == CoreErrorCode.VALIDATION_FAILED


class TestGlobalPluginLoader:
    """Test global plugin loader functions."""

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_get_plugin_loader_singleton(self, context: PluginTestContext) -> None:
        """Test that get_plugin_loader returns the same instance."""
        loader1 = get_plugin_loader()
        loader2 = get_plugin_loader()

        assert loader1 is loader2

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_discover_plugins_global(self, context: PluginTestContext) -> None:
        """Test global discover_plugins function."""
        with patch.object(PluginLoader, "discover_all_plugins") as mock_discover:
            discover_plugins()
            mock_discover.assert_called_once()

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_load_plugin_global(self, context: PluginTestContext) -> None:
        """Test global load_plugin function."""
        with patch.object(PluginLoader, "load_plugin") as mock_load:
            mock_load.return_value = MockValidPlugin()

            result = load_plugin(PluginType.HANDLER, "test_plugin")

            mock_load.assert_called_once_with(PluginType.HANDLER, "test_plugin")
            assert result is not None

    @pytest.mark.parametrize("context", [PluginTestContext.MOCK])
    def test_bootstrap_plugins_global(self, context: PluginTestContext) -> None:
        """Test global bootstrap_plugins function."""
        mock_registry = Mock()

        with patch.object(PluginLoader, "bootstrap_plugins") as mock_bootstrap:
            bootstrap_plugins(PluginType.HANDLER, mock_registry)
            mock_bootstrap.assert_called_once_with(PluginType.HANDLER, mock_registry)


class TestPluginIntegration:
    """Integration tests for plugin system."""

    @pytest.mark.parametrize("context", [PluginTestContext.INTEGRATION])
    def test_plugin_type_enum_completeness(self, context: PluginTestContext) -> None:
        """Test that all plugin types are properly defined."""
        expected_types = {"handler", "validator", "tool", "fixture", "node"}
        actual_types = {pt.value for pt in PluginType}

        assert actual_types == expected_types

    @pytest.mark.parametrize("context", [PluginTestContext.INTEGRATION])
    def test_plugin_source_enum_completeness(self, context: PluginTestContext) -> None:
        """Test that all plugin sources are properly defined."""
        expected_sources = {"entry_point", "config_file", "environment", "manual"}
        actual_sources = {ps.value for ps in PluginSource}

        assert actual_sources == expected_sources

    @pytest.mark.parametrize("context", [PluginTestContext.INTEGRATION])
    def test_entry_point_groups_mapping(self, context: PluginTestContext) -> None:
        """Test that entry point groups are properly mapped."""
        loader = PluginLoader()

        # Verify all plugin types have entry point groups
        for plugin_type in PluginType:
            assert plugin_type in loader.ENTRY_POINT_GROUPS
            group_name = loader.ENTRY_POINT_GROUPS[plugin_type]
            assert group_name.startswith("omnibase.")

    @pytest.mark.parametrize("context", [PluginTestContext.INTEGRATION])
    def test_environment_prefixes_mapping(self, context: PluginTestContext) -> None:
        """Test that environment variable prefixes are properly mapped."""
        loader = PluginLoader()

        # Verify all plugin types have environment prefixes
        for plugin_type in PluginType:
            assert plugin_type in loader.ENV_PREFIXES
            prefix = loader.ENV_PREFIXES[plugin_type]
            assert prefix.startswith("ONEX_PLUGIN_")
            assert prefix.endswith("_")
