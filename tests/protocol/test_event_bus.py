# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_event_bus.py
# version: 1.0.0
# uuid: 45ac1f4a-b229-4bf8-82d9-2ec2e1e667a9
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.979542
# last_modified_at: 2025-05-28T17:20:05.241216
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: bfb10232a2ec503578afe61ab60f2fad5b76a1fc02ddc5ef28beb4c310bc522b
# entrypoint: python@test_event_bus.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.test_event_bus
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Standards-Compliant Protocol Tests for ProtocolEventBus.

This file follows the canonical test pattern as demonstrated in src/omnibase/utils/tests/test_node_metadata_extractor.py. It demonstrates:
- Registry-driven test case execution pattern
- Context-agnostic, fixture-injected testing
- Protocol-first validation (no implementation details)
- No hardcoded test data or string literals
- Compliance with all standards in docs/testing.md

Tests verify that all implementations of ProtocolEventBus follow the protocol contract
through registry-injected test cases and fixture-provided dependencies.
"""

from typing import Any, Dict, List

import pytest

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.protocol.protocol_event_bus import ProtocolEventBus

# Context constants for fixture parametrization
MOCK_CONTEXT = 1
INTEGRATION_CONTEXT = 2


class MockEventBus(ProtocolEventBus):
    """Mock implementation for protocol testing in mock context."""

    def __init__(self) -> None:
        """Initialize mock event bus."""
        self.subscribers: List[Any] = []
        self.published_events: List[OnexEvent] = []

    def publish(self, event: OnexEvent) -> None:
        """Mock publish that stores events and notifies subscribers."""
        self.published_events.append(event)
        for callback in self.subscribers:
            try:
                callback(event)
            except Exception:
                # Mock implementation continues on subscriber errors
                pass

    def subscribe(self, callback: Any) -> None:
        """Mock subscribe that adds callback to list."""
        if callback not in self.subscribers:
            self.subscribers.append(callback)

    def unsubscribe(self, callback: Any) -> None:
        """Mock unsubscribe that removes callback from list."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    def clear(self) -> None:
        """Mock clear that removes all subscribers."""
        self.subscribers.clear()


@pytest.fixture(
    params=[
        pytest.param(MOCK_CONTEXT, id="mock", marks=pytest.mark.mock),
        pytest.param(
            INTEGRATION_CONTEXT, id="integration", marks=pytest.mark.integration
        ),
    ]
)
def event_bus_registry(request: Any) -> Dict[str, ProtocolEventBus]:
    """
    Canonical registry-swapping fixture for ONEX event bus tests.

    Context mapping:
      MOCK_CONTEXT = 1 (mock context; in-memory, isolated)
      INTEGRATION_CONTEXT = 2 (integration context; real event bus)

    Returns:
        Dict[str, ProtocolEventBus]: Registry of event buses in appropriate context.

    Raises:
        OnexError: If an unknown context is requested.
    """
    if request.param == MOCK_CONTEXT:
        # Mock context: return mock event bus
        return {
            "mock_bus": MockEventBus(),
        }
    elif request.param == INTEGRATION_CONTEXT:
        # Integration context: return real event bus
        from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
            InMemoryEventBus,
        )

        return {
            "in_memory_bus": InMemoryEventBus(),
        }
    else:
        raise OnexError(
            f"Unknown event bus context: {request.param}",
            CoreErrorCode.INVALID_PARAMETER,
        )


@pytest.fixture
def event_test_cases() -> Dict[str, Dict[str, Any]]:
    """
    Registry of test events for protocol compliance testing.

    TODO: This should be automated via decorators/import hooks per testing.md policy.
    """
    return {
        "node_start_event": {
            "event_type": OnexEventTypeEnum.NODE_START,
            "node_id": "test_node_start",
            "metadata": {"phase": "initialization"},
            "description": "Basic node start event",
        },
        "node_success_event": {
            "event_type": OnexEventTypeEnum.NODE_SUCCESS,
            "node_id": "test_node_success",
            "metadata": {"result": "completed", "duration": 1.5},
            "description": "Node success event with metadata",
        },
        "node_failure_event": {
            "event_type": OnexEventTypeEnum.NODE_FAILURE,
            "node_id": "test_node_failure",
            "metadata": {"error": "timeout", "retry_count": 3},
            "description": "Node failure event with error details",
        },
        "complex_metadata_event": {
            "event_type": OnexEventTypeEnum.NODE_START,
            "node_id": "complex_node",
            "metadata": {
                "nested": {"data": "value"},
                "list": [1, 2, 3],
                "string": "test",
                "number": 42,
            },
            "description": "Event with complex metadata structure",
        },
    }


