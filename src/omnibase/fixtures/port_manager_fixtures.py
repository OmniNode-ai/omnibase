import pytest

from omnibase.nodes.node_registry_node.v1_0_0.port_manager import PortManager
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)


@pytest.fixture
def event_bus():
    """
    Shared fixture for an in-memory event bus for event-driven tests.
    Use this fixture in any test that needs a protocol-pure event bus instance.
    """
    return InMemoryEventBus()


@pytest.fixture
def port_manager(event_bus):
    """
    Shared fixture for a PortManager instance with injected event bus.
    Use this fixture in any test that needs registry-driven port allocation.
    """
    return PortManager(event_bus=event_bus)
