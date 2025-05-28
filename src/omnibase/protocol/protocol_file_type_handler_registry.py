# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_file_type_handler_registry.py
# version: 1.0.0
# uuid: 29b1bc28-1ec3-42a5-9b20-cb29de348a5a
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.180074
# last_modified_at: 2025-05-28T17:20:05.195192
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 2f69123337ee4b244a77d0fa1a21864d580d29ae1ffc8af2162aec6bc336e2ef
# entrypoint: python@protocol_file_type_handler_registry.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_file_type_handler_registry
# meta_type: tool
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Any, Optional, Protocol, Set, Type, Union

from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler


class ProtocolFileTypeHandlerRegistry(Protocol):
    """
    Canonical protocol for file type handler registries shared across nodes.
    Placed in runtime/ per OmniNode Runtime Structure Guidelines: use runtime/ for execution-layer components reused by multiple nodes.
    All handler registration, lookup, and extension management must conform to this interface.

    Enhanced with plugin/override API for node-local handler extensions.
    """

    def register(self, extension: str, handler: ProtocolFileTypeHandler) -> None:
        """Register a handler for a file extension (e.g., '.py', '.yaml')."""
        ...

    def register_special(self, filename: str, handler: ProtocolFileTypeHandler) -> None:
        """Register a handler for a canonical filename or role (e.g., 'node.onex.yaml')."""
        ...

    def register_handler(
        self,
        extension_or_name: str,
        handler: Union[ProtocolFileTypeHandler, Type[ProtocolFileTypeHandler]],
        source: str = "unknown",
        priority: int = 0,
        override: bool = False,
        **handler_kwargs: Any,
    ) -> None:
        """
        Enhanced handler registration API supporting both extension-based and named registration.

        Args:
            extension_or_name: File extension (e.g., '.py') or handler name (e.g., 'custom_yaml')
            handler: Handler instance or handler class
            source: Source of registration ("core", "runtime", "node-local", "plugin")
            priority: Priority for conflict resolution (higher wins)
            override: Whether to override existing handlers
            **handler_kwargs: Arguments to pass to handler constructor if handler is a class
        """
        ...

    def get_handler(self, path: Path) -> Optional[ProtocolFileTypeHandler]:
        """Return the handler for the given path, or None if unhandled."""
        ...

    def get_named_handler(self, name: str) -> Optional[ProtocolFileTypeHandler]:
        """Get a handler by name."""
        ...

    def list_handlers(self) -> dict[str, dict[str, Any]]:
        """List all registered handlers with metadata."""
        ...

    def handled_extensions(self) -> Set[str]:
        """Return the set of handled file extensions."""
        ...

    def handled_specials(self) -> Set[str]:
        """Return the set of handled special filenames."""
        ...

    def handled_names(self) -> Set[str]:
        """Return the set of handled named handlers."""
        ...

    def register_all_handlers(self) -> None:
        """Register all canonical handlers for this registry."""
        ...

    def register_node_local_handlers(self, handlers: dict[str, Any]) -> None:
        """
        Convenience method for nodes to register their local handlers.

        Args:
            handlers: Dict mapping extensions/names to handler classes or instances
        """
        ...
