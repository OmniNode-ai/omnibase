# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: core_plugin_loader.py
# version: 1.0.0
# uuid: 1f68801f-230b-4390-b8de-92398d668021
# author: OmniNode Team
# created_at: 2025-05-26T10:53:14.834417
# last_modified_at: 2025-05-26T16:53:38.726957
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 9509479043e67b1a2f29927c040f2c030d6af2587cd0c3b14b3317ad9aa35f76
# entrypoint: python@core_plugin_loader.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.core_plugin_loader
# meta_type: tool
# === /OmniNode:Metadata ===


"""
General plugin discovery and loading system for ONEX.

This module provides a unified plugin discovery system that can load plugins
via entry points, configuration files, and environment variables. It supports
different plugin types (handlers, validators, tools, fixtures) and integrates
with the existing ONEX infrastructure.
"""

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Set

try:
    from importlib.metadata import entry_points
except ImportError:
    from importlib_metadata import entry_points  # type: ignore

import yaml

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class PluginType(Enum):
    """Supported plugin types in the ONEX system."""

    HANDLER = "handler"
    VALIDATOR = "validator"
    TOOL = "tool"
    FIXTURE = "fixture"
    NODE = "node"


class PluginSource(Enum):
    """Sources for plugin discovery."""

    ENTRY_POINT = "entry_point"
    CONFIG_FILE = "config_file"
    ENVIRONMENT = "environment"
    MANUAL = "manual"


@dataclass
class PluginMetadata:
    """Metadata for a discovered plugin."""

    name: str
    plugin_type: PluginType
    source: PluginSource
    module_path: str
    class_name: str
    priority: int = 0
    description: str = ""
    version: str = "unknown"
    entry_point_group: Optional[str] = None
    config_path: Optional[str] = None
    env_var: Optional[str] = None


class PluginProtocol(Protocol):
    """Protocol that all plugins must implement."""

    def bootstrap(self, registry: Any) -> None:
        """Bootstrap the plugin with the given registry."""
        ...


class PluginValidationError(OnexError):
    """Error raised when plugin validation fails."""

    def __init__(self, message: str, plugin_name: str = "unknown"):
        super().__init__(message, CoreErrorCode.VALIDATION_FAILED)
        self.plugin_name = plugin_name


class PluginRegistry:
    """Registry for managing discovered plugins."""

    def __init__(self) -> None:
        self._plugins: Dict[str, PluginMetadata] = {}
        self._loaded_plugins: Dict[str, Any] = {}

    def register_plugin(self, metadata: PluginMetadata) -> None:
        """Register a plugin with the registry."""
        plugin_key = f"{metadata.plugin_type.value}:{metadata.name}"

        # Check for conflicts
        if plugin_key in self._plugins:
            existing = self._plugins[plugin_key]
            if existing.priority >= metadata.priority:
                emit_log_event(
                    LogLevelEnum.WARNING,
                    f"Plugin {plugin_key} already registered with higher/equal priority "
                    f"({existing.priority} >= {metadata.priority}). Skipping.",
                    node_id=_COMPONENT_NAME,
                )
                return
            else:
                emit_log_event(
                    LogLevelEnum.INFO,
                    f"Replacing plugin {plugin_key} with higher priority "
                    f"({metadata.priority} > {existing.priority})",
                    node_id=_COMPONENT_NAME,
                )

        self._plugins[plugin_key] = metadata
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"Registered plugin: {plugin_key} from {metadata.source.value}",
            node_id=_COMPONENT_NAME,
        )

    def get_plugin(
        self, plugin_type: PluginType, name: str
    ) -> Optional[PluginMetadata]:
        """Get plugin metadata by type and name."""
        plugin_key = f"{plugin_type.value}:{name}"
        return self._plugins.get(plugin_key)

    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginMetadata]:
        """Get all plugins of a specific type."""
        return [
            plugin
            for plugin in self._plugins.values()
            if plugin.plugin_type == plugin_type
        ]

    def list_plugins(self) -> Dict[str, PluginMetadata]:
        """List all registered plugins."""
        return self._plugins.copy()

    def load_plugin(self, plugin_type: PluginType, name: str) -> Optional[Any]:
        """Load and instantiate a plugin."""
        plugin_key = f"{plugin_type.value}:{name}"

        # Return cached instance if already loaded
        if plugin_key in self._loaded_plugins:
            return self._loaded_plugins[plugin_key]

        metadata = self.get_plugin(plugin_type, name)
        if not metadata:
            return None

        try:
            # Import the plugin module and class
            module = __import__(metadata.module_path, fromlist=[metadata.class_name])
            plugin_class = getattr(module, metadata.class_name)

            # Instantiate the plugin
            plugin_instance = plugin_class()

            # Validate plugin protocol
            if not hasattr(plugin_instance, "bootstrap"):
                raise PluginValidationError(
                    f"Plugin {name} does not implement bootstrap() method",
                    plugin_name=name,
                )

            # Cache the loaded plugin
            self._loaded_plugins[plugin_key] = plugin_instance

            emit_log_event(
                LogLevelEnum.INFO,
                f"Loaded plugin: {plugin_key}",
                node_id=_COMPONENT_NAME,
            )
            return plugin_instance

        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Failed to load plugin {plugin_key}: {e}",
                node_id=_COMPONENT_NAME,
            )
            raise PluginValidationError(
                f"Failed to load plugin {name}: {e}", plugin_name=name
            )


