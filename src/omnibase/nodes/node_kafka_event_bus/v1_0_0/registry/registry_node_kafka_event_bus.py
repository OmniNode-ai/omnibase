# === OmniNode:Metadata ===
# author: OmniNode Team
# description: Canonical registry for event bus backends in node_kafka_event_bus
# === /OmniNode:Metadata ===

from typing import Dict, Type, Optional, Any
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from ..tools.tool_kafka_event_bus import KafkaEventBus

class RegistryNodeKafkaEventBus(ProtocolNodeRegistry):
    """
    Canonical registry for pluggable tools in ONEX event bus nodes.
    Use this for registering, looking up, and listing tools (event bus backends, etc.).
    Extend as needed for node-specific tool types or metadata.
    """
    def __init__(self):
        self._tools: Dict[str, Type[Any]] = {}

    def register_tool(self, name: str, tool_cls: Type[Any]) -> None:
        """
        Register a tool by name.
        Args:
            name: Tool name (e.g., 'kafka', 'inmemory')
            tool_cls: Class implementing the tool
        """
        self._tools[name.lower()] = tool_cls

    def get_tool(self, name: str) -> Optional[Type[Any]]:
        """
        Lookup a tool by name.
        Args:
            name: Tool name
        Returns:
            Tool class if registered, else None
        """
        return self._tools.get(name.lower())

    def list_tools(self) -> Dict[str, Type[Any]]:
        """
        List all registered tools.
        Returns:
            Dict of tool names to classes
        """
        return dict(self._tools)

# Usage: instantiate and inject as needed; do not use singletons.

# (Removed: initialize_registry_node_kafka_event_bus and registry_node_kafka_event_bus singleton) 