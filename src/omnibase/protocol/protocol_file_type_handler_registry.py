# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_file_type_handler_registry.py
# version: 1.0.0
# uuid: f163d8e6-c285-4b3a-9b74-2572b8c89582
# author: OmniNode Team
# created_at: 2025-05-22T05:34:29.792365
# last_modified_at: 2025-05-22T20:50:39.713660
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a55d1c43305f000e34830cfd76126ef8b7f549ba22dbb13bf05940751877b5b8
# entrypoint: python@protocol_file_type_handler_registry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_file_type_handler_registry
# meta_type: tool
# === /OmniNode:Metadata ===


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
