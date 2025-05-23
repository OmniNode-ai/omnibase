# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_event_bus.py
# version: 1.0.0
# uuid: 9df0b473-7c37-48f4-8d0a-2c2f0a98a0b8
# author: OmniNode Team
# created_at: 2025-05-23T13:39:32.036013
# last_modified_at: 2025-05-23T17:42:52.028338
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a9e062662c21839b6a52bd6de1bf5dffffaa003beaaae26f8460214a1abcce07
# entrypoint: python@test_event_bus.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_event_bus
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Dedicated protocol compliance tests for the ONEX InMemoryEventBus implementation.
Covers publish/subscribe, event order, data integrity, unsubscribe, error handling, and edge cases.
See: omnibase.runtime.events.event_bus_in_memory.InMemoryEventBus
"""

from _pytest.logging import LogCaptureFixture

from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.runtime.events.event_bus_in_memory import InMemoryEventBus


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
        raise RuntimeError("fail")

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
