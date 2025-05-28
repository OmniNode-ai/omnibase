# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_telemetry_subscriber.py
# version: 1.0.0
# uuid: e8274289-c889-4cb8-bce7-ff6978e1bc3a
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.645331
# last_modified_at: 2025-05-28T17:20:04.112320
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 448c4cae701cd3338dea23690ad65ec337c17325897474bac185be95abcf4ccc
# entrypoint: python@test_telemetry_subscriber.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.test_telemetry_subscriber
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Tests for the telemetry subscriber utility.

This module tests the TelemetrySubscriber and related functionality to ensure
proper event capture, filtering, and output formatting.
"""

import io
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import (
    clear_telemetry_handlers,
    register_telemetry_handler,
    unregister_telemetry_handler,
)
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry.telemetry_subscriber import (
    TelemetryOutputFormat,
    TelemetrySubscriber,
    create_cli_subscriber,
)


class TestTelemetrySubscriber:
    """Test suite for TelemetrySubscriber."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.output_stream = io.StringIO()
        self.subscriber = TelemetrySubscriber(
            output_format=TelemetryOutputFormat.STRUCTURED,
            output_stream=self.output_stream,
            color_output=False,  # Disable colors for testing
        )

    def teardown_method(self) -> None:
        """Clean up after tests."""
        if self.subscriber._is_monitoring:
            self.subscriber.stop_monitoring()
        clear_telemetry_handlers()

    def test_subscriber_initialization(self) -> None:
        """Test that the subscriber initializes correctly."""
        assert self.subscriber.output_format == TelemetryOutputFormat.STRUCTURED
        assert self.subscriber.output_stream == self.output_stream
        assert not self.subscriber.color_output
        assert self.subscriber.show_timestamps
        assert self.subscriber.show_execution_times

    def test_start_stop_monitoring(self) -> None:
        """Test starting and stopping telemetry monitoring."""
        # Initially not monitoring
        assert not self.subscriber._is_monitoring
        assert self.subscriber._event_bus is None

        # Start monitoring (using None to trigger global event bus)
        self.subscriber.start_monitoring(None)
        assert self.subscriber._is_monitoring
        assert self.subscriber._event_bus is not None

        # Stop monitoring
        self.subscriber.stop_monitoring()
        assert not self.subscriber._is_monitoring
        assert self.subscriber._event_bus is None

    def test_start_monitoring_twice_raises_error(self) -> None:
        """Test that starting monitoring twice raises an error."""
        self.subscriber.start_monitoring(None)

        with pytest.raises(OnexError, match="already monitoring"):
            self.subscriber.start_monitoring(None)

    def test_event_filtering_by_correlation_id(self) -> None:
        """Test filtering events by correlation ID."""
        subscriber = TelemetrySubscriber(
            output_stream=self.output_stream,
            filter_correlation_ids=["test-correlation-123"],
            color_output=False,
        )

        # Event with matching correlation ID should be processed
        matching_event = {
            "correlation_id": "test-correlation-123",
            "node_id": "test_node",
            "operation": "test_op",
        }
        assert subscriber._should_process_event(matching_event)

        # Event with non-matching correlation ID should be filtered out
        non_matching_event = {
            "correlation_id": "other-correlation-456",
            "node_id": "test_node",
            "operation": "test_op",
        }
        assert not subscriber._should_process_event(non_matching_event)

    def test_event_filtering_by_node_id(self) -> None:
        """Test filtering events by node ID."""
        subscriber = TelemetrySubscriber(
            output_stream=self.output_stream,
            filter_node_ids=["stamper_node"],
            color_output=False,
        )

        # Event with matching node ID should be processed
        matching_event = {
            "correlation_id": "test-123",
            "node_id": "stamper_node",
            "operation": "test_op",
        }
        assert subscriber._should_process_event(matching_event)

        # Event with non-matching node ID should be filtered out
        non_matching_event = {
            "correlation_id": "test-123",
            "node_id": "other_node",
            "operation": "test_op",
        }
        assert not subscriber._should_process_event(non_matching_event)

    def test_event_filtering_by_operation(self) -> None:
        """Test filtering events by operation."""
        subscriber = TelemetrySubscriber(
            output_stream=self.output_stream,
            filter_operations=["process_file"],
            color_output=False,
        )

        # Event with matching operation should be processed
        matching_event = {
            "correlation_id": "test-123",
            "node_id": "test_node",
            "operation": "process_file",
        }
        assert subscriber._should_process_event(matching_event)

        # Event with non-matching operation should be filtered out
        non_matching_event = {
            "correlation_id": "test-123",
            "node_id": "test_node",
            "operation": "other_operation",
        }
        assert not subscriber._should_process_event(non_matching_event)

    def test_operation_tracking(self) -> None:
        """Test tracking of active operations for timing."""
        correlation_id = "test-correlation-123"

        # Start event should create tracking entry
        start_event = {
            "correlation_id": correlation_id,
            "event_type": OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            "node_id": "test_node",
            "operation": "test_op",
            "metadata": {"function": "test_function"},
        }
        self.subscriber._track_operation(start_event)
        assert correlation_id in self.subscriber._active_operations

        # Success event should calculate total time and remove tracking
        success_event = {
            "correlation_id": correlation_id,
            "event_type": OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
            "metadata": {"execution_time_ms": 100.0},
        }
        self.subscriber._track_operation(success_event)
        assert correlation_id not in self.subscriber._active_operations
        assert "total_execution_time_ms" in success_event

    def test_json_output_format(self) -> None:
        """Test JSON output format."""
        subscriber = TelemetrySubscriber(
            output_format=TelemetryOutputFormat.JSON,
            output_stream=self.output_stream,
        )

        event_data = {
            "event_type": OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            "correlation_id": "test-123",
            "node_id": "test_node",
            "operation": "test_op",
            "timestamp": datetime(2023, 1, 1, 12, 0, 0),
            "metadata": {"test": "value"},
        }

        subscriber._output_json(event_data)
        output = self.output_stream.getvalue()

        # Should be valid JSON
        import json

        parsed = json.loads(output)
        assert parsed["correlation_id"] == "test-123"
        assert parsed["node_id"] == "test_node"
        assert parsed["timestamp"] == "2023-01-01T12:00:00"

    def test_structured_output_format(self) -> None:
        """Test structured output format."""
        event_data = {
            "event_type": OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
            "correlation_id": "test-correlation-123",
            "node_id": "stamper_node",
            "operation": "process_file",
            "timestamp": datetime(2023, 1, 1, 12, 0, 0),
            "metadata": {"execution_time_ms": 150.5},
        }

        self.subscriber._output_structured(event_data)
        output = self.output_stream.getvalue()

        # Should contain key information
        assert "TELEMETRY_OPERATION_SUCCESS" in output
        assert "stamper_node::process_file" in output
        assert "test-cor" in output  # Truncated correlation ID
        assert "150.5ms" in output

    def test_compact_output_format(self) -> None:
        """Test compact output format."""
        subscriber = TelemetrySubscriber(
            output_format=TelemetryOutputFormat.COMPACT,
            output_stream=self.output_stream,
        )

        event_data = {
            "event_type": OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            "correlation_id": "test-correlation-123",
            "operation": "process_file",
        }

        subscriber._output_compact(event_data)
        output = self.output_stream.getvalue()

        # Should be compact format with the correct symbol for START events
        assert "▶ process_file (test-cor)" in output

    def test_table_output_format(self) -> None:
        """Test table output format."""
        subscriber = TelemetrySubscriber(
            output_format=TelemetryOutputFormat.TABLE,
            output_stream=self.output_stream,
        )

        event_data = {
            "event_type": OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
            "correlation_id": "test-correlation-123",
            "node_id": "stamper_node",
            "operation": "process_file",
            "timestamp": datetime(2023, 1, 1, 12, 0, 0),
            "metadata": {"execution_time_ms": 75.25},
        }

        subscriber._output_table(event_data)
        output = self.output_stream.getvalue()

        # Should be table format with columns
        assert "|" in output
        assert "SUCCESS" in output
        assert "test-correla" in output  # Truncated correlation ID
        assert "75.25ms" in output

    def test_error_event_output(self) -> None:
        """Test output formatting for error events."""
        event_data = {
            "event_type": OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR,
            "correlation_id": "test-123",
            "node_id": "test_node",
            "operation": "test_op",
            "metadata": {
                "error_type": "OnexError",
                "error_message": "Test error message",
                "execution_time_ms": 50.0,
            },
        }

        self.subscriber._output_structured(event_data)
        output = self.output_stream.getvalue()

        # Should include error information
        assert "TELEMETRY_OPERATION_ERROR" in output
        assert "OnexError: Test error message" in output


