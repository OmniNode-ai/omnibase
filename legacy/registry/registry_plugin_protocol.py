from typing import Protocol, TypeVar, Generic, Dict, Optional

T = TypeVar('T')

class ProtocolPluginRegistry(Protocol, Generic[T]):
    """
    Generic protocol for plugin registries. Enforces type safety and standard registry operations.
    """
    def register_plugin(self, name: str, plugin: T) -> None:
        """Register a plugin by name/type."""
        ...

    def get_plugin(self, name: str) -> Optional[T]:
        """Retrieve a plugin by name/type."""
        ...

    def list_plugins(self) -> Dict[str, T]:
        """List all registered plugins."""
        ...

    def unregister_plugin(self, name: str) -> None:
        """Remove a plugin by name/type."""
        ...

    def clear_plugins(self) -> None:
        """Remove all registered plugins."""
        ...

    def has_plugin(self, name: str) -> bool:
        """Check if a plugin is registered under the given name/type."""
        ... 