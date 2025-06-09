# [ONEX_PROMPT] This is the canonical stub backend selection tool for {NODE_NAME}. Replace all tokens and follow [ONEX_PROMPT] instructions when generating a new node.
from omnibase.protocol.protocol_tool_backend_selection import ToolBackendSelectionProtocol
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry

# [ONEX_PROMPT] Rename and implement this class for your node's backend selection logic if needed.
class StubBackendSelection(ToolBackendSelectionProtocol):
    """
    [ONEX_PROMPT] Document the backend selection logic for {NODE_NAME}. If your node requires a real backend, implement it here.
    Canonical stub for ToolBackendSelectionProtocol.
    This is a placeholder for backend selection logic in the template node.
    Real nodes with backend logic (e.g., Kafka) should implement/inject a real ToolBackendSelection.
    For most nodes, this stub is sufficient and always returns an in-memory event bus for testing/example purposes.
    Requires explicit injection of a registry implementing ProtocolNodeRegistry.
    """
    def __init__(self, registry: ProtocolNodeRegistry):
        self.registry = registry

    def select_event_bus(self, config=None, logger=None):
        # [ONEX_PROMPT] Customize event bus selection logic for {NODE_NAME} if your node requires a real backend.
        tool_cls = self.registry.get_tool('inmemory')
        if tool_cls is not None:
            return tool_cls()
        raise RuntimeError("No 'inmemory' tool available in injected registry.") 