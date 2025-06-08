from typing import Protocol, Type, Optional, Dict, Any

class ProtocolNodeRegistry(Protocol):
    """
    Protocol for node-local tool registries in ONEX nodes.
    Use this for registering, looking up, and listing pluggable tools (formatters, backends, handlers, etc.).
    Extend this protocol in your node if you need to support additional tool types or metadata.
    """
    def register_tool(self, name: str, tool_cls: Type[Any]) -> None: ...
    def get_tool(self, name: str) -> Optional[Type[Any]]: ...
    def list_tools(self) -> Dict[str, Type[Any]]: ... 