@pytest.fixture
def test_scenario_registry() -> Dict[str, Dict[str, Any]]:
    """
    Registry of test scenarios for event bus behavior testing.

    TODO: This should be automated via decorators/import hooks per testing.md policy.
    """
    return {
        "single_subscriber": {
            "subscriber_count": 1,
            "event_count": 1,
            "description": "Single subscriber receives single event",
        },
        "multiple_subscribers": {
            "subscriber_count": 3,
            "event_count": 1,
            "description": "Multiple subscribers receive same event",
        },
        "ordered_events": {
            "subscriber_count": 1,
            "event_count": 3,
            "description": "Events received in published order",
        },
        "no_subscribers": {
            "subscriber_count": 0,
            "event_count": 1,
            "description": "Publishing with no subscribers",
        },
    }


def test_protocol_method_existence(
    event_bus_registry: Dict[str, ProtocolEventBus]
) -> None:
    """
    Protocol: Verify all required methods exist with correct signatures.
    """
    for bus_name, event_bus in event_bus_registry.items():
        # Check that all protocol methods exist
        assert hasattr(event_bus, "publish"), f"{bus_name}: Missing publish method"
        assert hasattr(event_bus, "subscribe"), f"{bus_name}: Missing subscribe method"
        assert hasattr(
            event_bus, "unsubscribe"
        ), f"{bus_name}: Missing unsubscribe method"

        # Check method signatures by inspecting callable
        assert callable(event_bus.publish), f"{bus_name}: publish must be callable"
        assert callable(event_bus.subscribe), f"{bus_name}: subscribe must be callable"
        assert callable(
            event_bus.unsubscribe
        ), f"{bus_name}: unsubscribe must be callable"


