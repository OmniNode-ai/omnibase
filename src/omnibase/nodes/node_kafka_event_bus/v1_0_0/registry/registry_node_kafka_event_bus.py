# === OmniNode:Metadata ===
# author: OmniNode Team
# description: Canonical registry for event bus backends in node_kafka_event_bus
# === /OmniNode:Metadata ===

from typing import Dict, Type, Optional
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.protocol.protocol_tool import ProtocolTool
from omnibase.protocol.protocol_logger import ProtocolLogger
from omnibase.enums.metadata import ToolRegistryModeEnum
from omnibase.core.error_codes import RegistryErrorCode, RegistryErrorModel, OnexError
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from ..tools.tool_kafka_event_bus import KafkaEventBus

class RegistryNodeKafkaEventBus(ProtocolNodeRegistry):
    """
    Canonical registry for pluggable tools in ONEX event bus nodes.
    Use this for registering, looking up, and listing tools (event bus backends, etc.).
    Now supports real/mock mode, trace logging, and standards-compliant error handling.
    """
    def __init__(self, mode: ToolRegistryModeEnum = ToolRegistryModeEnum.REAL, logger: Optional[ProtocolLogger] = None):
        self._tools: Dict[str, Type[ProtocolTool]] = {}
        self.mode: ToolRegistryModeEnum = mode
        self.logger: Optional[ProtocolLogger] = logger

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

    def register_tool(self, name: str, tool_cls: Type[ProtocolTool]) -> None:
        """
        Register a tool by name.
        Args:
            name: Tool name (e.g., 'kafka', 'inmemory')
            tool_cls: Class implementing the tool
        """
        key = name.lower()
        if key in self._tools:
            if self.logger:
                self.logger.log(f"Duplicate tool registration: {name}")
            raise OnexError(
                message=f"Tool '{name}' is already registered.",
                error_code=RegistryErrorCode.DUPLICATE_TOOL
            )
        self._tools[key] = tool_cls
        if self.logger:
            self.logger.log(f"Registered tool: {name}")

    def get_tool(self, name: str) -> Optional[Type[ProtocolTool]]:
        """
        Lookup a tool by name.
        Args:
            name: Tool name
        Returns:
            Tool class if registered, else None
        """
        key = name.lower()
        tool = self._tools.get(key)
        if tool is None:
            if self.logger:
                self.logger.log(f"Tool not found: {name}")
            # Canonical pattern: raise for explicit error paths, return None for optional lookups
            # raise OnexError(message=f"Tool '{name}' not found.", error_code=RegistryErrorCode.TOOL_NOT_FOUND)
            return None
        return tool

    def list_tools(self) -> Dict[str, Type[ProtocolTool]]:
        """
        List all registered tools.
        Returns:
            Dict of tool names to classes
        """
        return dict(self._tools)

# Usage: instantiate and inject as needed; do not use singletons.