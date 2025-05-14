from typing import Dict, TypeVar, Generic, Optional

T = TypeVar('T')

class PluginRegistryMixin(Generic[T]):
    """
    Generic mixin for plugin registries. Implements all standard registry operations.
    """
    def __init__(self):
        self._plugins: Dict[str, T] = {}

    def register_plugin(self, name: str, plugin: T) -> None:
        """Register a plugin by name/type."""
        self._plugins[name] = plugin

    def get_plugin(self, name: str) -> Optional[T]:
        """Retrieve a plugin by name/type."""
        return self._plugins.get(name)

    def list_plugins(self) -> Dict[str, T]:
        """List all registered plugins."""
        return dict(self._plugins)

    def unregister_plugin(self, name: str) -> None:
        """Remove a plugin by name/type."""
        self._plugins.pop(name, None)

    def clear_plugins(self) -> None:
        """Remove all registered plugins."""
        self._plugins.clear()

    def has_plugin(self, name: str) -> bool:
        """Check if a plugin is registered under the given name/type."""
        return name in self._plugins 