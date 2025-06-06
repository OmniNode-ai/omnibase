# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.622894'
# description: Stamped by PythonHandler
# entrypoint: python://test_event_bus
# hash: ae5c86c0b0be6c18d163a04f959d7213ea1e4110b78ecb9379582dc0a2e4a8bb
# last_modified_at: '2025-05-29T14:14:00.778124+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_event_bus.py
# namespace: python://omnibase.runtimes.onex_runtime.v1_0_0.runtime_tests.test_event_bus
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 71121c46-ee02-4beb-9606-d252bcf49d1b
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Dedicated protocol compliance tests for the ONEX InMemoryEventBus implementation.
Covers publish/subscribe, event order, data integrity, unsubscribe, error handling, and edge cases.
See: omnibase.runtime.events.event_bus_in_memory.InMemoryEventBus
"""

from _pytest.logging import LogCaptureFixture

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum
from omnibase.model.model_onex_event import (
    OnexEvent,
    OnexEventMetadataModel,
    OnexEventTypeEnum,
)
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)


def make_event(
    event_type: OnexEventTypeEnum,
    node_id: str = "test_node",
    metadata: OnexEventMetadataModel | None = None,
) -> OnexEvent:
    return OnexEvent(
        event_type=event_type,
        node_id=node_id,
        metadata=metadata or OnexEventMetadataModel(),
    )


def test_single_subscriber_receives_event() -> None:
    """A single subscriber should receive all published events."""
    bus = InMemoryEventBus()
    emit_log_event_sync(
        LogLevelEnum.DEBUG,
        f"[TEST] test_single_subscriber_receives_event: bus_id={bus.bus_id}",
        event_bus=bus,
    )
    received = []

    def cb(e):
        if e.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
            return
        emit_log_event_sync(
            LogLevelEnum.DEBUG,
            f"[TEST] Subscriber received event: {e.event_type} (bus_id={bus.bus_id})",
            event_bus=bus,
        )
        received.append(e)

    bus.subscribe(cb)
    event = make_event(OnexEventTypeEnum.NODE_START)
    bus.publish(event)
    assert len(received) == 1
    assert received[0].event_type == event.event_type
    assert received[0].node_id == event.node_id
    assert received[0].metadata == event.metadata


def test_multiple_subscribers_receive_event() -> None:
    """All subscribers should receive each published event."""
    bus = InMemoryEventBus()
    received1, received2 = [], []

    def cb1(e):
        if e.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
            return
        received1.append(e)

    def cb2(e):
        if e.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
            return
        received2.append(e)

    bus.subscribe(cb1)
    bus.subscribe(cb2)
    event = make_event(OnexEventTypeEnum.NODE_SUCCESS)
    bus.publish(event)
    assert len(received1) == 1
    assert len(received2) == 1
    assert received1[0].event_type == event.event_type
    assert received2[0].event_type == event.event_type
    assert received1[0].node_id == event.node_id
    assert received2[0].node_id == event.node_id
    assert received1[0].metadata == event.metadata
    assert received2[0].metadata == event.metadata


def test_event_order_is_preserved() -> None:
    """Events should be received in the order they are published."""
    bus = InMemoryEventBus()
    received = []

    def cb(e):
        if e.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
            return
        received.append(e)

    bus.subscribe(cb)
    events = [
        make_event(OnexEventTypeEnum.NODE_START),
        make_event(OnexEventTypeEnum.NODE_SUCCESS),
        make_event(OnexEventTypeEnum.NODE_FAILURE),
    ]
    for event in events:
        bus.publish(event)
    assert [e.event_type for e in received] == [e.event_type for e in events]
    assert [e.node_id for e in received] == [e.node_id for e in events]


def test_event_data_integrity() -> None:
    """Event data (type, metadata) should be preserved through the bus."""
    bus = InMemoryEventBus()
    received = []

    def cb(e):
        if e.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
            return
        received.append(e)

    bus.subscribe(cb)
    event = make_event(
        OnexEventTypeEnum.NODE_SUCCESS, metadata=OnexEventMetadataModel(foo="bar")
    )
    bus.publish(event)
    assert received[0].event_type == OnexEventTypeEnum.NODE_SUCCESS
    assert isinstance(received[0].metadata, OnexEventMetadataModel)
    assert received[0].metadata == OnexEventMetadataModel(foo="bar")


def test_unsubscribe_behavior() -> None:
    """Unsubscribed callbacks should not receive further events (if supported)."""
    bus = InMemoryEventBus()
    received = []

    def cb(e: OnexEvent) -> None:
        if e.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
            return
        received.append(e)

    bus.subscribe(cb)
    bus.unsubscribe(cb)
    bus.publish(make_event(OnexEventTypeEnum.NODE_START))
    # Only STRUCTURED_LOG events may be present, so filter for domain events
    domain_events = [
        e for e in received if e.event_type != OnexEventTypeEnum.STRUCTURED_LOG
    ]
    assert domain_events == []


def test_subscriber_exception_does_not_block_others(caplog: LogCaptureFixture) -> None:
    """Exceptions in one subscriber should not prevent others from receiving events."""
    bus = InMemoryEventBus()
    received = []

    def bad_cb(e: OnexEvent) -> None:
        if e.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
            return
        raise OnexError("fail", CoreErrorCode.OPERATION_FAILED)

    def good_cb(e: OnexEvent) -> None:
        if e.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
            return
        received.append(e)

    bus.subscribe(bad_cb)
    bus.subscribe(good_cb)
    event = make_event(OnexEventTypeEnum.NODE_SUCCESS)
    with caplog.at_level("ERROR"):
        bus.publish(event)
    assert len(received) == 1
    assert received[0].event_type == event.event_type
    assert received[0].node_id == event.node_id
    assert received[0].metadata == event.metadata


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
        if e.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
            return
        received.append("cb1")
        bus.unsubscribe(cb1)
        bus.subscribe(cb2)

    def cb2(e: OnexEvent) -> None:
        if e.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
            return
        received.append("cb2")

    bus.subscribe(cb1)
    event = make_event(OnexEventTypeEnum.NODE_START)
    bus.publish(event)
    # cb1 should run, then cb2 is subscribed but not called for this event
    assert received[0] == "cb1"
    # Next event: only cb2 should run
    bus.publish(make_event(OnexEventTypeEnum.NODE_SUCCESS))
    assert received[1] == "cb2"


# (Optional) Thread safety tests could be added here if required by implementation
