# === OmniNode:Metadata ===
# author: OmniNode Team
# description: Canonical registry for event bus backends in node_kafka_event_bus
# === /OmniNode:Metadata ===

from typing import Dict, Type, Optional
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.protocol.protocol_tool import ProtocolTool
from omnibase.protocol.protocol_logger import ProtocolLogger
from omnibase.enums.metadata import ToolRegistryModeEnum
from omnibase.core.core_errors import RegistryErrorCode, RegistryErrorModel, OnexError
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from ..tools.tool_kafka_event_bus import KafkaEventBus
from omnibase.constants import BOOTSTRAP_KEY, BACKEND_SELECTION_KEY, HEALTH_CHECK_KEY, INPUT_VALIDATION_KEY, OUTPUT_FIELD_KEY, CLI_COMMANDS_KEY
from ..tools.tool_cli_commands import ToolCliCommands
from omnibase.runtimes.onex_runtime.v1_0_0.protocols.protocol_metadata_loader import ProtocolMetadataLoader
from pathlib import Path
from omnibase.registry.base_registry import BaseOnexRegistry
from omnibase.nodes.node_logger.v1_0_0.tools.tool_logger_emit_log_event import ToolLoggerEmitLogEvent

# Context-aware factory for metadata loader
def make_metadata_loader_lambda(node_dir):
    from omnibase.runtimes.onex_runtime.v1_0_0.tools.metadata_loader_tool import ToolMetadataLoader
    return lambda: ToolMetadataLoader()
make_metadata_loader_lambda._is_context_factory = True

class RegistryKafkaEventBus(BaseOnexRegistry):
    """
    Canonical registry for pluggable tools in ONEX event bus nodes.
    Now supports ToolCollection-driven construction, standards-compliant error handling, and trace logging.
    """
    CANONICAL_TOOLS = {
        CLI_COMMANDS_KEY: ToolCliCommands,
        'kafka': KafkaEventBus,
        'inmemory': InMemoryEventBus,
        'METADATA_LOADER': make_metadata_loader_lambda,
        'tool_logger_emit_log_event': ToolLoggerEmitLogEvent,  # Protocol-compliant logger tool
    }

    def __init__(self, node_dir, tool_collection: dict = None, mode: ToolRegistryModeEnum = ToolRegistryModeEnum.REAL, logger: Optional[ProtocolLogger] = None):
        super().__init__(node_dir, tool_collection, mode, logger)
        if self.logger:
            self.logger.log(f"[RegistryKafkaEventBus] Registered tools: {list(self._tools.keys())}")

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
        """
        Register a tool by canonical key (e.g., BOOTSTRAP_KEY, BACKEND_SELECTION_KEY).
        Args:
            key: Canonical tool key constant
            tool_cls: Class implementing the tool
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

    def get_tool(self, key: str) -> Optional[Type[ProtocolTool]]:
        """
        Lookup a tool by canonical key.
        Args:
            key: Canonical tool key constant
        Returns:
            Tool class if registered, else None
        """
        tool = self._tools.get(key)
        if tool is None:
            if self.logger:
                self.logger.log(f"Tool not found: {key}")
            return None
        return tool

    def list_tools(self) -> Dict[str, Type[ProtocolTool]]:
        """
        List all registered tools by canonical key.
        Returns:
            Dict of canonical tool keys to classes
        """
        return dict(self._tools)

# Usage: instantiate and inject as needed; do not use singletons.