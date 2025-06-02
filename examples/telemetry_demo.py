# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: telemetry_demo.py
# version: 1.0.0
# uuid: 059b311c-4a91-40a0-b5bb-2d7369f03a43
# author: OmniNode Team
# created_at: 2025-05-25T13:48:20.304790
# last_modified_at: 2025-05-25T17:51:16.328501
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: faf2a6cc2bc1556dbbd5d4b74ec898d04a75f5eba5f76fd9dbaf210557286330
# entrypoint: python@telemetry_demo.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.telemetry_demo
# meta_type: tool
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Demonstration of the ONEX telemetry subscriber utility.

This script shows how to use the telemetry subscriber to monitor
telemetry events from ONEX nodes in real-time.
"""

import time
from datetime import datetime

from omnibase.model.model_onex_event import OnexEvent, OnexEventTypeEnum
from omnibase.runtimes.onex_runtime.v1_0_0.telemetry import (
    TelemetryOutputFormat,
    TelemetrySubscriber,
    _emit_event,
    clear_telemetry_handlers,
    create_cli_subscriber,
    register_telemetry_handler,
    TelemetryOperationStartMetadataModel,
    TelemetryOperationSuccessMetadataModel,
    TelemetryOperationErrorMetadataModel,
)


def demo_basic_subscriber() -> None:
    """Demonstrate basic telemetry subscriber functionality."""
    print("🔍 Demo: Basic Telemetry Subscriber")
    print("=" * 50)

    # Create a subscriber with structured output
    subscriber = TelemetrySubscriber(
        output_format=TelemetryOutputFormat.STRUCTURED,
        color_output=True,
    )

    # Start monitoring
    subscriber.start_monitoring()

    # Simulate some telemetry events
    events = [
        OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            correlation_id="demo-123",
            node_id="stamper_node",
            timestamp=datetime.utcnow(),
            metadata=TelemetryOperationStartMetadataModel(
                operation="process_file",
                function="run_stamper_node",
                args_count=2,
                kwargs_keys=[],
            ),
        ),
        OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
            correlation_id="demo-123",
            node_id="stamper_node",
            timestamp=datetime.utcnow(),
            metadata=TelemetryOperationSuccessMetadataModel(
                operation="process_file",
                function="run_stamper_node",
                execution_time_ms=125.5,
                result_type="StamperOutputState",
                success=True,
            ),
        ),
    ]

    print("Emitting telemetry events...")
    for event in events:
        _emit_event(event)
        time.sleep(0.1)  # Small delay for demonstration

    # Stop monitoring
    subscriber.stop_monitoring()
    print("\n")


def demo_filtered_subscriber() -> None:
    """Demonstrate filtered telemetry subscriber."""
    print("🔍 Demo: Filtered Telemetry Subscriber")
    print("=" * 50)

    # Create a subscriber that only shows events from stamper_node
    subscriber = TelemetrySubscriber(
        output_format=TelemetryOutputFormat.COMPACT,
        filter_node_ids=["stamper_node"],
        color_output=False,
    )

    subscriber.start_monitoring()

    # Emit events from different nodes
    events = [
        OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            correlation_id="filter-test-1",
            node_id="stamper_node",
            timestamp=datetime.utcnow(),
            metadata=TelemetryOperationStartMetadataModel(
                operation="stamp_file",
                function=None,
                args_count=None,
                kwargs_keys=[],
            ),
        ),
        OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            correlation_id="filter-test-2",
            node_id="other_node",
            timestamp=datetime.utcnow(),
            metadata=TelemetryOperationStartMetadataModel(
                operation="other_operation",
                function=None,
                args_count=None,
                kwargs_keys=[],
            ),
        ),
        OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
            correlation_id="filter-test-1",
            node_id="stamper_node",
            timestamp=datetime.utcnow(),
            metadata=TelemetryOperationSuccessMetadataModel(
                operation="stamp_file",
                function=None,
                execution_time_ms=50.0,
                result_type=None,
                success=True,
            ),
        ),
    ]

    print("Emitting events from different nodes (only stamper_node should be shown)...")
    for event in events:
        _emit_event(event)
        time.sleep(0.1)

    subscriber.stop_monitoring()
    print("\n")


def demo_json_output() -> None:
    """Demonstrate JSON output format."""
    print("🔍 Demo: JSON Output Format")
    print("=" * 50)

    subscriber = TelemetrySubscriber(
        output_format=TelemetryOutputFormat.JSON,
    )

    subscriber.start_monitoring()

    # Emit a single event
    event = OnexEvent(
        event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR,
        correlation_id="json-demo",
        node_id="stamper_node",
        timestamp=datetime.utcnow(),
        metadata=TelemetryOperationErrorMetadataModel(
            operation="process_file",
            function=None,
            execution_time_ms=25.0,
            error_type="FileNotFoundError",
            error_message="File not found: test.py",
            success=False,
        ),
    )

    print("Emitting error event in JSON format...")
    _emit_event(event)

    subscriber.stop_monitoring()
    print("\n")


def demo_cli_subscriber() -> None:
    """Demonstrate CLI subscriber creation."""
    print("🔍 Demo: CLI Subscriber")
    print("=" * 50)

    # Create a CLI subscriber with custom settings
    subscriber = create_cli_subscriber(
        format_type="table",
        correlation_id="cli-demo",
        no_color=True,
        no_timestamps=False,
    )

    subscriber.start_monitoring()

    # Emit events with the matching correlation ID
    events = [
        OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            correlation_id="cli-demo",
            node_id="stamper_node",
            timestamp=datetime.utcnow(),
            metadata=TelemetryOperationStartMetadataModel(
                operation="validate_file",
                function=None,
                args_count=None,
                kwargs_keys=[],
            ),
        ),
        OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
            correlation_id="cli-demo",
            node_id="stamper_node",
            timestamp=datetime.utcnow(),
            metadata=TelemetryOperationSuccessMetadataModel(
                operation="validate_file",
                function=None,
                execution_time_ms=75.25,
                result_type=None,
                success=True,
            ),
        ),
        OnexEvent(
            event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
            correlation_id="other-correlation",
            node_id="stamper_node",
            timestamp=datetime.utcnow(),
            metadata=TelemetryOperationStartMetadataModel(
                operation="other_operation",
                function=None,
                args_count=None,
                kwargs_keys=[],
            ),
        ),
    ]

    print("Emitting events (only cli-demo correlation ID should be shown)...")
    for event in events:
        _emit_event(event)
        time.sleep(0.1)

    subscriber.stop_monitoring()
    print("\n")


def demo_event_bus_integration() -> None:
    """Demonstrate integration with the telemetry event bus."""
    print("🔍 Demo: Event Bus Integration")
    print("=" * 50)

    # Create a custom event handler
    captured_events = []

    def custom_handler(event: OnexEvent) -> None:
        captured_events.append(event)
        print(f"Custom handler received: {event.event_type} for {event.correlation_id}")

    # Register the custom handler
    register_telemetry_handler(custom_handler)

    # Also start a subscriber
    subscriber = TelemetrySubscriber(
        output_format=TelemetryOutputFormat.COMPACT,
        color_output=False,
    )
    subscriber.start_monitoring()

    # Emit an event
    event = OnexEvent(
        event_type=OnexEventTypeEnum.TELEMETRY_OPERATION_START,
        correlation_id="bus-demo",
        node_id="stamper_node",
        timestamp=datetime.utcnow(),
        metadata={"operation": "integration_test"},
    )

    print("Emitting event to both custom handler and subscriber...")
    _emit_event(event)

    # Clean up
    subscriber.stop_monitoring()
    clear_telemetry_handlers()

    print(f"Custom handler captured {len(captured_events)} events")
    print("\n")


def main() -> None:
    """Run all telemetry subscriber demonstrations."""
    print("🚀 ONEX Telemetry Subscriber Demonstrations")
    print("=" * 60)
    print()

    try:
        demo_basic_subscriber()
        demo_filtered_subscriber()
        demo_json_output()
        demo_cli_subscriber()
        demo_event_bus_integration()

        print("✅ All demonstrations completed successfully!")
        print()
        print("💡 Usage Tips:")
        print("- Use structured format for development debugging")
        print("- Use compact format for CI/production monitoring")
        print("- Use JSON format for log aggregation systems")
        print("- Use table format for dashboard displays")
        print("- Apply filters to focus on specific operations or nodes")

    except KeyboardInterrupt:
        print("\n⏹️  Demonstrations interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
    finally:
        # Clean up any remaining handlers
        clear_telemetry_handlers()


if __name__ == "__main__":
    main()
