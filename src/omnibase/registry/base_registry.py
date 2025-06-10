from typing import Dict, Any
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry

class BaseOnexRegistry(ProtocolNodeRegistry):
    """
    Canonical ONEX base registry for all node registries.
    - Always registers/overwrites all tools in CANONICAL_TOOLS after any custom tool_collection.
    - For context-aware tools (e.g., METADATA_LOADER), CANONICAL_TOOLS should provide a factory that takes node_dir.
    - Child registries should set CANONICAL_TOOLS as a class variable.
    """
    CANONICAL_TOOLS: Dict[str, Any] = {}

    def __init__(self, node_dir, tool_collection: dict = None, mode=None, logger=None, **kwargs):
        self.node_dir = node_dir
        self.mode = mode
        self.logger = logger
        self._tools: Dict[str, Any] = {}
        if tool_collection:
            for key, tool_cls in tool_collection.items():
                self.register_tool(key, tool_cls)
        for key, tool in self.CANONICAL_TOOLS.items():
            if callable(tool) and getattr(tool, '_is_context_factory', False):
                self._tools[key] = tool(self.node_dir)
            else:
                self._tools[key] = tool

    def register_tool(self, key: str, tool_cls: Any) -> None:
        self._tools[key] = tool_cls

    def get_tool(self, key: str) -> Any:
        return self._tools.get(key)

    def list_tools(self) -> Dict[str, Any]:
        return dict(self._tools)

# Usage in child registry:
# class RegistryKafkaEventBus(BaseOnexRegistry):
#     CANONICAL_TOOLS = {
#         'CLI_COMMANDS': ToolCliCommands,
#         'METADATA_LOADER': make_metadata_loader_lambda,  # must set _is_context_factory = True
#     }
#
# def make_metadata_loader_lambda(node_dir):
#     ...
# make_metadata_loader_lambda._is_context_factory = True 