# [ONEX_PROMPT] This is the canonical registry implementation for {NODE_NAME}. Replace all tokens and follow [ONEX_PROMPT] instructions when generating a new node.
# [ONEX_PROMPT] All tokens in this file must correspond to fields in ModelTemplateContext. Ensure strong typing for all domain data (use canonical models/enums, never dict/str/list for domain data). File paths must use Path. All ONEX_PROMPT comments must be clear and actionable.
# === OmniNode:Metadata ===
# author: OmniNode Team
# description: Canonical registry for event bus backends in {NODE_NAME}
# === /OmniNode:Metadata ===

from typing import Dict, Type, Optional
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.protocol.protocol_tool import ProtocolTool
from omnibase.protocol.protocol_logger import ProtocolLogger
from omnibase.enums.metadata import ToolRegistryModeEnum
from omnibase.core.error_codes import RegistryErrorCode, RegistryErrorModel, OnexError

# [ONEX_PROMPT] Rename and implement this registry for your node's tool registration and lookup logic.
class Registry{NODE_CLASS}(ProtocolNodeRegistry):
    """
    [ONEX_PROMPT] Document the registry's role and any node-specific tool registration patterns for {NODE_NAME}.
    Canonical registry for pluggable tools in ONEX {NODE_NAME} nodes.
    Use this for registering, looking up, and listing tools (formatters, handlers, etc.).
    Now supports real/mock mode, trace logging, and standards-compliant error handling.
    """
    def __init__(self, mode: ToolRegistryModeEnum = ToolRegistryModeEnum.REAL, logger: Optional[ProtocolLogger] = None, tool_collection: Optional[dict] = None):
        self._tools: Dict[str, Type[ProtocolTool]] = {}
        self.mode: ToolRegistryModeEnum = mode
        self.logger: Optional[ProtocolLogger] = logger
        # Scenario-driven registry injection: register all tools from tool_collection if provided
        if tool_collection is not None:
            for name, tool_cls in tool_collection.items():
                self.register_tool(name, tool_cls)

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
        Register a tool by canonical key (e.g., BACKEND_SELECTION_KEY).
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
        List all registered tools.
        Returns:
            Dict of tool names to classes
        """
        return dict(self._tools)

# Usage: instantiate and inject as needed; do not use singletons. 