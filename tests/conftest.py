import pytest

@pytest.fixture(scope="session")
def protocol_event_bus():
    """
    Canonical protocol-pure event bus fixture for all tests requiring emit_log_event.
    Use this fixture in any test that calls emit_log_event or requires protocol-pure logging.
    """
    from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
    yield InMemoryEventBus() 