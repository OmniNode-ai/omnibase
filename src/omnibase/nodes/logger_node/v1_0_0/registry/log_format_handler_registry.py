# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: log_format_handler_registry.py
# version: 1.0.0
# uuid: 8d921154-14c6-4bdb-a274-efb7d8782fec
# author: OmniNode Team
# created_at: 2025-05-26T12:12:29.317096
# last_modified_at: 2025-05-26T16:53:38.736999
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 08a65b5178e96e8d48b71f565c3875a368d3cecb902f7c9f96cc188c43c606bf
# entrypoint: python@log_format_handler_registry.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.log_format_handler_registry
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Registry for pluggable log format handlers in the logger node.

This registry manages the discovery, registration, and selection of log format
handlers, following the established ONEX architecture patterns for pluggable
components with priority-based conflict resolution.
"""

import logging
from typing import Any, Dict, Optional, Type, Union

from ..protocol.protocol_log_format_handler import ProtocolLogFormatHandler


class HandlerRegistration:
    """Metadata for a registered log format handler."""

    def __init__(
        self,
        handler: ProtocolLogFormatHandler,
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


class LogFormatHandlerRegistry:
    """
    Registry for log format handlers in the logger node.

    Manages registration, discovery, and selection of format handlers with
    priority-based conflict resolution and source tracking.

    Follows the established ONEX architecture patterns for pluggable components.
    """

    def __init__(self) -> None:
        self._format_handlers: Dict[str, HandlerRegistration] = {}
        self._logger = logging.getLogger("omnibase.LogFormatHandlerRegistry")
        self._unhandled_formats: set[str] = set()

    def register_handler(
        self,
        format_name: str,
        handler: Union[ProtocolLogFormatHandler, Type[ProtocolLogFormatHandler]],
        source: str = "unknown",
        priority: int = 0,
        override: bool = False,
        **handler_kwargs: Any,
    ) -> None:
        """
        Register a log format handler.

        Args:
            format_name: Format name (e.g., 'json', 'yaml', 'markdown')
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
            name=format_name,
            source=source,
            priority=priority,
            override=override,
        )

        # Check for existing registration
        existing = self._format_handlers.get(format_name.lower())
        if existing and not override and existing.priority >= priority:
            self._logger.warning(
                f"Handler for format {format_name} already registered "
                f"with higher/equal priority ({existing.priority} >= {priority}). "
                f"Use override=True to force replacement."
            )
            return

        self._format_handlers[format_name.lower()] = registration
        self._logger.debug(
            f"Registered {source} handler for format {format_name} "
            f"(priority: {priority}, override: {override})"
        )

    def get_handler(self, format_name: str) -> Optional[ProtocolLogFormatHandler]:
        """
        Get a handler for the specified format.

        Args:
            format_name: Format name to look up

        Returns:
            Handler instance if found, None otherwise
        """
        registration = self._format_handlers.get(format_name.lower())
        if registration:
            return registration.handler

        # Track unhandled formats for debugging
        self._unhandled_formats.add(format_name.lower())
        return None

    def can_handle(self, format_name: str) -> bool:
        """
        Check if a format can be handled.

        Args:
            format_name: Format name to check

        Returns:
            True if a handler is registered for this format
        """
        return format_name.lower() in self._format_handlers

    def list_handlers(self) -> Dict[str, Dict[str, Any]]:
        """List all registered handlers with metadata."""
        handlers = {}

        for format_name, reg in self._format_handlers.items():
            handler_info = {
                "format": format_name,
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
                        "supported_formats": reg.handler.supported_formats,
                        "handler_priority": reg.handler.handler_priority,
                        "requires_dependencies": reg.handler.requires_dependencies,
                        "dependencies_available": reg.handler.validate_dependencies(),
                        "format_metadata": reg.handler.get_format_metadata(),
                    }
                )
            except AttributeError:
                # Handler doesn't implement metadata properties (legacy handler)
                handler_info["metadata_available"] = False

            handlers[f"format:{format_name}"] = handler_info

        return handlers

    def handled_formats(self) -> set[str]:
        """Return the set of handled format names."""
        return set(self._format_handlers.keys())

    def log_unhandled_formats(self, logger: Optional[logging.Logger] = None) -> None:
        """Log all unhandled formats encountered during this run (once per format)."""
        if self._unhandled_formats:
            msg = f"DEBUG: Unhandled format(s): {', '.join(sorted(self._unhandled_formats))} (no handler registered)"
            if logger:
                logger.debug(msg)
            else:
                print(msg)
        # Reset after logging
        self._unhandled_formats.clear()

    def register_all_handlers(self) -> None:
        """Register all canonical format handlers with proper source and priority."""
        # Import and register core format handlers
        from ..handlers.handler_csv_format import CsvFormatHandler
        from ..handlers.handler_json_format import JsonFormatHandler
        from ..handlers.handler_markdown_format import MarkdownFormatHandler
        from ..handlers.handler_text_format import TextFormatHandler
        from ..handlers.handler_yaml_format import YamlFormatHandler

        # Core handlers (highest priority)
        self.register_handler("json", JsonFormatHandler(), source="core", priority=100)
        self.register_handler("yaml", YamlFormatHandler(), source="core", priority=100)
        self.register_handler("yml", YamlFormatHandler(), source="core", priority=100)
        self.register_handler(
            "markdown", MarkdownFormatHandler(), source="core", priority=100
        )
        self.register_handler("text", TextFormatHandler(), source="core", priority=100)
        self.register_handler("csv", CsvFormatHandler(), source="core", priority=100)

        # Discover and register plugin handlers
        self.discover_plugin_handlers()

    def discover_plugin_handlers(self) -> None:
        """
        Discover and register handlers from entry points.

        Looks for entry points in the 'omnibase.logger_format_handlers' group and
        registers them as plugin handlers with priority 0.
        """
        try:
            from importlib.metadata import entry_points

            # Get all entry points for the logger format handlers group
            eps = entry_points()

            # Handle both new and old importlib.metadata APIs
            if hasattr(eps, "select"):
                # New API (Python 3.10+)
                handler_eps = eps.select(group="omnibase.logger_format_handlers")
            else:
                # Old API (Python < 3.10)
                handler_eps = eps.get("omnibase.logger_format_handlers", [])  # type: ignore

            for ep in handler_eps:
                try:
                    # Load the handler class
                    handler_class = ep.load()

                    # Validate that it implements the protocol
                    if not self._is_valid_handler_class(handler_class):
                        self._logger.warning(
                            f"Plugin handler {ep.name} from {ep.value} does not "
                            f"implement ProtocolLogFormatHandler. Skipping."
                        )
                        continue

                    # Register the handler with the entry point name
                    self.register_handler(
                        ep.name, handler_class, source="plugin", priority=0
                    )

                    self._logger.info(
                        f"Discovered and registered plugin format handler: {ep.name} "
                        f"from {ep.value}"
                    )

                except Exception as e:
                    self._logger.error(
                        f"Failed to load plugin format handler {ep.name} from {ep.value}: {e}"
                    )

        except Exception as e:
            self._logger.error(f"Failed to discover plugin format handlers: {e}")

    def _is_valid_handler_class(self, handler_class: Type) -> bool:
        """
        Validate that a class implements the ProtocolLogFormatHandler interface.

        Args:
            handler_class: The class to validate

        Returns:
            True if the class implements the required protocol methods
        """
        required_methods = [
            "can_handle",
            "format_log_entry",
            "validate_dependencies",
            "get_format_metadata",
        ]

        required_properties = [
            "handler_name",
            "handler_version",
            "handler_author",
            "handler_description",
            "supported_formats",
            "handler_priority",
            "requires_dependencies",
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
                    self._logger.debug(
                        f"Handler {handler_class.__name__} missing method: {method_name}"
                    )
                    return False

            # Check required properties
            for prop_name in required_properties:
                if not hasattr(instance, prop_name):
                    self._logger.debug(
                        f"Handler {handler_class.__name__} missing property: {prop_name}"
                    )
                    return False

            return True

        except Exception as e:
            self._logger.debug(f"Failed to validate handler class {handler_class}: {e}")
            return False

    def register_node_local_handlers(self, handlers: Dict[str, Any]) -> None:
        """
        Convenience method for nodes to register their local format handlers.

        Args:
            handlers: Dict mapping format names to handler classes or instances
        """
        for format_name, handler in handlers.items():
            self.register_handler(
                format_name, handler, source="node-local", priority=10
            )