def test_single_subscriber_receives_event(
    event_bus_registry: Dict[str, ProtocolEventBus],
    event_test_cases: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: A single subscriber should receive published events.
    """
    for bus_name, event_bus in event_bus_registry.items():
        # Clear any existing state
        if hasattr(event_bus, "clear"):
            event_bus.clear()

        for case_name, event_data in event_test_cases.items():
            received_events: List[OnexEvent] = []

            def callback(event: OnexEvent) -> None:
                received_events.append(event)

            event_bus.subscribe(callback)

            test_event = OnexEvent(
                event_type=event_data["event_type"],
                node_id=event_data["node_id"],
                metadata=event_data["metadata"],
            )

            event_bus.publish(test_event)

            assert (
                len(received_events) == 1
            ), f"{bus_name} with {case_name}: Expected 1 event, got {len(received_events)}"
            assert received_events[0].event_type == event_data["event_type"]
            assert received_events[0].node_id == event_data["node_id"]
            if event_data["metadata"]:
                assert received_events[0].metadata is not None

            # Clean up for next test case
            event_bus.unsubscribe(callback)
            if hasattr(event_bus, "clear"):
                event_bus.clear()


def test_multiple_subscribers_receive_same_event(
    event_bus_registry: Dict[str, ProtocolEventBus],
    event_test_cases: Dict[str, Dict[str, Any]],
    test_scenario_registry: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: Multiple subscribers should all receive the same event.
    """
    scenario = test_scenario_registry["multiple_subscribers"]
    subscriber_count = scenario["subscriber_count"]

    for bus_name, event_bus in event_bus_registry.items():
        # Clear any existing state
        if hasattr(event_bus, "clear"):
            event_bus.clear()

        for case_name, event_data in event_test_cases.items():
            received_events_list: List[List[OnexEvent]] = []
            callbacks = []

            # Create multiple subscribers
            for i in range(subscriber_count):
                received_events: List[OnexEvent] = []
                received_events_list.append(received_events)

                def callback(
                    event: OnexEvent, events_list: List[OnexEvent] = received_events
                ) -> None:
                    events_list.append(event)

                callbacks.append(callback)
                event_bus.subscribe(callback)

            test_event = OnexEvent(
                event_type=event_data["event_type"],
                node_id=event_data["node_id"],
                metadata=event_data["metadata"],
            )

            event_bus.publish(test_event)

            # All subscribers should receive the event
            for i, received_events in enumerate(received_events_list):
                assert (
                    len(received_events) == 1
                ), f"{bus_name} with {case_name}: Subscriber {i} expected 1 event, got {len(received_events)}"
                assert received_events[0].event_type == event_data["event_type"]
                assert received_events[0].node_id == event_data["node_id"]

            # Clean up for next test case
            for callback in callbacks:
                event_bus.unsubscribe(callback)
            if hasattr(event_bus, "clear"):
                event_bus.clear()


def test_events_received_in_order(
    event_bus_registry: Dict[str, ProtocolEventBus],
    event_test_cases: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: Events should be received in the order they are published.
    """
    for bus_name, event_bus in event_bus_registry.items():
        # Clear any existing state
        if hasattr(event_bus, "clear"):
            event_bus.clear()

        received_events: List[OnexEvent] = []

        def callback(event: OnexEvent) -> None:
            received_events.append(event)

        event_bus.subscribe(callback)

        # Create ordered events from test cases
        ordered_events = []
        for i, (case_name, event_data) in enumerate(event_test_cases.items()):
            test_event = OnexEvent(
                event_type=event_data["event_type"],
                node_id=f"{event_data['node_id']}_order_{i}",
                metadata={**event_data["metadata"], "order": i + 1},
            )
            ordered_events.append(test_event)

        # Publish events in order
        for event in ordered_events:
            event_bus.publish(event)

        assert len(received_events) == len(
            ordered_events
        ), f"{bus_name}: Expected {len(ordered_events)} events, got {len(received_events)}"

        # Verify order preservation
        for i, received_event in enumerate(received_events):
            expected_order = i + 1
            if received_event.metadata and "order" in received_event.metadata:
                assert (
                    received_event.metadata["order"] == expected_order
                ), f"{bus_name}: Event {i} out of order"

        # Clean up
        event_bus.unsubscribe(callback)
        if hasattr(event_bus, "clear"):
            event_bus.clear()


def test_event_data_preserved(
    event_bus_registry: Dict[str, ProtocolEventBus],
    event_test_cases: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: Event data (type, metadata) should be preserved during delivery.
    """
    for bus_name, event_bus in event_bus_registry.items():
        # Clear any existing state
        if hasattr(event_bus, "clear"):
            event_bus.clear()

        for case_name, event_data in event_test_cases.items():
            received_events: List[OnexEvent] = []

            def callback(event: OnexEvent) -> None:
                received_events.append(event)

            event_bus.subscribe(callback)

            test_event = OnexEvent(
                event_type=event_data["event_type"],
                node_id=event_data["node_id"],
                metadata=event_data["metadata"],
            )

            event_bus.publish(test_event)

            assert (
                len(received_events) == 1
            ), f"{bus_name} with {case_name}: Expected 1 event, got {len(received_events)}"
            received = received_events[0]

            assert received.event_type == event_data["event_type"]
            assert received.node_id == event_data["node_id"]
            assert received.metadata == event_data["metadata"]

            # Clean up for next test case
            event_bus.unsubscribe(callback)
            if hasattr(event_bus, "clear"):
                event_bus.clear()


def test_publish_with_no_subscribers(
    event_bus_registry: Dict[str, ProtocolEventBus],
    event_test_cases: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: Publishing with no subscribers should not error.
    """
    for bus_name, event_bus in event_bus_registry.items():
        # Clear any existing state
        if hasattr(event_bus, "clear"):
            event_bus.clear()

        for case_name, event_data in event_test_cases.items():
            test_event = OnexEvent(
                event_type=event_data["event_type"],
                node_id=event_data["node_id"],
                metadata=event_data["metadata"],
            )

            # Should not raise any exception
            try:
                event_bus.publish(test_event)
            except Exception as e:
                pytest.fail(
                    f"{bus_name} with {case_name}: Publishing with no subscribers should not error: {e}"
                )


def test_exception_in_subscriber_does_not_prevent_others(
    event_bus_registry: Dict[str, ProtocolEventBus],
    event_test_cases: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: Exception in one subscriber should not prevent others from receiving events.
    """
    for bus_name, event_bus in event_bus_registry.items():
        # Clear any existing state
        if hasattr(event_bus, "clear"):
            event_bus.clear()

        for case_name, event_data in event_test_cases.items():
            received_events_1: List[OnexEvent] = []
            received_events_3: List[OnexEvent] = []

            def callback_1(event: OnexEvent) -> None:
                received_events_1.append(event)

            def callback_2(event: OnexEvent) -> None:
                raise OnexError(
                    "Test exception in subscriber", CoreErrorCode.OPERATION_FAILED
                )

            def callback_3(event: OnexEvent) -> None:
                received_events_3.append(event)

            event_bus.subscribe(callback_1)
            event_bus.subscribe(callback_2)
            event_bus.subscribe(callback_3)

            test_event = OnexEvent(
                event_type=event_data["event_type"],
                node_id=event_data["node_id"],
                metadata=event_data["metadata"],
            )

            # Should not raise exception despite callback_2 failing
            event_bus.publish(test_event)

            # Other callbacks should still receive the event
            assert (
                len(received_events_1) == 1
            ), f"{bus_name} with {case_name}: Callback 1 should receive event, got {len(received_events_1)}"
            assert (
                len(received_events_3) == 1
            ), f"{bus_name} with {case_name}: Callback 3 should receive event, got {len(received_events_3)}"

            # Clean up for next test case
            event_bus.unsubscribe(callback_1)
            event_bus.unsubscribe(callback_2)
            event_bus.unsubscribe(callback_3)
            if hasattr(event_bus, "clear"):
                event_bus.clear()


def test_clear_removes_all_subscribers(
    event_bus_registry: Dict[str, ProtocolEventBus],
    event_test_cases: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: clear() should remove all subscribers (if supported).
    """
    for bus_name, event_bus in event_bus_registry.items():
        # Only test if clear method exists (it's optional)
        if not hasattr(event_bus, "clear"):
            continue

        for case_name, event_data in event_test_cases.items():
            received_events_1: List[OnexEvent] = []
            received_events_2: List[OnexEvent] = []

            def callback_1(event: OnexEvent) -> None:
                received_events_1.append(event)

            def callback_2(event: OnexEvent) -> None:
                received_events_2.append(event)

            event_bus.subscribe(callback_1)
            event_bus.subscribe(callback_2)

            # Clear all subscribers
            event_bus.clear()

            test_event = OnexEvent(
                event_type=event_data["event_type"],
                node_id=event_data["node_id"],
                metadata=event_data["metadata"],
            )

            event_bus.publish(test_event)

            # No callbacks should receive the event after clear
            assert (
                len(received_events_1) == 0
            ), f"{bus_name} with {case_name}: No events after clear, got {len(received_events_1)}"
            assert (
                len(received_events_2) == 0
            ), f"{bus_name} with {case_name}: No events after clear, got {len(received_events_2)}"


def test_error_handling_graceful(
    event_bus_registry: Dict[str, ProtocolEventBus],
    event_test_cases: Dict[str, Dict[str, Any]],
) -> None:
    """
    Protocol: Event bus should handle errors gracefully.
    """
    for bus_name, event_bus in event_bus_registry.items():
        for case_name, event_data in event_test_cases.items():
            test_event = OnexEvent(
                event_type=event_data["event_type"],
                node_id=event_data["node_id"],
                metadata=event_data["metadata"],
            )

            # These should not crash with unhandled exceptions
            try:
                # Test basic operations
                def dummy_callback(event: OnexEvent) -> None:
                    pass

                event_bus.subscribe(dummy_callback)
                event_bus.publish(test_event)
                event_bus.unsubscribe(dummy_callback)

                # Test edge cases
                event_bus.unsubscribe(dummy_callback)  # Unsubscribe non-existent
                event_bus.publish(test_event)  # Publish with no subscribers

            except Exception as e:
                # If exceptions occur, they should be handled gracefully
                assert isinstance(
                    e, (OnexError, TypeError, RuntimeError)
                ), f"{bus_name} with {case_name}: Unexpected exception type: {type(e)}"
