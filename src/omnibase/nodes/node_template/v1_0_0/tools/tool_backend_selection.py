from omnibase.protocol.protocol_tool_backend_selection import ToolBackendSelectionProtocol
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus

class StubBackendSelection(ToolBackendSelectionProtocol):
    """
    Canonical stub for ToolBackendSelectionProtocol.
    This is a placeholder for backend selection logic in the template node.
    Real nodes with backend logic (e.g., Kafka) should implement/inject a real backend selection tool.
    For most nodes, this stub is sufficient and always returns an in-memory event bus for testing/example purposes.
    """
    def select_event_bus(self, config=None, logger=None):
        return InMemoryEventBus()

# Singleton instance for import in tests/fixtures
stub_backend_selection = StubBackendSelection() 