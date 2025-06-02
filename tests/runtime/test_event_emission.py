# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-25T14:29:25.226680'
# description: Stamped by PythonHandler
# entrypoint: python://test_event_emission.py
# hash: c19c972f6b8bb76ab0acae5ddb85045d114553457b91439aa68e0cf570d2bd80
# last_modified_at: '2025-05-29T13:43:02.106726+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_event_emission.py
# namespace:
#   value: py://omnibase.tests.runtime.test_event_emission_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: b8d3b1fe-5631-4803-b93e-94ac31189957
# version: 1.0.0
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

import inspect
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import patch

import pytest

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_structured_logging import LogContextModel, emit_log_event
from omnibase.enums import LogLevel
from omnibase.fixtures.mocks.dummy_schema_loader import DummySchemaLoader
from omnibase.model.model_onex_event import (
    OnexEvent,
    OnexEventMetadataModel,
    OnexEventTypeEnum,
)
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


def make_test_log_context(test_name: str) -> LogContextModel:
    frame = inspect.currentframe().f_back
    return LogContextModel(
        calling_module=frame.f_globals.get("__name__", "<unknown>"),
        calling_function=frame.f_code.co_name,
        calling_line=frame.f_lineno,
        timestamp=datetime.now().isoformat(),
        test=test_name,
    )


@pytest.fixture
def test_event_bus():
    """
    Fixture that provides a fresh InMemoryEventBus for each test.
    """
    bus = InMemoryEventBus()
    emit_log_event(LogLevel.DEBUG, f"[FIXTURE] Created test_event_bus with bus_id={bus.bus_id}", event_bus=bus)
    yield bus
    # Optionally clear subscribers after test (for async/long-lived tests)
    bus.clear()


class TestTelemetryDecoratorEventEmission:
    """Test telemetry decorator event emission functionality."""

    def test_telemetry_decorator_emits_start_and_success_events(
        self, test_event_bus
    ) -> None:
        """Test that telemetry decorator emits start and success events."""
        event_bus = test_event_bus
        events: List[OnexEvent] = []

        def capture_events(event: OnexEvent) -> None:
            if event.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
                return
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

        # Filter for only TELEMETRY_OPERATION_* events
        telemetry_events = [
            e
            for e in events
            if isinstance(e, OnexEvent)
            and e.event_type.name.startswith("TELEMETRY_OPERATION_")
            and e.event_type != OnexEventTypeEnum.STRUCTURED_LOG
        ]
        assert len(telemetry_events) == 2
        start_event = next(
            e
            for e in telemetry_events
            if e.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START
        )
        success_event = next(
            e
            for e in telemetry_events
            if e.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS
        )
        assert start_event.node_id == "test_node"
        assert start_event.metadata.operation == "test_operation"
        assert success_event.node_id == "test_node"
        assert success_event.metadata.operation == "test_operation"
        assert start_event.correlation_id == success_event.correlation_id


