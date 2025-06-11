from omnibase.registry.base_registry import BaseOnexRegistry
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_factory import get_event_bus
from omnibase.nodes.node_manager.v1_0_0.tools import tool_cli_commands
from omnibase.model.model_event_bus_config import ModelEventBusConfig

class CliRegistry(BaseOnexRegistry):
    """
    Canonical registry for ONEX CLI tools, commands, and event bus.
    """
    def __init__(self, event_bus_type: str = "inmemory", node_dir: str = "cli"):
        super().__init__(node_dir=node_dir)
        # Register event bus (in-memory or Kafka)
        if event_bus_type == "kafka":
            from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.sync_kafka_event_bus import SyncKafkaEventBus
            config = ModelEventBusConfig.default()
            self._event_bus = SyncKafkaEventBus(config)
        else:
            self._event_bus = InMemoryEventBus()
        # Optionally register the event bus as a tool
        # self.register_tool('event_bus', self._event_bus)
        # Register CLI tools/commands
        self.register_tool("cli_parity_validate", tool_cli_commands.cli_parity_validate)
        self.register_tool("cli_static_typing_enforce", tool_cli_commands.cli_static_typing_enforce)
        # Add more CLI tools/commands as needed

    def get_event_bus(self):
        return self._event_bus

    def has_tool(self, key: str) -> bool:
        return key in self._tools 