class TestCreateCliSubscriber:
    """Test suite for create_cli_subscriber function."""

    def test_create_cli_subscriber_defaults(self) -> None:
        """Test creating a CLI subscriber with default settings."""
        subscriber = create_cli_subscriber()

        assert subscriber.output_format == TelemetryOutputFormat.STRUCTURED
        assert subscriber.show_timestamps
        assert subscriber.show_execution_times
        assert not subscriber.filter_correlation_ids
        assert not subscriber.filter_node_ids
        assert not subscriber.filter_operations

    def test_create_cli_subscriber_with_filters(self) -> None:
        """Test creating a CLI subscriber with filters."""
        subscriber = create_cli_subscriber(
            format_type="json",
            correlation_id="test-123",
            node_id="stamper_node",
            operation="process_file",
            no_color=True,
            no_timestamps=True,
            no_execution_times=True,
        )

        assert subscriber.output_format == TelemetryOutputFormat.JSON
        assert not subscriber.show_timestamps
        assert not subscriber.show_execution_times
        assert not subscriber.color_output
        assert "test-123" in subscriber.filter_correlation_ids
        assert "stamper_node" in subscriber.filter_node_ids
        assert "process_file" in subscriber.filter_operations

    def test_create_cli_subscriber_invalid_format(self) -> None:
        """Test creating a CLI subscriber with invalid format falls back to structured."""
        subscriber = create_cli_subscriber(format_type="invalid_format")
        assert subscriber.output_format == TelemetryOutputFormat.STRUCTURED


