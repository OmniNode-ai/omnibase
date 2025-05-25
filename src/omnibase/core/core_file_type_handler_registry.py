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
from typing import Any, Dict, Optional, Type, Union

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


class HandlerRegistration:
    """Metadata for a registered handler."""

    def __init__(
        self,
        handler: ProtocolFileTypeHandler,
        name: str,
        source: str = "unknown",
        priority: int = 0,
        override: bool = False,
    ):
        self.handler = handler
        self.name = name
        self.source = source  # "core", "runtime", "node-local", "plugin"
        self.priority = priority  # Higher priority wins conflicts
        self.override = override  # Whether this registration overrides existing


class FileTypeHandlerRegistry:
    """
    Registry for file type handlers. Maps file extensions and canonical filenames/roles to handler instances.

    Enhanced with plugin/override API for node-local handler extensions:
    - Runtime handler registration and override
    - Handler metadata and introspection
    - Priority-based conflict resolution
    - Source tracking (core/runtime/node-local/plugin)
    """

    def __init__(self) -> None:
        self._handlers: Dict[FileTypeEnum, ProtocolFileTypeHandler] = {}
        self._logger = logging.getLogger("omnibase.FileTypeHandlerRegistry")
        self._extension_handlers: dict[str, HandlerRegistration] = {}
        self._special_handlers: dict[str, HandlerRegistration] = {}
        self._named_handlers: dict[str, HandlerRegistration] = (
            {}
        )  # New: named handler registry
        self._unhandled_extensions: set[str] = set()
        self._unhandled_specials: set[str] = set()

    def register(
        self, file_type: FileTypeEnum, handler: ProtocolFileTypeHandler
    ) -> None:
        """Legacy method for backward compatibility."""
        self._handlers[file_type] = handler
        self._logger.debug(f"Registered handler for file type: {file_type}")

    def can_handle(self, file_type: FileTypeEnum) -> bool:
        """Legacy method for backward compatibility."""
        return file_type in self._handlers

    def debug_log_unsupported(self, path: Path) -> None:
        self._logger.debug(f"Unsupported file type for: {path}")

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
        # Instantiate handler if class was passed
        if isinstance(handler, type):
            handler_instance = handler(**handler_kwargs)
        else:
            handler_instance = handler

        registration = HandlerRegistration(
            handler=handler_instance,
            name=extension_or_name,
            source=source,
            priority=priority,
            override=override,
        )

        # Determine if this is an extension or named handler
        if extension_or_name.startswith("."):
            # Extension-based registration
            existing = self._extension_handlers.get(extension_or_name.lower())
            if existing and not override and existing.priority >= priority:
                self._logger.warning(
                    f"Handler for extension {extension_or_name} already registered "
                    f"with higher/equal priority ({existing.priority} >= {priority}). "
                    f"Use override=True to force replacement."
                )
                return

            self._extension_handlers[extension_or_name.lower()] = registration
            self._logger.debug(
                f"Registered {source} handler for extension {extension_or_name} "
                f"(priority: {priority}, override: {override})"
            )
        else:
            # Named handler registration
            existing = self._named_handlers.get(extension_or_name)
            if existing and not override and existing.priority >= priority:
                self._logger.warning(
                    f"Named handler {extension_or_name} already registered "
                    f"with higher/equal priority ({existing.priority} >= {priority}). "
                    f"Use override=True to force replacement."
                )
                return

            self._named_handlers[extension_or_name] = registration
            self._logger.debug(
                f"Registered {source} named handler {extension_or_name} "
                f"(priority: {priority}, override: {override})"
            )

    def register_special(
        self,
        filename: str,
        handler: Union[ProtocolFileTypeHandler, Type[ProtocolFileTypeHandler]],
        source: str = "unknown",
        priority: int = 0,
        override: bool = False,
        **handler_kwargs: Any,
    ) -> None:
        """
        Enhanced special filename handler registration.

        Args:
            filename: Special filename (e.g., '.onexignore')
            handler: Handler instance or handler class
            source: Source of registration ("core", "runtime", "node-local", "plugin")
            priority: Priority for conflict resolution (higher wins)
            override: Whether to override existing handlers
            **handler_kwargs: Arguments to pass to handler constructor if handler is a class
        """
        # Instantiate handler if class was passed
        if isinstance(handler, type):
            handler_instance = handler(**handler_kwargs)
        else:
            handler_instance = handler

        registration = HandlerRegistration(
            handler=handler_instance,
            name=filename,
            source=source,
            priority=priority,
            override=override,
        )

        existing = self._special_handlers.get(filename.lower())
        if existing and not override and existing.priority >= priority:
            self._logger.warning(
                f"Special handler for {filename} already registered "
                f"with higher/equal priority ({existing.priority} >= {priority}). "
                f"Use override=True to force replacement."
            )
            return

        self._special_handlers[filename.lower()] = registration
        self._logger.debug(
            f"Registered {source} special handler for {filename} "
            f"(priority: {priority}, override: {override})"
        )

    def get_handler(self, path: Path) -> Optional[ProtocolFileTypeHandler]:
        """Return the handler for the given path, or None if unhandled. Tracks unhandled types for debug logging."""
        # Check special filenames first
        special_reg = self._special_handlers.get(path.name.lower())
        if special_reg:
            return special_reg.handler

        # Then check extension
        ext = path.suffix.lower()
        ext_reg = self._extension_handlers.get(ext)
        if ext_reg:
            return ext_reg.handler

        # Track unhandled types
        if ext:
            self._unhandled_extensions.add(ext)
        else:
            self._unhandled_specials.add(path.name.lower())
        return None

    def get_named_handler(self, name: str) -> Optional[ProtocolFileTypeHandler]:
        """Get a handler by name."""
        registration = self._named_handlers.get(name)
        return registration.handler if registration else None

    def list_handlers(self) -> dict[str, dict[str, Any]]:
        """List all registered handlers with metadata."""
        handlers = {}

        # Extension handlers
        for ext, reg in self._extension_handlers.items():
            handler_info = {
                "type": "extension",
                "key": ext,
                "handler_class": reg.handler.__class__.__name__,
                "source": reg.source,
                "priority": reg.priority,
                "override": reg.override,
            }

            # Add handler metadata if available
            try:
                handler_info.update(
                    {
                        "handler_name": reg.handler.handler_name,
                        "handler_version": reg.handler.handler_version,
                        "handler_author": reg.handler.handler_author,
                        "handler_description": reg.handler.handler_description,
                        "supported_extensions": reg.handler.supported_extensions,
                        "supported_filenames": reg.handler.supported_filenames,
                        "handler_priority": reg.handler.handler_priority,
                        "requires_content_analysis": reg.handler.requires_content_analysis,
                    }
                )
            except AttributeError:
                # Handler doesn't implement metadata properties (legacy handler)
                handler_info["metadata_available"] = False

            handlers[f"extension:{ext}"] = handler_info

        # Special handlers
        for filename, reg in self._special_handlers.items():
            handler_info = {
                "type": "special",
                "key": filename,
                "handler_class": reg.handler.__class__.__name__,
                "source": reg.source,
                "priority": reg.priority,
                "override": reg.override,
            }

            # Add handler metadata if available
            try:
                handler_info.update(
                    {
                        "handler_name": reg.handler.handler_name,
                        "handler_version": reg.handler.handler_version,
                        "handler_author": reg.handler.handler_author,
                        "handler_description": reg.handler.handler_description,
                        "supported_extensions": reg.handler.supported_extensions,
                        "supported_filenames": reg.handler.supported_filenames,
                        "handler_priority": reg.handler.handler_priority,
                        "requires_content_analysis": reg.handler.requires_content_analysis,
                    }
                )
            except AttributeError:
                # Handler doesn't implement metadata properties (legacy handler)
                handler_info["metadata_available"] = False

            handlers[f"special:{filename}"] = handler_info

        # Named handlers
        for name, reg in self._named_handlers.items():
            handler_info = {
                "type": "named",
                "key": name,
                "handler_class": reg.handler.__class__.__name__,
                "source": reg.source,
                "priority": reg.priority,
                "override": reg.override,
            }

            # Add handler metadata if available
            try:
                handler_info.update(
                    {
                        "handler_name": reg.handler.handler_name,
                        "handler_version": reg.handler.handler_version,
                        "handler_author": reg.handler.handler_author,
                        "handler_description": reg.handler.handler_description,
                        "supported_extensions": reg.handler.supported_extensions,
                        "supported_filenames": reg.handler.supported_filenames,
                        "handler_priority": reg.handler.handler_priority,
                        "requires_content_analysis": reg.handler.requires_content_analysis,
                    }
                )
            except AttributeError:
                # Handler doesn't implement metadata properties (legacy handler)
                handler_info["metadata_available"] = False

            handlers[f"named:{name}"] = handler_info

        return handlers

    def handled_extensions(self) -> set[str]:
        return set(self._extension_handlers.keys())

    def handled_specials(self) -> set[str]:
        return set(self._special_handlers.keys())

    def handled_names(self) -> set[str]:
        """Return the set of handled named handlers."""
        return set(self._named_handlers.keys())

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
        """Register all canonical handlers with proper source and priority."""
        # Core handlers (highest priority)
        self.register_special(
            ".onexignore", IgnoreFileHandler(), source="core", priority=100
        )
        self.register_special(
            ".gitignore", IgnoreFileHandler(), source="core", priority=100
        )

        # Runtime handlers (medium priority)
        self.register_handler(".py", PythonHandler(), source="runtime", priority=50)
        self.register_handler(
            ".yaml", MetadataYAMLHandler(), source="runtime", priority=50
        )
        self.register_handler(
            ".yml", MetadataYAMLHandler(), source="runtime", priority=50
        )
        self.register_handler(".md", MarkdownHandler(), source="runtime", priority=50)

    def register_node_local_handlers(self, handlers: dict[str, Any]) -> None:
        """
        Convenience method for nodes to register their local handlers.

        Args:
            handlers: Dict mapping extensions/names to handler classes or instances
        """
        for key, handler in handlers.items():
            if key.startswith("."):
                self.register_handler(key, handler, source="node-local", priority=10)
            elif key.startswith("special:"):
                filename = key[8:]  # Remove 'special:' prefix
                self.register_special(
                    filename, handler, source="node-local", priority=10
                )
            else:
                self.register_handler(key, handler, source="node-local", priority=10)