class TestStamperNodeEventEmission:
    """Test stamper node integration with telemetry and event emission."""

    def test_stamper_node_emits_telemetry_events(self, test_event_bus) -> None:
        """Test that stamper node emits telemetry events during execution."""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('# Test file for stamping\nprint("Hello, world!")\n')
            test_file_path = f.name

        try:
            event_bus = test_event_bus
            events: List[OnexEvent] = []

            def capture_events(event: OnexEvent) -> None:
                if event.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
                    return
                events.append(event)

            event_bus.subscribe(capture_events)

            schema_version = OnexVersionLoader().get_onex_versions().schema_version
            input_state = StamperInputState(
                file_path=test_file_path,
                author="Test Author",
                version=schema_version,
                correlation_id="stamper-test-123",
            )

            stamper_engine = StamperEngine(
                schema_loader=DummySchemaLoader(),
                file_io=RealFileIO(),
                event_bus=event_bus,
            )

            with patch(
                "omnibase.nodes.stamper_node.v1_0_0.node.StamperEngine"
            ) as mock_engine_class:
                mock_engine_class.return_value = stamper_engine
                output_state = run_stamper_node(input_state, event_bus=event_bus)

            assert output_state.status == "success"

            onex_events = [
                e
                for e in events
                if isinstance(e, OnexEvent)
                and e.event_type != OnexEventTypeEnum.STRUCTURED_LOG
            ]
            assert len(onex_events) >= 4
            node_start_events = [
                e for e in onex_events if e.event_type == OnexEventTypeEnum.NODE_START
            ]
            node_success_events = [
                e for e in onex_events if e.event_type == OnexEventTypeEnum.NODE_SUCCESS
            ]
            telemetry_start_events = [
                e
                for e in onex_events
                if e.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START
            ]
            telemetry_success_events = [
                e
                for e in onex_events
                if e.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS
            ]
            assert len(node_start_events) == 1
            assert len(node_success_events) == 1
            assert len(telemetry_start_events) >= 1
            assert len(telemetry_success_events) >= 1
            correlation_ids = {e.correlation_id for e in onex_events}
            assert "stamper-test-123" in correlation_ids
            assert node_start_events[0].node_id == "stamper_node"
            assert node_success_events[0].node_id == "stamper_node"
            assert telemetry_start_events[0].node_id == "stamper_node"
            assert telemetry_success_events[0].node_id == "stamper_node"
        finally:
            Path(test_file_path).unlink(missing_ok=True)

    def test_stamper_node_emits_failure_event_on_error(self, test_event_bus) -> None:
        """Test that stamper node handles errors gracefully and emits appropriate events."""
        event_bus = test_event_bus
        events: List[OnexEvent] = []

        def capture_events(event: OnexEvent) -> None:
            if event.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
                return
            events.append(event)

        event_bus.subscribe(capture_events)

        schema_version = OnexVersionLoader().get_onex_versions().schema_version
        input_state = StamperInputState(
            file_path="/non/existent/file.py",
            author="Test Author",
            version=schema_version,
            correlation_id="stamper-error-test-456",
        )

        output_state = run_stamper_node(input_state, event_bus=event_bus)
        assert output_state.status == "error"
        onex_events = [
            e
            for e in events
            if isinstance(e, OnexEvent)
            and e.event_type != OnexEventTypeEnum.STRUCTURED_LOG
        ]
        node_start_events = [
            e for e in onex_events if e.event_type == OnexEventTypeEnum.NODE_START
        ]
        node_success_events = [
            e for e in onex_events if e.event_type == OnexEventTypeEnum.NODE_SUCCESS
        ]
        node_failure_events = [
            e for e in onex_events if e.event_type == OnexEventTypeEnum.NODE_FAILURE
        ]
        assert len(node_start_events) == 1
        assert len(node_success_events) == 1
        assert len(node_failure_events) == 0
        assert node_start_events[0].correlation_id == "stamper-error-test-456"
        assert node_success_events[0].correlation_id == "stamper-error-test-456"


class TestTelemetrySubscriberEventHandling:
    """Test telemetry subscriber event handling functionality."""

    def test_telemetry_subscriber_receives_and_processes_events(
        self, test_event_bus
    ) -> None:
        """Test that telemetry subscriber receives and processes events correctly."""
        event_bus = test_event_bus
        processed_events: List[OnexEvent] = []

        def capture_events(event: OnexEvent) -> None:
            if event.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
                return
            processed_events.append(event)

        event_bus.subscribe(capture_events)
        test_events = [
            OnexEvent(
                event_type=OnexEventTypeEnum.NODE_START,
                node_id="test_node",
                correlation_id="test-123",
                metadata=OnexEventMetadataModel(test="data"),
            ),
            OnexEvent(
                event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
                node_id="test_node",
                correlation_id="test-123",
                metadata=OnexEventMetadataModel(operation="test_op"),
            ),
            OnexEvent(
                event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
                node_id="test_node",
                correlation_id="test-123",
                metadata=OnexEventMetadataModel(operation="test_op", duration_ms=100),
            ),
        ]
        for event in test_events:
            event_bus.publish(event)
        onex_events = [
            e
            for e in processed_events
            if isinstance(e, OnexEvent)
            and e.event_type != OnexEventTypeEnum.STRUCTURED_LOG
        ]
        assert len(onex_events) == 3
        assert onex_events == test_events

    def test_telemetry_subscriber_handles_event_validation_errors(
        self, test_event_bus
    ) -> None:
        event_bus = test_event_bus
        processed_events: List[OnexEvent] = []
        validation_errors: List[Exception] = []

        def validate_and_capture_events(event: OnexEvent) -> None:
            if event.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
                return
            try:
                validate_event_schema(event, strict_mode=True)
                processed_events.append(event)
            except Exception as e:
                validation_errors.append(e)

        event_bus.subscribe(validate_and_capture_events)
        invalid_event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id="",  # Invalid: empty node_id
            correlation_id="test-123",
            metadata=OnexEventMetadataModel(),
        )
        event_bus.publish(invalid_event)
        onex_events = [
            e
            for e in processed_events
            if isinstance(e, OnexEvent)
            and e.event_type != OnexEventTypeEnum.STRUCTURED_LOG
        ]
        assert len(validation_errors) == 1
        assert len(onex_events) == 0


