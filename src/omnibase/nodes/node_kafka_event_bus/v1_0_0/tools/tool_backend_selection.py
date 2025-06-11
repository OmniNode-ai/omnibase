from omnibase.enums.log_level import LogLevelEnum
from omnibase.protocol.protocol_tool_backend_selection import (
    ToolBackendSelectionProtocol,
)
from omnibase.model.model_event_bus_config import ModelEventBusConfig
from omnibase.protocol.protocol_event_bus import ProtocolEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import (
    emit_log_event_sync,
    make_log_context,
)
from omnibase.mixin.mixin_node_id_from_contract import MixinNodeIdFromContract
from pathlib import Path
from omnibase.protocol.protocol_node_registry import ProtocolNodeRegistry
from omnibase.core.core_errors import OnexError
from ..error_codes import NodeKafkaEventBusNodeErrorCode

class ToolBackendSelection(ToolBackendSelectionProtocol, MixinNodeIdFromContract):
    """
    Protocol-compliant tool for selecting and instantiating the event bus backend (Kafka or InMemory).
    Requires explicit injection of a registry implementing ProtocolNodeRegistry.
    Accepts a strongly-typed ModelEventBusConfig and returns a ProtocolEventBus instance.
    Emits log events for backend selection and degraded mode.
    """
    def __init__(self, registry: ProtocolNodeRegistry):
        self.registry = registry

    def select_event_bus(
        self, config: ModelEventBusConfig = None, logger=None
    ) -> ProtocolEventBus:
        node_id = self._load_node_id()
        backend_name = 'kafka' if config is not None else 'inmemory'
        tool_cls = self.registry.get_tool(backend_name)
        if tool_cls is not None and config is not None:
            try:
                bus = tool_cls(config)
                emit_log_event_sync(
                    LogLevelEnum.INFO,
                    f"[tool_backend_selection] Using {backend_name.capitalize()}EventBus backend via injected registry.",
                    make_log_context(node_id=node_id),
                )
                return bus
            except Exception as e:
                emit_log_event_sync(
                    LogLevelEnum.WARNING,
                    f"[tool_backend_selection] Failed to instantiate {backend_name.capitalize()}EventBus: {e}. Falling back to InMemoryEventBus.",
                    make_log_context(node_id=node_id),
                )
        # Fallback to InMemoryEventBus
        fallback_cls = self.registry.get_tool('inmemory')
        if fallback_cls is not None:
            emit_log_event_sync(
                LogLevelEnum.INFO,
                "[tool_backend_selection] Using InMemoryEventBus backend via injected registry.",
                make_log_context(node_id=node_id),
            )
            return fallback_cls()
        raise OnexError(NodeKafkaEventBusNodeErrorCode.BACKEND_UNAVAILABLE, "No 'inmemory' tool available in injected registry.")

    def _get_node_dir(self):
        import inspect
        import os
        module = inspect.getmodule(self)
        node_file = Path(module.__file__)
        if node_file.parent.name == "tools":
            node_dir = node_file.parent.parent
        else:
            node_dir = node_file.parent

        return node_dir
