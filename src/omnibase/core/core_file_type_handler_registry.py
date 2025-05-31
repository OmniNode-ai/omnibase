# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.426013'
# description: Stamped by PythonHandler
# entrypoint: python://core_file_type_handler_registry
# hash: bc7c0b5865e69a8864f75614980760a6e587d4a2334b8b6e20b462d1defc9fcf
# last_modified_at: '2025-05-29T14:13:58.419139+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: core_file_type_handler_registry.py
# namespace: python://omnibase.core.core_file_type_handler_registry
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 1037f545-c709-4372-bb30-73859e348c64
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Any, Dict, Optional, Type, Union, List

try:
    from importlib.metadata import entry_points
except ImportError:
    # Python < 3.8 compatibility
    from importlib_metadata import entry_points

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import FileTypeEnum, LogLevelEnum
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler
from omnibase.protocol.protocol_handler_discovery import (
    HandlerInfo,
    ProtocolHandlerDiscovery,
    ProtocolHandlerRegistry,
)
from omnibase.enums.handler_source import HandlerSourceEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus

# Component identifier for logging
_COMPONENT_NAME = Path(__file__).stem


class HandlerRegistration:
    """Metadata for a registered handler."""

    def __init__(
        self,
        handler: ProtocolFileTypeHandler,
        name: str,
        source: HandlerSourceEnum = HandlerSourceEnum.CORE,
        priority: int = 0,
        override: bool = False,
    ):
        self.handler = handler
        self.name = name
        self.source = source  # HandlerSourceEnum
        self.priority = priority  # Higher priority wins conflicts
        self.override = override  # Whether this registration overrides existing


