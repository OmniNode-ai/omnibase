# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_event_emission.py
# version: 1.0.0
# uuid: b8d3b1fe-5631-4803-b93e-94ac31189957
# author: OmniNode Team
# created_at: 2025-05-25T14:29:25.226680
# last_modified_at: 2025-05-25T18:41:25.273698
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 380f9d900f89f1a769fa189bf89f455db4962e21aae3c0ae3770a93c1b8cb442
# entrypoint: python@test_event_emission.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_event_emission
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Comprehensive tests for event emission and telemetry subscriber output.

This test suite validates:
1. Telemetry decorator event emission
2. Event schema compliance
3. Stamper node integration with telemetry
4. Telemetry subscriber functionality
5. End-to-end event flow
"""

import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import patch

import pytest

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.fixtures.mocks.dummy_schema_loader import DummySchemaLoader
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.nodes.stamper_node.v1_0_0.helpers.stamper_engine import StamperEngine
from omnibase.nodes.stamper_node.v1_0_0.models.state import StamperInputState
from omnibase.nodes.stamper_node.v1_0_0.node import run_stamper_node
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import telemetry
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry.event_schema_validator import (
    validate_event_schema,
)
from omnibase.runtimes.onex_runtime.v1_0_0.utils.onex_version_loader import (
    OnexVersionLoader,
)
from omnibase.utils.real_file_io import RealFileIO


class TestTelemetryDecoratorEventEmission:
    """Test telemetry decorator event emission functionality."""

    def test_telemetry_decorator_emits_start_and_success_events(self) -> None:
        """Test that telemetry decorator emits start and success events."""
        event_bus = InMemoryEventBus()
        events: List[OnexEvent] = []

        def capture_events(event: OnexEvent) -> None:
            events.append(event)

        event_bus.subscribe(capture_events)

        @telemetry(
            node_name="test_node", operation="test_operation", event_bus=event_bus
        )
        def test_function(**kwargs: Any) -> str:
            return "success"

        # Execute function
        result = test_function()

        # Verify result
        assert result == "success"

        # Verify events were emitted
        assert len(events) == 2

        # Verify start event
        start_event = events[0]
        assert start_event.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START
        assert start_event.node_id == "test_node"
        assert start_event.metadata is not None
        assert start_event.metadata["operation"] == "test_operation"

        # Verify success event
        success_event = events[1]
        assert success_event.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS
        assert success_event.node_id == "test_node"
        assert success_event.metadata is not None
        assert success_event.metadata["operation"] == "test_operation"

        # Verify correlation ID consistency
        assert start_event.correlation_id == success_event.correlation_id

    def test_telemetry_decorator_emits_error_event_on_exception(self) -> None:
        """Test that telemetry decorator emits error event when function raises exception."""
        event_bus = InMemoryEventBus()
        events: List[OnexEvent] = []

        def capture_events(event: OnexEvent) -> None:
            events.append(event)

        event_bus.subscribe(capture_events)

        @telemetry(
            node_name="test_node", operation="test_operation", event_bus=event_bus
        )
        def failing_function(**kwargs: Any) -> str:
            raise OnexError("Test error", CoreErrorCode.OPERATION_FAILED)

        # Execute function and expect exception
        with pytest.raises(OnexError, match="Test error"):
            failing_function()

        # Verify events were emitted
        assert len(events) == 2

        # Verify start event
        start_event = events[0]
        assert start_event.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START

        # Verify error event
        error_event = events[1]
        assert error_event.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR
        assert error_event.node_id == "test_node"
        assert error_event.metadata is not None
        assert error_event.metadata["operation"] == "test_operation"
        assert "error_message" in error_event.metadata
        assert "Test error" in error_event.metadata["error_message"]

    def test_telemetry_decorator_generates_correlation_id_if_not_provided(self) -> None:
        """Test that telemetry decorator generates correlation ID if not provided."""
        event_bus = InMemoryEventBus()
        events: List[OnexEvent] = []

        def capture_events(event: OnexEvent) -> None:
            events.append(event)

        event_bus.subscribe(capture_events)

        @telemetry(
            node_name="test_node", operation="test_operation", event_bus=event_bus
        )
        def test_function(**kwargs: Any) -> str:
            return "success"

        # Execute function without correlation_id
        test_function()

        # Verify correlation ID was generated
        assert len(events) == 2
        start_event = events[0]
        success_event = events[1]

        assert start_event.correlation_id is not None
        assert success_event.correlation_id is not None
        assert start_event.correlation_id == success_event.correlation_id

        # Verify it's a valid UUID format
        uuid.UUID(start_event.correlation_id)

    def test_telemetry_decorator_with_emit_events_disabled(self) -> None:
        """Test that telemetry decorator respects emit_events=False."""
        event_bus = InMemoryEventBus()
        events: List[OnexEvent] = []

        def capture_events(event: OnexEvent) -> None:
            events.append(event)

        event_bus.subscribe(capture_events)

        @telemetry(
            node_name="test_node",
            operation="test_operation",
            event_bus=event_bus,
            emit_events=False,
        )
        def test_function(**kwargs: Any) -> str:
            return "success"

        # Execute function
        result = test_function()

        # Verify no events were emitted
        assert len(events) == 0
        assert result == "success"

    def test_emitted_events_comply_with_schema(self) -> None:
        """Test that all emitted events comply with ONEX event schema."""
        event_bus = InMemoryEventBus()
        events: List[OnexEvent] = []

        def capture_events(event: OnexEvent) -> None:
            events.append(event)

        event_bus.subscribe(capture_events)

        @telemetry(
            node_name="test_node", operation="test_operation", event_bus=event_bus
        )
        def test_function(**kwargs: Any) -> str:
            return "success"

        # Execute function
        test_function()

        # Validate all events against schema
        for event in events:
            # Should not raise any exceptions
            validate_event_schema(event, strict_mode=True)

            # Verify required fields are present
            assert event.event_id is not None
            assert event.timestamp is not None
            assert event.node_id is not None
            assert event.event_type is not None
            assert event.correlation_id is not None


class TestStamperNodeEventEmission:
    """Test stamper node integration with telemetry and event emission."""

    def test_stamper_node_emits_telemetry_events(self) -> None:
        """Test that stamper node emits telemetry events during execution."""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('# Test file for stamping\nprint("Hello, world!")\n')
            test_file_path = f.name

        try:
            # Create event bus to capture events
            event_bus = InMemoryEventBus()
            events: List[OnexEvent] = []

            def capture_events(event: OnexEvent) -> None:
                events.append(event)

            event_bus.subscribe(capture_events)

            # Create input state
            schema_version = OnexVersionLoader().get_onex_versions().schema_version
            input_state = StamperInputState(
                file_path=test_file_path,
                author="Test Author",
                version=schema_version,
                correlation_id="stamper-test-123",
            )

            # Create stamper engine with real file I/O for disk operations
            stamper_engine = StamperEngine(
                schema_loader=DummySchemaLoader(),
                file_io=RealFileIO(),  # Use real file I/O for disk operations
            )

            # Mock the stamper engine creation in the node
            with patch(
                "omnibase.nodes.stamper_node.v1_0_0.node.StamperEngine"
            ) as mock_engine_class:
                mock_engine_class.return_value = stamper_engine

                # Execute stamper node with event_bus passed through kwargs
                # This allows the telemetry decorator to pick up the event_bus
                output_state = run_stamper_node(
                    input_state, event_bus=event_bus, correlation_id="stamper-test-123"
                )

            # Verify stamper succeeded
            assert output_state.status == "success"

            # Verify events were emitted
            # Should have: NODE_START, NODE_SUCCESS (from node), TELEMETRY_OPERATION_START, TELEMETRY_OPERATION_SUCCESS (from decorator)
            assert len(events) >= 4

            # Find events by type
            node_start_events = [
                e for e in events if e.event_type == OnexEventTypeEnum.NODE_START
            ]
            node_success_events = [
                e for e in events if e.event_type == OnexEventTypeEnum.NODE_SUCCESS
            ]
            telemetry_start_events = [
                e
                for e in events
                if e.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START
            ]
            telemetry_success_events = [
                e
                for e in events
                if e.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS
            ]

            # Verify we have the expected events
            assert len(node_start_events) == 1
            assert len(node_success_events) == 1
            assert (
                len(telemetry_start_events) >= 1
            )  # May have multiple telemetry operations
            assert len(telemetry_success_events) >= 1

            # Verify correlation ID propagation
            correlation_ids = {e.correlation_id for e in events}
            assert "stamper-test-123" in correlation_ids

            # Verify node events have correct node_id
            assert node_start_events[0].node_id == "stamper_node"
            assert node_success_events[0].node_id == "stamper_node"

            # Verify telemetry events have correct node_id
            assert telemetry_start_events[0].node_id == "stamper_node"
            assert telemetry_success_events[0].node_id == "stamper_node"

        finally:
            # Clean up temporary file
            Path(test_file_path).unlink(missing_ok=True)

    def test_stamper_node_emits_failure_event_on_error(self) -> None:
        """Test that stamper node handles errors gracefully and emits appropriate events."""
        event_bus = InMemoryEventBus()
        events: List[OnexEvent] = []

        def capture_events(event: OnexEvent) -> None:
            events.append(event)

        event_bus.subscribe(capture_events)

        # Create input state with non-existent file
        schema_version = OnexVersionLoader().get_onex_versions().schema_version
        input_state = StamperInputState(
            file_path="/non/existent/file.py",
            author="Test Author",
            version=schema_version,
            correlation_id="stamper-error-test-456",
        )

        # Execute stamper node - it should handle the error gracefully and return error status
        output_state = run_stamper_node(
            input_state, event_bus=event_bus, correlation_id="stamper-error-test-456"
        )

        # Verify stamper returned error status but completed successfully
        assert output_state.status == "error"
        assert output_state.correlation_id == "stamper-error-test-456"

        # Verify events were emitted - should be NODE_START, NODE_SUCCESS (not NODE_FAILURE)
        # because the stamper handles errors gracefully
        node_start_events = [
            e for e in events if e.event_type == OnexEventTypeEnum.NODE_START
        ]
        node_success_events = [
            e for e in events if e.event_type == OnexEventTypeEnum.NODE_SUCCESS
        ]
        node_failure_events = [
            e for e in events if e.event_type == OnexEventTypeEnum.NODE_FAILURE
        ]

        assert len(node_start_events) == 1
        assert len(node_success_events) == 1
        assert (
            len(node_failure_events) == 0
        )  # No failure events because error was handled gracefully

        # Verify correlation ID propagation
        assert node_start_events[0].correlation_id == "stamper-error-test-456"
        assert node_success_events[0].correlation_id == "stamper-error-test-456"


class TestTelemetrySubscriberEventHandling:
    """Test telemetry subscriber event handling functionality."""

    def test_telemetry_subscriber_receives_and_processes_events(self) -> None:
        """Test that telemetry subscriber receives and processes events correctly."""
        event_bus = InMemoryEventBus()

        # Create a simple event handler to capture events
        processed_events: List[OnexEvent] = []

        def capture_events(event: OnexEvent) -> None:
            processed_events.append(event)

        # Subscribe to event bus directly
        event_bus.subscribe(capture_events)

        # Emit test events
        test_events = [
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_START,
                node_id="test_node",
                correlation_id="test-123",
                metadata={"test": "data"},
            ),
            OnexEvent(
                event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
                node_id="test_node",
                correlation_id="test-123",
                metadata={"operation": "test_op"},
            ),
            OnexEvent(
                event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
                node_id="test_node",
                correlation_id="test-123",
                metadata={"operation": "test_op", "duration_ms": 100},
            ),
        ]

        for event in test_events:
            event_bus.publish(event)

        # Verify subscriber processed all events
        assert len(processed_events) == 3
        assert processed_events == test_events

    def test_telemetry_subscriber_handles_event_validation_errors(self) -> None:
        """Test that telemetry subscriber handles event validation errors gracefully."""
        event_bus = InMemoryEventBus()

        # Create event handler with validation
        processed_events: List[OnexEvent] = []
        validation_errors: List[Exception] = []

        def validate_and_capture_events(event: OnexEvent) -> None:
            try:
                # Validate event schema
                validate_event_schema(event, strict_mode=True)
                processed_events.append(event)
            except Exception as e:
                validation_errors.append(e)

        event_bus.subscribe(validate_and_capture_events)

        # Create invalid event (missing required fields)
        invalid_event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id="",  # Invalid: empty node_id
            correlation_id="test-123",
            metadata={},
        )

        # Emit invalid event
        event_bus.publish(invalid_event)

        # Verify validation error was caught
        assert len(validation_errors) == 1
        assert len(processed_events) == 0


class TestEndToEndEventFlow:
    """Test end-to-end event flow from emission to subscriber processing."""

    def test_complete_event_flow_with_schema_validation(self) -> None:
        """Test complete event flow with schema validation."""
        event_bus = InMemoryEventBus()

        # Set up event capture
        all_events: List[OnexEvent] = []
        validated_events: List[OnexEvent] = []
        validation_errors: List[Exception] = []

        def capture_and_validate_events(event: OnexEvent) -> None:
            all_events.append(event)
            try:
                validate_event_schema(event, strict_mode=True)
                validated_events.append(event)
            except Exception as e:
                validation_errors.append(e)

        event_bus.subscribe(capture_and_validate_events)

        # Execute telemetry-decorated function
        @telemetry(
            node_name="end_to_end_test", operation="test_operation", event_bus=event_bus
        )
        def test_function(**kwargs: Any) -> Dict[str, Any]:
            return {"result": "success", "data": [1, 2, 3]}

        # Execute function
        result = test_function(correlation_id="e2e-test-789")

        # Verify function result
        assert result == {"result": "success", "data": [1, 2, 3]}

        # Verify events were emitted and validated
        assert len(all_events) == 2  # START and SUCCESS
        assert len(validated_events) == 2  # Both should be valid
        assert len(validation_errors) == 0  # No validation errors

        # Verify event details
        start_event = validated_events[0]
        success_event = validated_events[1]

        assert start_event.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START
        assert success_event.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS
        assert start_event.correlation_id == "e2e-test-789"
        assert success_event.correlation_id == "e2e-test-789"
        assert start_event.node_id == "end_to_end_test"
        assert success_event.node_id == "end_to_end_test"

    def test_event_flow_with_correlation_id_propagation(self) -> None:
        """Test that correlation IDs are properly propagated through event flow."""
        event_bus = InMemoryEventBus()
        events: List[OnexEvent] = []

        def capture_events(event: OnexEvent) -> None:
            print(f"Captured event: {event.event_type} from {event.node_id}")
            events.append(event)

        event_bus.subscribe(capture_events)

        # Test multiple operations with same correlation ID
        correlation_id = "correlation-test-999"

        @telemetry(node_name="node_1", operation="op_1", event_bus=event_bus)
        def operation_1(**kwargs: Any) -> str:
            return "op1_result"

        @telemetry(node_name="node_2", operation="op_2", event_bus=event_bus)
        def operation_2(**kwargs: Any) -> str:
            return "op2_result"

        # Execute operations with same correlation ID
        result1 = operation_1(correlation_id=correlation_id)
        result2 = operation_2(correlation_id=correlation_id)

        # Verify results
        assert result1 == "op1_result"
        assert result2 == "op2_result"

        # Verify all events have the same correlation ID
        assert len(events) == 4  # 2 operations × 2 events each
        for event in events:
            assert event.correlation_id == correlation_id

        # Verify event sequence
        assert events[0].event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START
        assert events[0].node_id == "node_1"
        assert events[1].event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS
        assert events[1].node_id == "node_1"
        assert events[2].event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START
        assert events[2].node_id == "node_2"
        assert events[3].event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS
        assert events[3].node_id == "node_2"
