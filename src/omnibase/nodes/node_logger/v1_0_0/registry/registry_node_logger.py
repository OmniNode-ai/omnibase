# === OmniNode:Metadata ===
# author: OmniNode Team
# description: Canonical registry for tools in node_logger
# === /OmniNode:Metadata ===

from typing import Dict, Type, Optional
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.protocol.protocol_tool import ProtocolTool
from omnibase.protocol.protocol_logger import ProtocolLogger
from omnibase.enums.metadata import ToolRegistryModeEnum
from omnibase.core.error_codes import RegistryErrorCode, OnexError
from ..tools.tool_backend_selection import StubBackendSelection
from ..tools.tool_text_format import ToolTextFormat
from ..tools.tool_json_format import ToolJsonFormat
from ..tools.tool_yaml_format import ToolYamlFormat
from ..tools.tool_markdown_format import ToolMarkdownFormat
from ..tools.tool_csv_format import ToolCsvFormat
from ..tools.tool_context_aware_output_handler import ToolContextAwareOutputHandler
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus

class RegistryNodeLogger(ProtocolNodeRegistry):
    """
    Canonical registry for pluggable tools in ONEX logger node.
    Supports ToolCollection-driven construction, standards-compliant error handling, and trace logging.
    """
    def __init__(self, tool_collection: dict = None, mode: ToolRegistryModeEnum = ToolRegistryModeEnum.REAL, logger: Optional[ProtocolLogger] = None):
        self._tools: Dict[str, Type[ProtocolTool]] = {}
        self.mode: ToolRegistryModeEnum = mode
        self.logger: Optional[ProtocolLogger] = logger
        # Late import to avoid circular dependency
        from ..node import NodeLogger
        # Only register default tools if not present in tool_collection
        default_tools = {
            'logger_engine': NodeLogger,
            'backend_selection': lambda: StubBackendSelection(self),
            'inmemory': InMemoryEventBus,
            'text': ToolTextFormat,
            'json': ToolJsonFormat,
            'yaml': ToolYamlFormat,
            'markdown': ToolMarkdownFormat,
            'csv': ToolCsvFormat,
            'context_aware_output_handler': ToolContextAwareOutputHandler,
        }
        tool_collection = tool_collection or {}
        for key, tool_cls in default_tools.items():
            if key not in tool_collection:
                self.register_tool(key, tool_cls)
        for key, tool_cls in tool_collection.items():
            self.register_tool(key, tool_cls)

    def set_mode(self, mode: ToolRegistryModeEnum) -> None:
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
        self.logger = logger

    def register_tool(self, key: str, tool_cls: Type[ProtocolTool]) -> None:
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

    def get_tool(self, key: str) -> Optional[Type[ProtocolTool]]:
        tool = self._tools.get(key)
        if tool is None:
            if self.logger:
                self.logger.log(f"Tool not found: {key}")
            return None
        return tool

    def list_tools(self) -> Dict[str, Type[ProtocolTool]]:
        return dict(self._tools)

# Usage: instantiate and inject as needed; do not use singletons. 