class TestEndToEndEventFlow:
    """Test end-to-end event flow from emission to subscriber processing."""

    def test_complete_event_flow_with_schema_validation(self, test_event_bus) -> None:
        """Test complete event flow with schema validation."""
        event_bus = test_event_bus
        events: List[OnexEvent] = []

        def capture_and_validate_events(event: OnexEvent) -> None:
            if event.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
                return
            events.append(event)
            try:
                if e.event_type.name.startswith("TELEMETRY_OPERATION_"):
                    validate_event_schema(event, strict_mode=True, event_bus=event_bus)
            except Exception:
                pass

        event_bus.subscribe(capture_and_validate_events)

        @telemetry(
            node_name="end_to_end_test", operation="test_operation", event_bus=event_bus
        )
        def test_function(**kwargs: Any) -> Dict[str, Any]:
            return {"result": "success", "data": [1, 2, 3]}

        result = test_function(correlation_id="e2e-test-789")
        assert result == {"result": "success", "data": [1, 2, 3]}
        telemetry_events = [
            e
            for e in events
            if isinstance(e, OnexEvent)
            and e.event_type.name.startswith("TELEMETRY_OPERATION_")
            and e.event_type != OnexEventTypeEnum.STRUCTURED_LOG
        ]
        assert len(telemetry_events) == 2  # START and SUCCESS
        start_event = next(
            e
            for e in telemetry_events
            if e.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START
        )
        success_event = next(
            e
            for e in telemetry_events
            if e.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS
        )
        assert start_event.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START
        assert success_event.event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS
        assert start_event.correlation_id == "e2e-test-789"
        assert success_event.correlation_id == "e2e-test-789"
        assert start_event.node_id == "end_to_end_test"
        assert success_event.node_id == "end_to_end_test"

    def test_event_flow_with_correlation_id_propagation(self, test_event_bus) -> None:
        """Test that correlation IDs are properly propagated through event flow."""
        event_bus = test_event_bus
        events: List[OnexEvent] = []

        def capture_events(event: OnexEvent) -> None:
            if event.event_type == OnexEventTypeEnum.STRUCTURED_LOG:
                return
            events.append(event)

        event_bus.subscribe(capture_events)
        correlation_id = "correlation-test-999"

        @telemetry(node_name="node_1", operation="op_1", event_bus=event_bus)
        def operation_1(**kwargs: Any) -> str:
            return "op1_result"

        @telemetry(node_name="node_2", operation="op_2", event_bus=event_bus)
        def operation_2(**kwargs: Any) -> str:
            return "op2_result"

        result1 = operation_1(correlation_id=correlation_id)
        result2 = operation_2(correlation_id=correlation_id)
        assert result1 == "op1_result"
        assert result2 == "op2_result"
        telemetry_events = [
            e
            for e in events
            if isinstance(e, OnexEvent)
            and e.event_type.name.startswith("TELEMETRY_OPERATION_")
            and e.event_type != OnexEventTypeEnum.STRUCTURED_LOG
        ]
        assert len(telemetry_events) == 4  # 2 operations × 2 events each
        for event in telemetry_events:
            assert event.correlation_id == correlation_id
        assert (
            telemetry_events[0].event_type
            == OnexEventTypeEnum.TELEMETRY_OPERATION_START
        )
        assert telemetry_events[0].node_id == "node_1"
        assert (
            telemetry_events[1].event_type
            == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS
        )
        assert telemetry_events[1].node_id == "node_1"
        assert (
            telemetry_events[2].event_type
            == OnexEventTypeEnum.TELEMETRY_OPERATION_START
        )
        assert telemetry_events[2].node_id == "node_2"
        assert (
            telemetry_events[3].event_type
            == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS
        )
        assert telemetry_events[3].node_id == "node_2"
