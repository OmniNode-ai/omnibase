from typing import Dict, Type, Optional, Any
from foundation.protocol.protocol_scaffold_plugin import ProtocolScaffoldPlugin
from foundation.registry.registry_plugin_protocol import ProtocolPluginRegistry
from foundation.registry.registry_plugin_mixin import PluginRegistryMixin

class ScaffoldPluginRegistry(PluginRegistryMixin[ProtocolScaffoldPlugin], ProtocolPluginRegistry[ProtocolScaffoldPlugin]):
    """
    Registry for scaffold generator plugins (DI-compliant).
    Implements ProtocolPluginRegistry and PluginRegistryMixin for type safety and maintainability.
    """
    def __init__(self, logger: Any = None, config: Optional[dict] = None) -> None:
        """
        Initialize the registry with DI-compliant dependencies.
        Args:
            logger: Logger instance (optional, DI-injected)
            config: Optional configuration dictionary
        """
        super().__init__()
        self.logger = logger
        self.config = config or {}
        self._plugins: Dict[str, Type[ProtocolScaffoldPlugin]] = {}

    def register_plugin(self, name: str, plugin: ProtocolScaffoldPlugin) -> None:
        """
        Register a scaffold plugin class by name.
        Args:
            name: Unique name/type for the plugin (e.g., 'container', 'service')
            plugin: The plugin class implementing ProtocolScaffoldPlugin
        """
        super().register_plugin(name, plugin)
        if self.logger:
            self.logger.info(f"Registered scaffold plugin: {name}")

    def get_plugin(self, name: str) -> Optional[Type[ProtocolScaffoldPlugin]]:
        """
        Retrieve a registered plugin class by name.
        Args:
            name: Name/type of the plugin
        Returns:
            The plugin class, or None if not found
        """
        return self._plugins.get(name)

    def list_plugins(self) -> Dict[str, Type[ProtocolScaffoldPlugin]]:
        """
        List all registered scaffold plugins.
        Returns:
            Dictionary of plugin names to classes
        """
        return dict(self._plugins) 