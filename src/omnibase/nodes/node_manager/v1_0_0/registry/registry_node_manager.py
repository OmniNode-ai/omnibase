# === OmniNode:Metadata ===
# author: OmniNode Team
# description: Canonical registry for event bus backends in node_template
# === /OmniNode:Metadata ===

from typing import Dict, Type, Optional
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.protocol.protocol_tool import ProtocolTool
from omnibase.protocol.protocol_logger import ProtocolLogger
from omnibase.enums.metadata import ToolRegistryModeEnum
from omnibase.core.error_codes import RegistryErrorCode, RegistryErrorModel, OnexError
from omnibase.nodes.node_manager.v1_0_0.tools.tool_contract_to_model import ToolContractToModel
from omnibase.nodes.node_manager.v1_0_0.tools.tool_backend_selection import StubBackendSelection
from omnibase.nodes.node_manager.v1_0_0.tools.tool_maintenance import ToolMaintenance
from omnibase.nodes.node_manager.v1_0_0.tools.tool_validation_engine import ToolValidationEngine
from omnibase.nodes.node_manager.v1_0_0.tools.tool_template_engine import ToolTemplateEngine
from omnibase.nodes.node_manager.v1_0_0.tools.tool_cli_commands import ToolCliCommands
from omnibase.nodes.node_manager.v1_0_0.tools.tool_file_generator import ToolFileGenerator

TOOL_KEYS = {
    "CONTRACT_TO_MODEL": ToolContractToModel,
    "BACKEND_SELECTION": StubBackendSelection,
    "MAINTENANCE": ToolMaintenance,
    "VALIDATION_ENGINE": ToolValidationEngine,
    "TEMPLATE_ENGINE": ToolTemplateEngine,
    "CLI_COMMANDS": ToolCliCommands,
    "FILE_GENERATOR": ToolFileGenerator,
}

class RegistryNodeManager(ProtocolNodeRegistry):
    """
    Canonical registry for pluggable tools in node_manager node.
    Compatible with scenario harness and supports tool_collection injection.
    """
    def __init__(self, tool_collection: Optional[dict] = None, logger: Optional[ProtocolLogger] = None, mode: ToolRegistryModeEnum = ToolRegistryModeEnum.REAL):
        self._tools: Dict[str, Type[ProtocolTool]] = {}
        self.mode: ToolRegistryModeEnum = mode
        self.logger: Optional[ProtocolLogger] = logger
        if tool_collection is not None:
            for name, tool_cls in tool_collection.items():
                self.register_tool(name, tool_cls)
        else:
            for name, tool_cls in TOOL_KEYS.items():
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