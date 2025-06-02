# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.880085'
# description: Stamped by PythonHandler
# entrypoint: python://test_structured_logging.py
# hash: 9f4593dfdb0927ef232d29fb4b8363229eb5218b8cbc7fdf8002203fac0f98ff
# last_modified_at: '2025-05-29T13:51:23.338366+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_structured_logging.py
# namespace: py://omnibase.tests.core.test_structured_logging_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 581688c6-2007-4b99-90d4-fc3a11030aaa
# version: 1.0.0
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
    LogContextModel,
    OnexLoggingConfig,
    StructuredLoggingAdapter,
    emit_log_event_sync,
    setup_structured_logging,
)
from omnibase.enums import LogLevelEnum, OutputFormatEnum
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
        emit_log_event_sync(LogLevelEnum.INFO, "Test message", event_bus=event_bus)
        emit_log_event_sync(LogLevelEnum.ERROR, "Error message", event_bus=event_bus)
        emit_log_event_sync(LogLevelEnum.WARNING, "Warning message", event_bus=event_bus)

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

            # Simulate recursive log from Logger Node only for OnexEvent
            if (
                isinstance(event, OnexEvent)
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
        with patch("omnibase.core.core_structured_logging._global_event_bus", mock_bus):
            # Emit a log that will trigger the spy
            emit_log_event_sync(LogLevelEnum.INFO, "Test log", event_bus=mock_bus)

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
            emit_log_event_sync(LogLevelEnum.INFO, "Trigger error", event_bus=event_bus)
            emit_log_event_sync(LogLevelEnum.INFO, "After error", event_bus=event_bus)

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
                target=emit_log_event_sync,
                args=(LogLevelEnum.INFO, f"Concurrent message {i}"),
                kwargs={"event_bus": event_bus},
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
