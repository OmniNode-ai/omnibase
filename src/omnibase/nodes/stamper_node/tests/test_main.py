import pytest

from omnibase.model.model_onex_event import OnexEventTypeEnum
from omnibase.nodes.stamper_node.main import run_stamper_node
from omnibase.nodes.stamper_node.models.state import (
    StamperInputState,
    StamperOutputState,
)
from omnibase.runtime.events.event_bus_in_memory import InMemoryEventBus

# Register the custom mark to avoid PytestUnknownMarkWarning
pytestmark = pytest.mark.node


# Canonical ONEX fixture-injected, protocol-first test (see docs/testing.md)
@pytest.fixture
def input_state() -> StamperInputState:
    # In-memory, context-agnostic input (no real file path)
    return StamperInputState(
        file_path="mock/path.yaml", author="TestUser", version="0.1.0"
    )


@pytest.mark.node
def test_run_stamper_node_stub(input_state: StamperInputState) -> None:
    result = run_stamper_node(input_state)
    assert isinstance(result, StamperOutputState)
    assert result.status == "success"
    assert "mock/path.yaml" in result.message
    assert "TestUser" in result.message


def test_event_emission_success(input_state: StamperInputState) -> None:
    events = []
    event_bus = InMemoryEventBus()
    event_bus.subscribe(lambda e: events.append(e))
    run_stamper_node(input_state, event_bus=event_bus)
    event_types = [e.event_type for e in events]
    assert event_types == [OnexEventTypeEnum.NODE_START, OnexEventTypeEnum.NODE_SUCCESS]
    assert (
        events[0].metadata is not None
        and events[0].metadata["input_state"]["file_path"] == input_state.file_path
    )
    assert (
        events[1].metadata is not None
        and events[1].metadata["output_state"]["status"] == "success"
    )


def test_event_emission_failure(
    input_state: StamperInputState, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Patch run_stamper_node to raise inside the try block
    def fail_output(*args: object, **kwargs: object) -> None:
        raise RuntimeError("Simulated failure")

    events = []
    event_bus = InMemoryEventBus()
    event_bus.subscribe(lambda e: events.append(e))

    monkeypatch.setattr(
        "omnibase.nodes.stamper_node.main.StamperOutputState", fail_output
    )
    with pytest.raises(RuntimeError, match="Simulated failure"):
        run_stamper_node(input_state, event_bus=event_bus)
    event_types = [e.event_type for e in events]
    assert event_types[0] == OnexEventTypeEnum.NODE_START
    assert event_types[-1] == OnexEventTypeEnum.NODE_FAILURE


# TODO: Integrate protocol registry and context-parametrized fixture per docs/testing.md
# TODO: Add more comprehensive tests after real logic is migrated
