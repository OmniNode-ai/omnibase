from pathlib import Path
from typing import Optional, Protocol, Set

from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler


class ProtocolFileTypeHandlerRegistry(Protocol):
    """
    Canonical protocol for file type handler registries shared across nodes.
    Placed in runtime/ per OmniNode Runtime Structure Guidelines: use runtime/ for execution-layer components reused by multiple nodes.
    All handler registration, lookup, and extension management must conform to this interface.
    """

    def register(self, extension: str, handler: ProtocolFileTypeHandler) -> None:
        """Register a handler for a file extension (e.g., '.py', '.yaml')."""
        ...

    def register_special(self, filename: str, handler: ProtocolFileTypeHandler) -> None:
        """Register a handler for a canonical filename or role (e.g., 'node.onex.yaml')."""
        ...

    def get_handler(self, path: Path) -> Optional[ProtocolFileTypeHandler]:
        """Return the handler for the given path, or None if unhandled."""
        ...

    def handled_extensions(self) -> Set[str]:
        """Return the set of handled file extensions."""
        ...

    def handled_specials(self) -> Set[str]:
        """Return the set of handled special filenames."""
        ...

    def register_all_handlers(self) -> None:
        """Register all canonical handlers for this registry."""
        ...
