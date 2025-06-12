# === OmniNode:Metadata ===
# author: OmniNode Team
# description: Canonical registry for tools in node_logger
# === /OmniNode:Metadata ===

from typing import Dict, Type, Optional, Any
from pathlib import Path

from omnibase.enums.metadata import ToolRegistryModeEnum
from omnibase.core.core_errors import RegistryErrorCode, OnexError
from omnibase.registry.base_registry import BaseOnexRegistry
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.protocol.protocol_tool import ProtocolTool
from omnibase.protocol.protocol_logger import ProtocolLogger

from ..tools.tool_logger_emit_log_event import (
    ToolLoggerEmitLogEvent,
    emit_log_event, 
    emit_log_event_sync, 
    emit_log_event_async, 
    trace_function_lifecycle, 
    ToolLoggerCodeBlock, 
    tool_logger_performance_metrics
)
from ..tools.tool_backend_selection import StubBackendSelection
from ..tools.tool_text_format import ToolTextFormat
from ..tools.tool_json_format import ToolJsonFormat
from ..tools.tool_yaml_format import ToolYamlFormat
from ..tools.tool_markdown_format import ToolMarkdownFormat
from ..tools.tool_csv_format import ToolCsvFormat
from ..tools.tool_context_aware_output_handler import ToolContextAwareOutputHandler
from ..tools.tool_smart_log_formatter import ToolSmartLogFormatter, create_smart_formatter
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from ..tools.tool_logger_engine import ToolLoggerEngine

class RegistryNodeLogger(BaseOnexRegistry):
    """
    Canonical registry for pluggable tools in ONEX logger node.
    
    Provides central service management for all logging-related tools and formatters
    according to the registry-centric architecture pattern. All operations are strongly
    typed and protocol-compliant.
    
    Features:
    - Registry-based tool discovery and instantiation
    - Support for multiple output formats (text, JSON, YAML, Markdown, CSV)
    - Smart formatting with context-aware level selection
    - Fallback mechanisms for bootstrap scenarios
    - Comprehensive correlation ID tracking
    
    Usage:
        registry = RegistryNodeLogger(node_dir=Path("path/to/node"), 
                                     tool_collection=custom_tools, 
                                     mode=ToolRegistryModeEnum.REAL)
        emit_log = registry.get_tool("emit_log_event")
        formatter = registry.get_tool("smart_log_formatter")
    """
    
    # Canonical tools provided by this registry, automatically registered
    CANONICAL_TOOLS = {
        'tool_logger_emit_log_event': ToolLoggerEmitLogEvent(),
        'emit_log_event': emit_log_event,
        'emit_log_event_sync': emit_log_event_sync,
        'emit_log_event_async': emit_log_event_async,
        'trace_function_lifecycle': trace_function_lifecycle,
        'ToolLoggerCodeBlock': ToolLoggerCodeBlock,
        'tool_logger_performance_metrics': tool_logger_performance_metrics,
        'backend_selection': StubBackendSelection,
        'inmemory': InMemoryEventBus,
        'text': ToolTextFormat(),
        'json': ToolJsonFormat(),
        'tool_yaml_format': ToolYamlFormat,
        'tool_markdown_format': ToolMarkdownFormat(),
        'csv': ToolCsvFormat(),
        'context_aware_output_handler': ToolContextAwareOutputHandler(),
        'tool_smart_log_formatter': ToolSmartLogFormatter(),
        'smart_log_formatter': ToolSmartLogFormatter,  # DEPRECATED: use tool_smart_log_formatter instance
        'create_smart_formatter': create_smart_formatter,
        'tool_logger_engine': ToolLoggerEngine(),
    }

    def __init__(
        self, 
        node_dir: Path, 
        tool_collection: Optional[Dict[str, Any]] = None, 
        logger: Optional[ProtocolLogger] = None, 
        mode: ToolRegistryModeEnum = ToolRegistryModeEnum.REAL,
        dependency_mode: Optional[str] = None,
    ):
        """
        Initialize the logger node registry with optional tool collection and mode.
        
        Args:
            node_dir: Path to the node directory
            tool_collection: Optional dictionary of custom tools to register
            logger: Optional logger instance for registry operations
            mode: Registry mode (REAL or MOCK)
            dependency_mode: Optional dependency resolution mode
        """
        super().__init__(node_dir, tool_collection, mode, logger)
        self.dependency_mode = dependency_mode
        
        if self.logger:
            self.logger.log(f"[RegistryNodeLogger] Initialized with {len(self._tools)} registered tools")
            self.logger.log(f"[RegistryNodeLogger] Mode: {mode}, Dependency mode: {dependency_mode}")

    def set_mode(self, mode: ToolRegistryModeEnum) -> None:
        """
        Set the registry mode (REAL or MOCK).
        
        Args:
            mode: Registry mode enum value
            
        Raises:
            OnexError: If the mode is invalid
        """
        if mode not in (ToolRegistryModeEnum.REAL, ToolRegistryModeEnum.MOCK):
            if self.logger:
                self.logger.log(f"Invalid registry mode: {mode}")
            raise OnexError(
                message=f"Invalid registry mode: {mode}",
                error_code=RegistryErrorCode.INVALID_MODE
            )
        self.mode = mode
        if self.logger:
            self.logger.log(f"Registry mode set to: {mode}")

    def set_logger(self, logger: Optional[ProtocolLogger]) -> None:
        """
        Set the logger for registry operations.
        
        Args:
            logger: Logger instance implementing ProtocolLogger
        """
        self.logger = logger

    def register_tool(self, key: str, tool_cls: Any) -> None:
        """
        Register a new tool with the registry.
        
        Args:
            key: Tool name/key
            tool_cls: Tool class or instance
            
        Raises:
            OnexError: If the tool is already registered
        """
        if key in self._tools:
            if self.logger:
                self.logger.log(f"Duplicate tool registration: {key}")
            raise OnexError(
                message=f"Tool '{key}' is already registered.",
                error_code=RegistryErrorCode.DUPLICATE_TOOL
            )
        self._tools[key] = tool_cls
        if self.logger:
            self.logger.log(f"Registered tool: {key}")

    def get_tool(self, key: str) -> Any:
        """
        Get a tool from the registry by key.
        
        Args:
            key: Tool name/key
            
        Returns:
            Tool class or instance, or None if not found
        """
        tool = self._tools.get(key)
        if tool is None and self.logger:
            self.logger.log(f"Tool not found: {key}")
        return tool

    def list_tools(self) -> Dict[str, Any]:
        """
        List all registered tools.
        
        Returns:
            Dictionary of tool name/key to tool class/instance
        """
        return dict(self._tools)
    
    def get_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """
        Get dependencies required by this registry.
        
        Returns:
            Dictionary mapping tool names to their dependency requirements
        """
        return {
            "event_bus": {
                "required": True,
                "default": "inmemory",
                "description": "Event bus for log event publishing",
            },
            "output_handler": {
                "required": True,
                "default": "context_aware_output_handler",
                "description": "Handler for log output formatting and routing",
            },
            "formatter": {
                "required": True,
                "default": "smart_log_formatter",
                "description": "Formatter for log event presentation",
            }
        }

# Usage: instantiate and inject as needed; do not use singletons. 