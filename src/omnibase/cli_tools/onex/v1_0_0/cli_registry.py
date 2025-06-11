from omnibase.registry.base_registry import BaseOnexRegistry
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.nodes.node_manager.v1_0_0.tools import tool_cli_commands
from omnibase.model.model_event_bus_config import ModelEventBusConfig
from omnibase.enums import LogLevelEnum
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import KafkaEventBus

class CliRegistry(BaseOnexRegistry):
    """
    Canonical registry for ONEX CLI tools, commands, and event bus.
    """
    def __init__(self, event_bus_type: str = "inmemory", node_dir: str = "cli"):
        super().__init__(node_dir=node_dir)
        config = ModelEventBusConfig.default()
        if event_bus_type == "kafka":
            self._event_bus = KafkaEventBus(config)
            emit_log_event_sync(LogLevelEnum.INFO, "[CliRegistry] Using async KafkaEventBus for CLI", node_id="cli_registry")
        else:
            self._event_bus = InMemoryEventBus()
            emit_log_event_sync(LogLevelEnum.INFO, "[CliRegistry] Using InMemoryEventBus for CLI", node_id="cli_registry")
        # Register CLI tools/commands
        self.register_tool("cli_parity_validate", tool_cli_commands.cli_parity_validate)
        self.register_tool("cli_static_typing_enforce", tool_cli_commands.cli_static_typing_enforce)
        # self.register_tool("node_kafka_event_bus", ...)  # REMOVE or COMMENT OUT any such line
        # Add more CLI tools/commands as needed

    def get_event_bus(self):
        return self._event_bus

    def has_tool(self, key: str) -> bool:
        return key in self._tools 