class FileTypeHandlerRegistry(ProtocolHandlerRegistry):
    """
    Registry for file type handlers. Maps file extensions and canonical filenames/roles to handler instances.

    Enhanced with plugin/override API for node-local handler extensions:
    - Runtime handler registration and override
    - Handler metadata and introspection
    - Priority-based conflict resolution
    - Source tracking (core/runtime/node-local/plugin)
    - Discovery-based handler registration
    """

    def __init__(self, event_bus: ProtocolEventBus) -> None:
        self._handlers: Dict[FileTypeEnum, ProtocolFileTypeHandler] = {}
        self._extension_handlers: dict[str, HandlerRegistration] = {}
        self._special_handlers: dict[str, HandlerRegistration] = {}
        self._named_handlers: dict[str, HandlerRegistration] = (
            {}
        )  # New: named handler registry
        self._unhandled_extensions: set[str] = set()
        self._unhandled_specials: set[str] = set()
        self._discovery_sources: List[ProtocolHandlerDiscovery] = []
        if event_bus is None:
            raise RuntimeError("FileTypeHandlerRegistry requires explicit event_bus injection (protocol purity)")
        self._event_bus = event_bus
        # Protocol purity: Do NOT import or instantiate runtime/node handlers here.
        # All special handlers must be registered via plugin discovery, event-driven registration, or handler injection.

    def register(
        self, file_type: FileTypeEnum, handler: ProtocolFileTypeHandler
    ) -> None:
        """Legacy method for backward compatibility."""
        self._handlers[file_type] = handler
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"Registered handler for file type: {file_type}",
            node_id=_COMPONENT_NAME,
            event_bus=self._event_bus,
        )

    def can_handle(self, file_type: FileTypeEnum) -> bool:
        """Legacy method for backward compatibility."""
        return file_type in self._handlers

    def debug_log_unsupported(self, path: Path) -> None:
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"Unsupported file type for: {path}",
            node_id=_COMPONENT_NAME,
            event_bus=self._event_bus,
        )

    def register_handler(
        self,
        extension_or_name: str,
        handler: Union[ProtocolFileTypeHandler, Type[ProtocolFileTypeHandler]],
        source: HandlerSourceEnum = HandlerSourceEnum.CORE,
        priority: int = 0,
        override: bool = False,
        **handler_kwargs: Any,
    ) -> None:
        """
        Enhanced handler registration API supporting both extension-based and named registration.

        Args:
            extension_or_name: File extension (e.g., '.py') or handler name (e.g., 'custom_yaml')
            handler: Handler instance or handler class
            source: Source of registration (HandlerSourceEnum)
            priority: Priority for conflict resolution (higher wins)
            override: Whether to override existing handlers
            **handler_kwargs: Arguments to pass to handler constructor if handler is a class
        """
        # Instantiate handler if class was passed
        if isinstance(handler, type):
            try:
                handler_instance = handler(event_bus=self._event_bus, **handler_kwargs)
            except TypeError:
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
                emit_log_event(
                    LogLevelEnum.WARNING,
                    f"Handler for extension {extension_or_name} already registered "
                    f"with higher/equal priority ({existing.priority} >= {priority}). "
                    f"Use override=True to force replacement.",
                    node_id=_COMPONENT_NAME,
                    event_bus=self._event_bus,
                )
                return

            self._extension_handlers[extension_or_name.lower()] = registration
            emit_log_event(
                LogLevelEnum.DEBUG,
                f"Registered {source} handler for extension {extension_or_name} "
                f"(priority: {priority}, override: {override})",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
        else:
            # Named handler registration
            existing = self._named_handlers.get(extension_or_name)
            if existing and not override and existing.priority >= priority:
                emit_log_event(
                    LogLevelEnum.WARNING,
                    f"Named handler {extension_or_name} already registered "
                    f"with higher/equal priority ({existing.priority} >= {priority}). "
                    f"Use override=True to force replacement.",
                    node_id=_COMPONENT_NAME,
                    event_bus=self._event_bus,
                )
                return

            self._named_handlers[extension_or_name] = registration
            emit_log_event(
                LogLevelEnum.DEBUG,
                f"Registered {source} named handler {extension_or_name} "
                f"(priority: {priority}, override: {override})",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )

    def register_special(
        self,
        filename: str,
        handler: Union[ProtocolFileTypeHandler, Type[ProtocolFileTypeHandler]],
        source: HandlerSourceEnum = HandlerSourceEnum.CORE,
        priority: int = 0,
        override: bool = False,
        **handler_kwargs: Any,
    ) -> None:
        """
        Enhanced special filename handler registration.
        """
        # Debug: log before registration
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[DEBUG] register_special: BEFORE registration for {filename} (current keys: {list(self._special_handlers.keys())})",
            node_id=_COMPONENT_NAME,
            event_bus=self._event_bus,
        )
        # Instantiate handler if class was passed
        if isinstance(handler, type):
            try:
                handler_instance = handler(event_bus=self._event_bus, **handler_kwargs)
            except TypeError:
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
            emit_log_event(
                LogLevelEnum.WARNING,
                f"Special handler for {filename} already registered "
                f"with higher/equal priority ({existing.priority} >= {priority}). "
                f"Use override=True to force replacement.",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
            emit_log_event(
                LogLevelEnum.DEBUG,
                f"[DEBUG] register_special: SKIPPED registration for {filename} (existing priority: {existing.priority}, new: {priority}, override: {override})",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
            return

        self._special_handlers[filename.lower()] = registration
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[DEBUG] register_special: AFTER registration for {filename} (current keys: {list(self._special_handlers.keys())})",
            node_id=_COMPONENT_NAME,
            event_bus=self._event_bus,
        )
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"Registered {source} special handler for {filename} "
            f"(priority: {priority}, override: {override})",
            node_id=_COMPONENT_NAME,
            event_bus=self._event_bus,
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

        # Debug log: print current special_handlers at start
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[DEBUG] list_handlers: current special_handlers at start: {list(self._special_handlers.keys())}",
            node_id=_COMPONENT_NAME,
            event_bus=self._event_bus,
        )

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
            handler_key = f"special:{filename}"
            emit_log_event(
                LogLevelEnum.DEBUG,
                f"[DEBUG] list_handlers: adding special handler with key: {handler_key}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
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

            emit_log_event(
                LogLevelEnum.DEBUG,
                f"[DEBUG] list_handlers: special handler_info for {filename}: {handler_info}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )

            handlers[handler_key] = handler_info

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

        # At the end of list_handlers, add a debug log to print all handler keys
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"[DEBUG] list_handlers keys: {list(handlers.keys())}",
            node_id=_COMPONENT_NAME,
            event_bus=self._event_bus,
        )
        return handlers

    def handled_extensions(self) -> set[str]:
        return set(self._extension_handlers.keys())

    def handled_specials(self) -> set[str]:
        return set(self._special_handlers.keys())

    def handled_names(self) -> set[str]:
        """Return the set of handled named handlers."""
        return set(self._named_handlers.keys())

    def log_unhandled_types(self, logger: Optional[object] = None) -> None:
        """
        Log all unhandled file types encountered during this run (once per type).

        Args:
            logger: Deprecated parameter kept for backward compatibility,
                   structured logging is used instead
        """
        if self._unhandled_extensions or self._unhandled_specials:
            msg = "Ignored file type(s): "
            parts = []
            if self._unhandled_extensions:
                parts.append(", ".join(sorted(self._unhandled_extensions)))
            if self._unhandled_specials:
                parts.append(", ".join(sorted(self._unhandled_specials)))
            msg += "; ".join(parts) + " (no handler registered)"
            emit_log_event(
                LogLevelEnum.DEBUG,
                msg,
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
        # Reset after logging
        self._unhandled_extensions.clear()
        self._unhandled_specials.clear()

    def register_discovery_source(self, discovery: ProtocolHandlerDiscovery) -> None:
        """
        Register a handler discovery source.
        
        Args:
            discovery: Handler discovery implementation
        """
        self._discovery_sources.append(discovery)
        emit_log_event(
            LogLevelEnum.DEBUG,
            f"Registered discovery source: {discovery.get_source_name()}",
            node_id=_COMPONENT_NAME,
            event_bus=self._event_bus,
        )

    def discover_and_register_handlers(self) -> None:
        """
        Discover and register handlers from all registered discovery sources.
        """
        for discovery in self._discovery_sources:
            try:
                handlers = discovery.discover_handlers()
                for handler_info in handlers:
                    self.register_handler_info(handler_info)
                
                emit_log_event(
                    LogLevelEnum.DEBUG,
                    f"Discovered {len(handlers)} handlers from {discovery.get_source_name()}",
                    node_id=_COMPONENT_NAME,
                    event_bus=self._event_bus,
                )
            except Exception as e:
                emit_log_event(
                    LogLevelEnum.ERROR,
                    f"Failed to discover handlers from {discovery.get_source_name()}: {e}",
                    node_id=_COMPONENT_NAME,
                    event_bus=self._event_bus,
                )

    def register_handler_info(self, handler_info: HandlerInfo) -> None:
        """
        Register a handler from HandlerInfo.
        
        Args:
            handler_info: Information about the handler to register
        """
        try:
            # Instantiate the handler with event_bus if supported
            try:
                handler_instance = handler_info.handler_class(event_bus=self._event_bus)
            except TypeError:
                handler_instance = handler_info.handler_class()
            # Register for extensions
            for extension in handler_info.extensions:
                self.register_handler(
                    extension,
                    handler_instance,
                    source=handler_info.source,
                    priority=handler_info.priority,
                )
            # Register for special files
            for special_file in handler_info.special_files:
                self.register_special(
                    special_file,
                    handler_instance,
                    source=handler_info.source,
                    priority=handler_info.priority,
                )
                
        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"Failed to register handler {handler_info.name}: {e}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )

    def register_all_handlers(self) -> None:
        """Register all canonical handlers using discovery sources (protocol-pure: no runtime/node imports)."""
        self.discover_and_register_handlers()
        self.discover_plugin_handlers()
        # Protocol purity: Do NOT import or instantiate runtime/node handlers here.
        # After registration, check for required special handlers and emit protocol-pure error if missing.
        required_specials = ['.onexignore', '.gitignore']
        missing = [s for s in required_specials if s not in self._special_handlers]
        if missing:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"[PROTOCOL PURITY] Missing required special handler(s): {missing}. Must be registered via plugin or event-driven registration.",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )

    def discover_plugin_handlers(self) -> None:
        """
        Discover and register handlers from entry points.

        Looks for entry points in the 'omnibase.handlers' group and registers
        them as plugin handlers with correct type/source for all supported extensions and special files.
        """
        try:
            eps = entry_points()
            if hasattr(eps, "select"):
                handler_eps = eps.select(group="omnibase.handlers")
            else:
                handler_eps = eps.get("omnibase.handlers", [])

            emit_log_event(
                LogLevelEnum.DEBUG,
                f"[DEBUG] discover_plugin_handlers: Found {len(handler_eps)} entry points in 'omnibase.handlers': {[ (ep.name, ep.value) for ep in handler_eps ]}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )

            core_extensions = {".py", ".yaml", ".yml", ".md", ".markdown", ".mdx"}
            core_specials = {".onexignore", ".gitignore"}

            for ep in handler_eps:
                try:
                    handler_class = ep.load()
                    if not self._is_valid_handler_class(handler_class):
                        emit_log_event(
                            LogLevelEnum.WARNING,
                            f"Plugin handler {ep.name} from {ep.value} does not implement ProtocolFileTypeHandler. Skipping.",
                            node_id=_COMPONENT_NAME,
                            event_bus=self._event_bus,
                        )
                        continue
                    try:
                        handler_instance = handler_class(event_bus=self._event_bus)
                    except TypeError:
                        handler_instance = handler_class()
                    # Register for all supported extensions
                    if hasattr(handler_instance, "get_supported_extensions"):
                        for ext in handler_instance.get_supported_extensions():
                            if ext in core_extensions:
                                self.register_handler(
                                    ext,
                                    handler_instance,
                                    source=HandlerSourceEnum.CORE,
                                    priority=100,
                                )
                            else:
                                self.register_handler(
                                    ext,
                                    handler_instance,
                                    source=HandlerSourceEnum.PLUGIN,
                                    priority=0,
                                )
                    elif hasattr(handler_instance, "supported_extensions"):
                        for ext in handler_instance.supported_extensions:
                            if ext in core_extensions:
                                self.register_handler(
                                    ext,
                                    handler_instance,
                                    source=HandlerSourceEnum.CORE,
                                    priority=100,
                                )
                            else:
                                self.register_handler(
                                    ext,
                                    handler_instance,
                                    source=HandlerSourceEnum.PLUGIN,
                                    priority=0,
                                )
                    # Register for all special files
                    if hasattr(handler_instance, "get_special_files"):
                        for special_file in handler_instance.get_special_files():
                            if special_file in core_specials:
                                # Instantiate a new handler for each special file
                                try:
                                    special_handler_instance = handler_class(event_bus=self._event_bus)
                                except TypeError:
                                    special_handler_instance = handler_class()
                                self.register_special(
                                    special_file,
                                    special_handler_instance,
                                    source=HandlerSourceEnum.CORE,
                                    priority=100,
                                )
                                emit_log_event(
                                    LogLevelEnum.DEBUG,
                                    f"[DEBUG] Registered special handler for {special_file} via plugin discovery.",
                                    node_id=_COMPONENT_NAME,
                                    event_bus=self._event_bus,
                                )
                            else:
                                try:
                                    special_handler_instance = handler_class(event_bus=self._event_bus)
                                except TypeError:
                                    special_handler_instance = handler_class()
                                self.register_special(
                                    special_file,
                                    special_handler_instance,
                                    source=HandlerSourceEnum.PLUGIN,
                                    priority=0,
                                )
                    elif hasattr(handler_instance, "supported_filenames"):
                        for special_file in handler_instance.supported_filenames:
                            if special_file in core_specials:
                                # Instantiate a new handler for each special file
                                try:
                                    special_handler_instance = handler_class(event_bus=self._event_bus)
                                except TypeError:
                                    special_handler_instance = handler_class()
                                self.register_special(
                                    special_file,
                                    special_handler_instance,
                                    source=HandlerSourceEnum.CORE,
                                    priority=100,
                                )
                                emit_log_event(
                                    LogLevelEnum.DEBUG,
                                    f"[DEBUG] Registered special handler for {special_file} via plugin discovery.",
                                    node_id=_COMPONENT_NAME,
                                    event_bus=self._event_bus,
                                )
                            else:
                                try:
                                    special_handler_instance = handler_class(event_bus=self._event_bus)
                                except TypeError:
                                    special_handler_instance = handler_class()
                                self.register_special(
                                    special_file,
                                    special_handler_instance,
                                    source=HandlerSourceEnum.PLUGIN,
                                    priority=0,
                                )
                    # Also register by entry-point name as a named handler (for legacy compatibility)
                    self.register_handler(
                        ep.name,
                        handler_instance,
                        source=HandlerSourceEnum.PLUGIN,
                        priority=0,
                    )
                    emit_log_event(
                        LogLevelEnum.INFO,
                        f"Discovered and registered plugin handler: {ep.name} from {ep.value}",
                        node_id=_COMPONENT_NAME,
                        event_bus=self._event_bus,
                    )
                except Exception as e:
                    emit_log_event(
                        LogLevelEnum.ERROR,
                        f"[DEBUG] Failed to load plugin handler {ep.name} from {ep.value}: {e}",
                        node_id=_COMPONENT_NAME,
                        event_bus=self._event_bus,
                    )
        except Exception as e:
            emit_log_event(
                LogLevelEnum.ERROR,
                f"[DEBUG] Failed to discover plugin handlers: {e}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )

    def _is_valid_handler_class(self, handler_class: Type) -> bool:
        """
        Validate that a class implements the ProtocolFileTypeHandler interface.

        Args:
            handler_class: The class to validate

        Returns:
            True if the class implements the required protocol methods
        """
        required_methods = [
            "can_handle",
            "extract_block",
            "serialize_block",
            "stamp",
            "validate",
            "pre_validate",
            "post_validate",
        ]

        required_properties = [
            "handler_name",
            "handler_version",
            "handler_author",
            "handler_description",
            "supported_extensions",
            "supported_filenames",
            "handler_priority",
            "requires_content_analysis",
        ]

        try:
            # Check if it's a class
            if not isinstance(handler_class, type):
                return False

            # Try to instantiate it (basic validation)
            instance = handler_class()

            # Check required methods
            for method_name in required_methods:
                if not hasattr(instance, method_name) or not callable(
                    getattr(instance, method_name)
                ):
                    emit_log_event(
                        LogLevelEnum.DEBUG,
                        f"Handler {handler_class.__name__} missing method: {method_name}",
                        node_id=_COMPONENT_NAME,
                        event_bus=self._event_bus,
                    )
                    return False

            # Check required properties
            for prop_name in required_properties:
                if not hasattr(instance, prop_name):
                    emit_log_event(
                        LogLevelEnum.DEBUG,
                        f"Handler {handler_class.__name__} missing property: {prop_name}",
                        node_id=_COMPONENT_NAME,
                        event_bus=self._event_bus,
                    )
                    return False

            return True

        except Exception as e:
            emit_log_event(
                LogLevelEnum.DEBUG,
                f"Failed to validate handler class {handler_class}: {e}",
                node_id=_COMPONENT_NAME,
                event_bus=self._event_bus,
            )
            return False

    def register_plugin_handlers_from_config(
        self, config_path: Optional[str] = None
    ) -> None:
        """
        Register plugin handlers from a configuration file.

        Args:
            config_path: Path to configuration file. If None, looks for default locations.
        """
        import os

        import yaml

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

                    handlers = config.get("handlers", {})
                    for name, handler_config in handlers.items():
                        try:
                            # Import the handler class
                            module_path = handler_config["module"]
                            class_name = handler_config["class"]

                            module = __import__(module_path, fromlist=[class_name])
                            handler_class = getattr(module, class_name)

                            # Register the handler
                            self.register_handler(
                                name,
                                handler_class,
                                source=HandlerSourceEnum.PLUGIN,
                                priority=handler_config.get("priority", 0),
                            )

                            emit_log_event(
                                LogLevelEnum.INFO,
                                f"Registered plugin handler from config: {name} "
                                f"({module_path}.{class_name})",
                                node_id=_COMPONENT_NAME,
                                event_bus=self._event_bus,
                            )

                        except Exception as e:
                            emit_log_event(
                                LogLevelEnum.ERROR,
                                f"Failed to load plugin handler {name} from config: {e}",
                                node_id=_COMPONENT_NAME,
                                event_bus=self._event_bus,
                            )

                    break  # Use first found config file

                except Exception as e:
                    emit_log_event(
                        LogLevelEnum.ERROR,
                        f"Failed to load plugin config from {path}: {e}",
                        node_id=_COMPONENT_NAME,
                        event_bus=self._event_bus,
                    )

    def register_plugin_handlers_from_env(self) -> None:
        """
        Register plugin handlers from environment variables.

        Looks for environment variables in the format:
        ONEX_PLUGIN_HANDLER_<NAME>=module.path:ClassName
        """
        import os

        prefix = "ONEX_PLUGIN_HANDLER_"

        for env_var, value in os.environ.items():
            if env_var.startswith(prefix):
                handler_name = env_var[len(prefix) :].lower()

                try:
                    # Parse module:class format
                    if ":" not in value:
                        emit_log_event(
                            LogLevelEnum.ERROR,
                            f"Invalid handler specification in {env_var}: {value}. "
                            f"Expected format: module.path:ClassName",
                            node_id=_COMPONENT_NAME,
                            event_bus=self._event_bus,
                        )
                        continue

                    module_path, class_name = value.split(":", 1)

                    # Import the handler class
                    module = __import__(module_path, fromlist=[class_name])
                    handler_class = getattr(module, class_name)

                    # Register the handler
                    self.register_handler(
                        handler_name, handler_class, source=HandlerSourceEnum.PLUGIN, priority=0
                    )

                    emit_log_event(
                        LogLevelEnum.INFO,
                        f"Registered plugin handler from environment: {handler_name} "
                        f"({module_path}.{class_name})",
                        node_id=_COMPONENT_NAME,
                        event_bus=self._event_bus,
                    )

                except Exception as e:
                    emit_log_event(
                        LogLevelEnum.ERROR,
                        f"Failed to load plugin handler from {env_var}: {e}",
                        node_id=_COMPONENT_NAME,
                        event_bus=self._event_bus,
                    )

    def register_node_local_handlers(self, handlers: dict[str, Any]) -> None:
        """
        Convenience method for nodes to register their local handlers.

        Args:
            handlers: Dict mapping extensions/names to handler classes or instances
        """
        for key, handler in handlers.items():
            if key.startswith("."):
                self.register_handler(key, handler, source=HandlerSourceEnum.NODE_LOCAL, priority=10)
            elif key.startswith("special:"):
                filename = key[8:]  # Remove 'special:' prefix
                self.register_special(
                    filename, handler, source=HandlerSourceEnum.NODE_LOCAL, priority=10
                )
            else:
                self.register_handler(key, handler, source=HandlerSourceEnum.NODE_LOCAL, priority=10)

    def clear_registry(self) -> None:
        self._handlers.clear()
        self._extension_handlers.clear()
        self._special_handlers.clear()
        self._named_handlers.clear()
        self._unhandled_extensions.clear()
        self._unhandled_specials.clear()
        self._discovery_sources.clear()
