import pytest
from pydantic import ValidationError

from omnibase.nodes.stamper_node.src.main import (
    StamperInputState,
    StamperOutputState,
    run_stamper_node,
)
from omnibase.model.model_onex_event import OnexEventTypeEnum
from omnibase.runtime.events.event_bus_in_memory import InMemoryEventBus


# Canonical ONEX fixture-injected, protocol-first test (see docs/testing.md)
@pytest.fixture
def input_state():
    # In-memory, context-agnostic input (no real file path)
    return StamperInputState(file_path="mock/path.yaml", author="TestUser", version="0.1.0")


@pytest.mark.node
def test_run_stamper_node_stub(input_state):
    output = run_stamper_node(input_state)
    assert isinstance(output, StamperOutputState)
    assert output.status == "success"
    assert "mock/path.yaml" in output.message
    assert "TestUser" in output.message


def test_event_emission_success(input_state):
    events = []
    event_bus = InMemoryEventBus()
    event_bus.subscribe(lambda e: events.append(e))
    output = run_stamper_node(input_state, event_bus=event_bus)
    event_types = [e.event_type for e in events]
    assert event_types == [OnexEventTypeEnum.NODE_START, OnexEventTypeEnum.NODE_SUCCESS]
    assert events[0].metadata["input_state"]["file_path"] == input_state.file_path
    assert events[1].metadata["output_state"]["status"] == "success"


def test_event_emission_failure(input_state, monkeypatch):
    # Patch run_stamper_node to raise inside the try block
    def broken_run(input_state, event_bus=None):
        if event_bus is None:
            event_bus = InMemoryEventBus()
        node_id = "stamper_node"
        event_bus.publish(type("Dummy", (), {"event_type": OnexEventTypeEnum.NODE_START, "node_id": node_id, "metadata": {}})())
        raise RuntimeError("Simulated failure")
    # Use the real function but patch the output logic to raise
    events = []
    event_bus = InMemoryEventBus()
    event_bus.subscribe(lambda e: events.append(e))
    # Patch the output creation to raise
    def fail_output(*args, **kwargs):
        raise RuntimeError("Simulated failure")
    monkeypatch.setattr("omnibase.nodes.stamper_node.src.main.StamperOutputState", fail_output)
    with pytest.raises(RuntimeError, match="Simulated failure"):
        run_stamper_node(input_state, event_bus=event_bus)
    event_types = [e.event_type for e in events]
    assert event_types[0] == OnexEventTypeEnum.NODE_START
    assert event_types[-1] == OnexEventTypeEnum.NODE_FAILURE


# TODO: Integrate protocol registry and context-parametrized fixture per docs/testing.md

# TODO: Add more comprehensive tests after real logic is migrated