class TestTelemetryIntegration:
    """Integration tests for telemetry subscriber with telemetry decorator."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        clear_telemetry_handlers()

    def teardown_method(self) -> None:
        """Clean up after tests."""
        clear_telemetry_handlers()

    def test_event_handler_registration(self) -> None:
        """Test registering and unregistering event handlers."""
        handler1 = MagicMock()
        handler2 = MagicMock()

        # Register handlers
        register_telemetry_handler(handler1)
        register_telemetry_handler(handler2)

        # Create a test event
        event = OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            correlation_id="test-123",
            node_id="test_node",
            timestamp=datetime.utcnow(),
        )

        # Import and call _emit_event to trigger handlers
        from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import _emit_event

        _emit_event(event)

        # Both handlers should have been called
        handler1.assert_called_once_with(event)
        handler2.assert_called_once_with(event)

        # Unregister one handler
        unregister_telemetry_handler(handler1)
        handler1.reset_mock()
        handler2.reset_mock()

        # Emit another event
        _emit_event(event)

        # Only handler2 should be called
        handler1.assert_not_called()
        handler2.assert_called_once_with(event)

    def test_clear_handlers(self) -> None:
        """Test clearing all telemetry handlers."""
        handler1 = MagicMock()
        handler2 = MagicMock()

        register_telemetry_handler(handler1)
        register_telemetry_handler(handler2)

        # Clear all handlers
        clear_telemetry_handlers()

        # Create and emit event
        event = OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            correlation_id="test-123",
            node_id="test_node",
            timestamp=datetime.utcnow(),
        )

        from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import _emit_event

        _emit_event(event)

        # No handlers should be called
        handler1.assert_not_called()
        handler2.assert_not_called()

    def test_handler_exception_handling(self) -> None:
        """Test that handler exceptions don't break event emission."""

        def failing_handler(event: OnexEvent) -> None:
            raise OnexError("Handler error", CoreErrorCode.OPERATION_FAILED)

        working_handler = MagicMock()

        register_telemetry_handler(failing_handler)
        register_telemetry_handler(working_handler)

        # Create and emit event
        event = OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            correlation_id="test-123",
            node_id="test_node",
            timestamp=datetime.utcnow(),
        )

        # Should not raise an exception
        from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import _emit_event

        _emit_event(event)

        # Working handler should still be called
        working_handler.assert_called_once_with(event)
