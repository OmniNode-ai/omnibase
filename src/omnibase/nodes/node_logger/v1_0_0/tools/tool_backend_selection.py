from omnibase.protocol.protocol_tool_backend_selection import ToolBackendSelectionProtocol
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.core.errors import OnexError
from ..error_codes import NodeLoggerNodeErrorCode

class StubBackendSelection(ToolBackendSelectionProtocol):
    """
    Canonical stub for ToolBackendSelectionProtocol.
    This is a placeholder for backend selection logic in the logger node.
    Real nodes with backend logic (e.g., Kafka) should implement/inject a real backend selection tool.
    For most nodes, this stub is sufficient and always returns an in-memory event bus for testing/example purposes.
    Requires explicit injection of a registry implementing ProtocolNodeRegistry.
    """
    def __init__(self, registry: ProtocolNodeRegistry):
        self.registry = registry

    def select_event_bus(self, config=None, logger=None):
        tool_cls = self.registry.get_tool('inmemory')
        if tool_cls is not None:
            return tool_cls()
        raise OnexError(NodeLoggerNodeErrorCode.BACKEND_UNAVAILABLE, "No 'inmemory' tool available in injected registry.") 