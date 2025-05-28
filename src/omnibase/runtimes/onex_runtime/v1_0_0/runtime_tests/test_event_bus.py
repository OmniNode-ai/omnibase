# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_event_bus.py
# version: 1.0.0
# uuid: 71121c46-ee02-4beb-9606-d252bcf49d1b
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.622894
# last_modified_at: 2025-05-28T17:20:05.302714
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 597b1a724b45697e75816cba2749277d8f2912cca279709c8015e8d2d3071dfe
# entrypoint: python@test_event_bus.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.test_event_bus
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Dedicated protocol compliance tests for the ONEX InMemoryEventBus implementation.
Covers publish/subscribe, event order, data integrity, unsubscribe, error handling, and edge cases.
See: omnibase.runtime.events.event_bus_in_memory.InMemoryEventBus
"""

from _pytest.logging import LogCaptureFixture

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)


def make_event(
    event_type: OnexEventTypeEnum,
    node_id: str = "test_node",
    metadata: dict | None = None,
) -> OnexEvent:
    return OnexEvent(event_type=event_type, node_id=node_id, metadata=metadata or {})


def test_single_subscriber_receives_event() -> None:
    """A single subscriber should receive all published events."""
    bus = InMemoryEventBus()
    received = []
    bus.subscribe(lambda e: received.append(e))
    event = make_event(OnexEventTypeEnum.NODE_START)
    bus.publish(event)
    assert received == [event]


def test_multiple_subscribers_receive_event() -> None:
    """All subscribers should receive each published event."""
    bus = InMemoryEventBus()
    received1, received2 = [], []
    bus.subscribe(lambda e: received1.append(e))
    bus.subscribe(lambda e: received2.append(e))
    event = make_event(OnexEventTypeEnum.NODE_SUCCESS)
    bus.publish(event)
    assert received1 == [event]
    assert received2 == [event]


def test_event_order_is_preserved() -> None:
    """Events should be received in the order they are published."""
    bus = InMemoryEventBus()
    received = []
    bus.subscribe(lambda e: received.append(e))
    events = [
        make_event(OnexEventTypeEnum.NODE_START),
        make_event(OnexEventTypeEnum.NODE_SUCCESS),
        make_event(OnexEventTypeEnum.NODE_FAILURE),
    ]
    for event in events:
        bus.publish(event)
    assert received == events


def test_event_data_integrity() -> None:
    """Event data (type, metadata) should be preserved through the bus."""
    bus = InMemoryEventBus()
    received = []
    bus.subscribe(lambda e: received.append(e))
    event = make_event(OnexEventTypeEnum.NODE_SUCCESS, metadata={"foo": "bar"})
    bus.publish(event)
    assert received[0].event_type == OnexEventTypeEnum.NODE_SUCCESS
    assert isinstance(received[0].metadata, dict)
    assert received[0].metadata["foo"] == "bar"


def test_unsubscribe_behavior() -> None:
    """Unsubscribed callbacks should not receive further events (if supported)."""
    bus = InMemoryEventBus()
    received = []

    def cb(e: OnexEvent) -> None:
        received.append(e)

    bus.subscribe(cb)
    bus.unsubscribe(cb)
    bus.publish(make_event(OnexEventTypeEnum.NODE_START))
    assert received == []


def test_subscriber_exception_does_not_block_others(caplog: LogCaptureFixture) -> None:
    """Exceptions in one subscriber should not prevent others from receiving events."""
    bus = InMemoryEventBus()
    received = []

    def bad_cb(e: OnexEvent) -> None:
        raise OnexError("fail", CoreErrorCode.OPERATION_FAILED)

    def good_cb(e: OnexEvent) -> None:
        received.append(e)

    bus.subscribe(bad_cb)
    bus.subscribe(good_cb)
    event = make_event(OnexEventTypeEnum.NODE_SUCCESS)
    with caplog.at_level("ERROR"):
        bus.publish(event)
    assert received == [event]
    assert any("EventBus subscriber error" in r for r in caplog.text.splitlines())


def test_publish_with_no_subscribers() -> None:
    """Publishing with no subscribers should not error."""
    bus = InMemoryEventBus()
    event = make_event(OnexEventTypeEnum.NODE_START)
    # Should not raise
    bus.publish(event)


def test_subscribe_unsubscribe_during_publish() -> None:
    """Subscribing/unsubscribing during event emission should not cause errors (if supported)."""
    bus = InMemoryEventBus()
    received = []

    def cb1(e: OnexEvent) -> None:
        received.append("cb1")
        bus.unsubscribe(cb1)
        bus.subscribe(cb2)

    def cb2(e: OnexEvent) -> None:
        received.append("cb2")

    bus.subscribe(cb1)
    event = make_event(OnexEventTypeEnum.NODE_START)
    bus.publish(event)
    # cb1 should run, then cb2 is subscribed but not called for this event
    assert received == ["cb1"]
    # Next event: only cb2 should run
    bus.publish(make_event(OnexEventTypeEnum.NODE_SUCCESS))
    assert received == ["cb1", "cb2"]


# (Optional) Thread safety tests could be added here if required by implementation