class PluginLoader:
    """Main plugin discovery and loading system."""

    # Entry point groups for different plugin types
    ENTRY_POINT_GROUPS = {
        PluginType.HANDLER: "omnibase.handlers",
        PluginType.VALIDATOR: "omnibase.validators",
        PluginType.TOOL: "omnibase.tools",
        PluginType.FIXTURE: "omnibase.fixtures",
        PluginType.NODE: "omnibase.nodes",
    }

    # Environment variable prefixes for different plugin types
    ENV_PREFIXES = {
        PluginType.HANDLER: "ONEX_PLUGIN_HANDLER_",
        PluginType.VALIDATOR: "ONEX_PLUGIN_VALIDATOR_",
        PluginType.TOOL: "ONEX_PLUGIN_TOOL_",
        PluginType.FIXTURE: "ONEX_PLUGIN_FIXTURE_",
        PluginType.NODE: "ONEX_PLUGIN_NODE_",
    }

    def __init__(self) -> None:
        self.registry = PluginRegistry()
        self._discovered_sources: Set[str] = set()

    def discover_all_plugins(self) -> None:
        """Discover plugins from all sources."""
        emit_log_event(
            LogLevelEnum.INFO,
            "Starting plugin discovery from all sources",
            node_id=_COMPONENT_NAME,
        )

        # Discover from entry points
        self.discover_entry_point_plugins()

        # Discover from configuration files
        self.discover_config_file_plugins()

        # Discover from environment variables
        self.discover_environment_plugins()

        emit_log_event(
            LogLevelEnum.INFO,
            f"Plugin discovery complete. Found {len(self.registry.list_plugins())} plugins.",
            node_id=_COMPONENT_NAME,
        )

    def discover_entry_point_plugins(self) -> None:
        """Discover plugins from entry points."""
        emit_log_event(
            LogLevelEnum.DEBUG,
            "Discovering plugins from entry points",
            node_id=_COMPONENT_NAME,
        )

        try:
            eps = entry_points()

            for plugin_type, group_name in self.ENTRY_POINT_GROUPS.items():
                try:
                    # Handle both new and old importlib.metadata APIs
                    if hasattr(eps, "select"):
                        # New API (Python 3.10+)
                        plugin_eps = eps.select(group=group_name)
                    else:
                        # Old API (Python < 3.10)
                        plugin_eps = eps.get(group_name, [])  # type: ignore

                    for ep in plugin_eps:
                        try:
                            # Parse module:class format
                            module_path, class_name = ep.value.split(":", 1)

                            metadata = PluginMetadata(
                                name=ep.name,
                                plugin_type=plugin_type,
                                source=PluginSource.ENTRY_POINT,
                                module_path=module_path,
                                class_name=class_name,
                                priority=0,  # Default priority for entry points
                                entry_point_group=group_name,
                            )

                            self.registry.register_plugin(metadata)
                            self._discovered_sources.add(
                                f"entry_point:{group_name}:{ep.name}"
                            )

                        except Exception as e:
                            emit_log_event(
                                LogLevelEnum.ERROR,
                                f"Failed to process entry point {ep.name} from {group_name}: {e}",
                                node_id=_COMPONENT_NAME,
                            )

                except Exception as e:
                    emit_log_event(
                        LogLevelEnum.ERROR,
                        f"Failed to discover plugins from group {group_name}: {e}",
                        node_id=_COMPONENT_NAME,
                    )

        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Failed to discover entry point plugins: {e}",
                node_id=_COMPONENT_NAME,
            )

    def discover_config_file_plugins(self, config_path: Optional[str] = None) -> None:
        """Discover plugins from configuration files."""
        emit_log_event(
            LogLevelEnum.DEBUG,
            "Discovering plugins from configuration files",
            node_id=_COMPONENT_NAME,
        )

        # Default configuration file locations
        default_paths = [
            "plugin_registry.yaml",
            "~/.onex/plugin_registry.yaml",
            "/etc/onex/plugin_registry.yaml",
        ]

        if config_path:
            config_paths = [config_path]
        else:
            config_paths = [os.path.expanduser(p) for p in default_paths]

        for path in config_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        config = yaml.safe_load(f)

                    if not config:
                        continue

                    # Process each plugin type
                    for plugin_type in PluginType:
                        type_key = (
                            f"{plugin_type.value}s"  # handlers, validators, tools, etc.
                        )
                        plugins_config = config.get(type_key, {})

                        for name, plugin_config in plugins_config.items():
                            try:
                                metadata = PluginMetadata(
                                    name=name,
                                    plugin_type=plugin_type,
                                    source=PluginSource.CONFIG_FILE,
                                    module_path=plugin_config["module"],
                                    class_name=plugin_config["class"],
                                    priority=plugin_config.get(
                                        "priority", 5
                                    ),  # Higher than entry points
                                    description=plugin_config.get("description", ""),
                                    version=plugin_config.get("version", "unknown"),
                                    config_path=path,
                                )

                                self.registry.register_plugin(metadata)
                                self._discovered_sources.add(
                                    f"config_file:{path}:{name}"
                                )

                            except KeyError as e:
                                emit_log_event(
                                    LogLevelEnum.ERROR,
                                    f"Invalid plugin config for {name} in {path}: missing {e}",
                                    node_id=_COMPONENT_NAME,
                                )
                            except Exception as e:
                                emit_log_event(
                                    LogLevelEnum.ERROR,
                                    f"Failed to process plugin {name} from {path}: {e}",
                                    node_id=_COMPONENT_NAME,
                                )

                    break  # Use first found config file

                except Exception as e:
                    emit_log_event(
                        LogLevelEnum.ERROR,
                        f"Failed to load plugin config from {path}: {e}",
                        node_id=_COMPONENT_NAME,
                    )

    def discover_environment_plugins(self) -> None:
        """Discover plugins from environment variables."""
        emit_log_event(
            LogLevelEnum.DEBUG,
            "Discovering plugins from environment variables",
            node_id=_COMPONENT_NAME,
        )

        for plugin_type, prefix in self.ENV_PREFIXES.items():
            for env_var, value in os.environ.items():
                if env_var.startswith(prefix):
                    plugin_name = env_var[len(prefix) :].lower()

                    try:
                        # Parse module:class format
                        if ":" not in value:
                            emit_log_event(
                                LogLevelEnum.ERROR,
                                f"Invalid plugin specification in {env_var}: {value}. "
                                f"Expected format: module.path:ClassName",
                                node_id=_COMPONENT_NAME,
                            )
                            continue

                        module_path, class_name = value.split(":", 1)

                        metadata = PluginMetadata(
                            name=plugin_name,
                            plugin_type=plugin_type,
                            source=PluginSource.ENVIRONMENT,
                            module_path=module_path,
                            class_name=class_name,
                            priority=10,  # Higher than config files
                            env_var=env_var,
                        )

                        self.registry.register_plugin(metadata)
                        self._discovered_sources.add(f"environment:{env_var}")

                    except Exception as e:
                        emit_log_event(
                            LogLevelEnum.ERROR,
                            f"Failed to process environment plugin {env_var}: {e}",
                            node_id=_COMPONENT_NAME,
                        )

    def load_plugin(self, plugin_type: PluginType, name: str) -> Optional[Any]:
        """Load a specific plugin."""
        return self.registry.load_plugin(plugin_type, name)

    def load_plugins_by_type(self, plugin_type: PluginType) -> Dict[str, Any]:
        """Load all plugins of a specific type."""
        plugins = {}
        for metadata in self.registry.get_plugins_by_type(plugin_type):
            try:
                plugin_instance = self.registry.load_plugin(plugin_type, metadata.name)
                if plugin_instance:
                    plugins[metadata.name] = plugin_instance
            except Exception as e:
                emit_log_event(
                    LogLevelEnum.ERROR,
                    f"Failed to load plugin {metadata.name}: {e}",
                    node_id=_COMPONENT_NAME,
                )

        return plugins

    def bootstrap_plugins(self, plugin_type: PluginType, registry: Any) -> None:
        """Bootstrap all plugins of a specific type with the given registry."""
        plugins = self.load_plugins_by_type(plugin_type)

        for name, plugin_instance in plugins.items():
            try:
                plugin_instance.bootstrap(registry)
                emit_log_event(
                    LogLevelEnum.INFO,
                    f"Bootstrapped {plugin_type.value} plugin: {name}",
                    node_id=_COMPONENT_NAME,
                )
            except Exception as e:
                emit_log_event(
                    LogLevelEnum.ERROR,
                    f"Failed to bootstrap plugin {name}: {e}",
                    node_id=_COMPONENT_NAME,
                )

    def get_discovery_report(self) -> Dict[str, Any]:
        """Get a report of plugin discovery results."""
        plugins = self.registry.list_plugins()

        report = {
            "total_plugins": len(plugins),
            "plugins_by_type": {},
            "plugins_by_source": {},
            "discovered_sources": list(self._discovered_sources),
            "plugins": {},
        }

        # Group by type
        for plugin_type in PluginType:
            type_plugins = [p for p in plugins.values() if p.plugin_type == plugin_type]
            report["plugins_by_type"][plugin_type.value] = len(type_plugins)  # type: ignore

        # Group by source
        for source in PluginSource:
            source_plugins = [p for p in plugins.values() if p.source == source]
            report["plugins_by_source"][source.value] = len(source_plugins)  # type: ignore

        # Plugin details
        for key, metadata in plugins.items():
            report["plugins"][key] = {  # type: ignore
                "name": metadata.name,
                "type": metadata.plugin_type.value,
                "source": metadata.source.value,
                "module": metadata.module_path,
                "class": metadata.class_name,
                "priority": metadata.priority,
                "description": metadata.description,
                "version": metadata.version,
            }

        return report


# Global plugin loader instance
_plugin_loader: Optional[PluginLoader] = None


def get_plugin_loader() -> PluginLoader:
    """Get the global plugin loader instance."""
    global _plugin_loader
    if _plugin_loader is None:
        _plugin_loader = PluginLoader()
    return _plugin_loader


def discover_plugins() -> None:
    """Discover all plugins using the global plugin loader."""
    loader = get_plugin_loader()
    loader.discover_all_plugins()


def load_plugin(plugin_type: PluginType, name: str) -> Optional[Any]:
    """Load a specific plugin using the global plugin loader."""
    loader = get_plugin_loader()
    return loader.load_plugin(plugin_type, name)


def bootstrap_plugins(plugin_type: PluginType, registry: Any) -> None:
    """Bootstrap all plugins of a specific type using the global plugin loader."""
    loader = get_plugin_loader()
    loader.bootstrap_plugins(plugin_type, registry)
