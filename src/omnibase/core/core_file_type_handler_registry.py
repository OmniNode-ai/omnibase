# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: core_file_type_handler_registry.py
# version: 1.0.0
# uuid: d082a39b-579f-4827-afe3-5733ccdea23d
# author: OmniNode Team
# created_at: 2025-05-22T12:17:04.372004
# last_modified_at: 2025-05-22T20:50:39.720224
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: ce3ca9d1def0015af16b6aa36207bc43861091a9aacc5f0c1af67417d6d739a5
# entrypoint: python@core_file_type_handler_registry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.core_file_type_handler_registry
# meta_type: tool
# === /OmniNode:Metadata ===


import logging
from pathlib import Path
from typing import Dict, Optional

from omnibase.handlers.handler_ignore import IgnoreFileHandler
from omnibase.model.model_enum_file_type import FileTypeEnum
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_markdown import (
    MarkdownHandler,
)
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_metadata_yaml import (
    MetadataYAMLHandler,
)
from omnibase.runtimes.onex_runtime.v1_0_0.handlers.handler_python import PythonHandler


class FileTypeHandlerRegistry:
    """
    Registry for file type handlers. Maps file extensions and canonical filenames/roles to handler instances.
    """

    def __init__(self) -> None:
        self._handlers: Dict[FileTypeEnum, ProtocolFileTypeHandler] = {}
        self._logger = logging.getLogger("omnibase.FileTypeHandlerRegistry")
        self._extension_handlers: dict[str, ProtocolFileTypeHandler] = {}
        self._special_handlers: dict[str, ProtocolFileTypeHandler] = {}
        self._unhandled_extensions: set[str] = set()
        self._unhandled_specials: set[str] = set()

    def register(
        self, file_type: FileTypeEnum, handler: ProtocolFileTypeHandler
    ) -> None:
        self._handlers[file_type] = handler
        self._logger.debug(f"Registered handler for file type: {file_type}")

    def can_handle(self, file_type: FileTypeEnum) -> bool:
        return file_type in self._handlers

    def debug_log_unsupported(self, path: Path) -> None:
        self._logger.debug(f"Unsupported file type for: {path}")

    def register_handler(
        self, extension: str, handler: ProtocolFileTypeHandler
    ) -> None:
        """Register a handler for a file extension (e.g., '.py', '.yaml')."""
        self._extension_handlers[extension.lower()] = handler

    def register_special(self, filename: str, handler: ProtocolFileTypeHandler) -> None:
        """Register a handler for a canonical filename or role (e.g., 'node.onex.yaml')."""
        self._special_handlers[filename.lower()] = handler

    def get_handler(self, path: Path) -> Optional[ProtocolFileTypeHandler]:
        """Return the handler for the given path, or None if unhandled. Tracks unhandled types for debug logging."""
        # Check special filenames first
        if path.name.lower() in self._special_handlers:
            return self._special_handlers[path.name.lower()]
        # Then check extension
        ext = path.suffix.lower()
        handler = self._extension_handlers.get(ext)
        if handler is None:
            if ext:
                self._unhandled_extensions.add(ext)
            else:
                self._unhandled_specials.add(path.name.lower())
        return handler

    def handled_extensions(self) -> set[str]:
        return set(self._extension_handlers.keys())

    def handled_specials(self) -> set[str]:
        return set(self._special_handlers.keys())

    def log_unhandled_types(self, logger: Optional[logging.Logger] = None) -> None:
        """Log all unhandled file types encountered during this run (once per type)."""
        if self._unhandled_extensions or self._unhandled_specials:
            msg = "DEBUG: Ignored file type(s): "
            parts = []
            if self._unhandled_extensions:
                parts.append(", ".join(sorted(self._unhandled_extensions)))
            if self._unhandled_specials:
                parts.append(", ".join(sorted(self._unhandled_specials)))
            msg += "; ".join(parts) + " (no handler registered)"
            if logger:
                logger.debug(msg)
            else:
                print(msg)
        # Reset after logging
        self._unhandled_extensions.clear()
        self._unhandled_specials.clear()

    def register_all_handlers(self) -> None:
        self.register_handler(".py", PythonHandler())
        self.register_handler(".yaml", MetadataYAMLHandler())
        self.register_handler(".yml", MetadataYAMLHandler())
        self.register_handler(".md", MarkdownHandler())
        self.register_special(".onexignore", IgnoreFileHandler())
        self.register_special(".gitignore", IgnoreFileHandler())
