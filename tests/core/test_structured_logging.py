# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_structured_logging.py
# version: 1.0.0
# uuid: b6d526b8-0895-4773-b36a-46e487de50e9
# author: OmniNode Team
# created_at: 2025-05-26T15:47:37.841917
# last_modified_at: 2025-05-27T09:37:09.261277
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 16ded2551b4d99787977ff70f572333c7b13daaf8c440024c2477f8b44c3343b
# entrypoint: python@test_structured_logging.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_structured_logging
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Tests for structured logging system.

This module tests the structured logging system to ensure it handles
complex scenarios correctly, including recursion avoidance and error handling.
"""

import threading
from typing import Any
from unittest.mock import patch

import pytest

from omnibase.core.core_structured_logging import (
    LogLevelEnum,
    OnexLoggingConfig,
    StructuredLoggingAdapter,
    emit_log_event,
    setup_structured_logging,
)
from omnibase.enums import OutputFormatEnum
from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import (
    InMemoryEventBus,
)


class TestStructuredLogging:
    """Test suite for structured logging system."""

    def test_basic_logging_flow(self) -> None:
        """Test that the basic logging flow doesn't crash."""
        # Create event bus
        event_bus = InMemoryEventBus()
        config = OnexLoggingConfig(
            default_output_format=OutputFormatEnum.TEXT,
            log_level=LogLevelEnum.DEBUG,
            enable_correlation_ids=True,
        )

        # Set up structured logging with our test config and event bus
        setup_structured_logging(config, event_bus)

        # Simply verify that these don't raise exceptions
        emit_log_event(LogLevelEnum.INFO, "Test message")
        emit_log_event(LogLevelEnum.ERROR, "Error message")
        emit_log_event(LogLevelEnum.WARNING, "Warning message")

        # This test passes if we get here without infinite recursion or exceptions
        assert True

    def test_recursive_logging_prevention(self) -> None:
        """Test that recursive logging is prevented."""
        # Create event bus with a counter to detect multiple calls
        event_bus = InMemoryEventBus()

        # Set up structured logging with our test config and event bus
        setup_structured_logging(None, event_bus)

        # Create a spy to track publish calls
        original_publish = event_bus.publish
        publish_count = 0

        def publish_spy(event: Any) -> None:
            nonlocal publish_count
            publish_count += 1

            # Call original publish
            original_publish(event)

            # Simulate recursive log from Logger Node
            if (
                publish_count == 1
                and event.event_type == OnexEventTypeEnum.STRUCTURED_LOG
            ):
                # Create a fake Logger Node log event that would normally cause recursion
                recursive_event = OnexEvent(
                    event_type=OnexEventTypeEnum.STRUCTURED_LOG,
                    node_id="logger_node",
                    metadata={
                        "log_level": "info",
                        "message": "Recursive log message",
                        "context": {
                            "calling_module": "omnibase.nodes.logger_node.v1_0_0.node"
                        },
                    },
                )
                original_publish(recursive_event)

        # Install the spy by creating a mock event bus
        class MockEventBus:
            def __init__(self, original_bus: Any):
                self.original_bus = original_bus
                self.publish = publish_spy

            def subscribe(self, callback: Any) -> None:
                self.original_bus.subscribe(callback)

            def unsubscribe(self, callback: Any) -> None:
                self.original_bus.unsubscribe(callback)

        mock_bus = MockEventBus(event_bus)

        # Patch the global event bus
        with patch("omnibase.core.structured_logging._global_event_bus", mock_bus):
            # Emit a log that will trigger the spy
            emit_log_event(LogLevelEnum.INFO, "Test log")

        # We've done recursive publishing, but we shouldn't enter infinite recursion
        # The test passes if we get here without crashing
        assert publish_count > 0

    def test_error_handling(self) -> None:
        """Test that errors in log handling don't crash the application."""
        # Create event bus
        event_bus = InMemoryEventBus()

        # Set up structured logging
        setup_structured_logging(None, event_bus)

        # Make the _handle_log_event method raise an exception
        def failing_handler(event: Any) -> None:
            # Always fail on handling
            from omnibase.core.core_error_codes import CoreErrorCode, OnexError

            raise OnexError(
                "Simulated error in log handling", CoreErrorCode.OPERATION_FAILED
            )

        # Install the failing handler
        with patch.object(
            StructuredLoggingAdapter, "_handle_log_event", failing_handler
        ):
            # This should trigger the error but not crash
            emit_log_event(LogLevelEnum.INFO, "Trigger error")

            # This should still work despite the previous error
            emit_log_event(LogLevelEnum.INFO, "After error")

        # This test passes if we get here without crashing
        assert True

    def test_concurrent_logging(self) -> None:
        """Test that concurrent logging doesn't cause issues."""
        # Create event bus
        event_bus = InMemoryEventBus()

        # Set up structured logging
        setup_structured_logging(None, event_bus)

        # Create multiple threads to emit logs concurrently
        log_count = 10
        threads = []

        for i in range(log_count):
            thread = threading.Thread(
                target=emit_log_event,
                args=(LogLevelEnum.INFO, f"Concurrent message {i}"),
            )
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # This test passes if we get here without crashing or deadlocking
        assert True


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
