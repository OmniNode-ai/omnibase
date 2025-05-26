# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: telemetry_subscriber.py
# version: 1.0.0
# uuid: 3fa07126-6917-466a-9a52-f63df6195c8f
# author: OmniNode Team
# created_at: 2025-05-25T13:44:55.577448
# last_modified_at: 2025-05-25T17:51:16.328901
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 587226e3a11217011ed16ba7888416839f0a13b1688ae185e5e6af6faa980e81
# entrypoint: python@telemetry_subscriber.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.telemetry_subscriber
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Telemetry subscriber utility for ONEX node telemetry events.

This module provides utilities to subscribe to telemetry decorator events/logs
and print/process them in real time for local development and CI use.
"""

import json
import logging
import sys
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TextIO

from omnibase.model.model_onex_event import OnexEventTypeEnum


class TelemetryOutputFormat(Enum):
    """Output format options for telemetry subscriber."""

    JSON = "json"
    STRUCTURED = "structured"
    COMPACT = "compact"
    TABLE = "table"


class TelemetrySubscriber:
    """
    Real-time telemetry event subscriber and processor.

    This subscriber can capture telemetry events from the logging system
    and process them in various formats for monitoring and debugging.
    """

    def __init__(
        self,
        output_format: TelemetryOutputFormat = TelemetryOutputFormat.STRUCTURED,
        output_stream: Optional[TextIO] = None,
        filter_correlation_ids: Optional[List[str]] = None,
        filter_node_ids: Optional[List[str]] = None,
        filter_operations: Optional[List[str]] = None,
        show_timestamps: bool = True,
        show_execution_times: bool = True,
        color_output: bool = True,
    ):
        """
        Initialize the telemetry subscriber.

        Args:
            output_format: Format for output (json, structured, compact, table)
            output_stream: Stream to write output to (defaults to stdout)
            filter_correlation_ids: Only show events with these correlation IDs
            filter_node_ids: Only show events from these nodes
            filter_operations: Only show events for these operations
            show_timestamps: Whether to include timestamps in output
            show_execution_times: Whether to show execution times
            color_output: Whether to use colored output (if supported)
        """
        self.output_format = output_format
        self.output_stream = output_stream or sys.stdout
        self.filter_correlation_ids = set(filter_correlation_ids or [])
        self.filter_node_ids = set(filter_node_ids or [])
        self.filter_operations = set(filter_operations or [])
        self.show_timestamps = show_timestamps
        self.show_execution_times = show_execution_times
        self.color_output = (
            color_output and hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
        )

        self._active_operations: Dict[str, Dict[str, Any]] = {}
        self._handler: Optional[TelemetryLogHandler] = None
        self._logger: Optional[logging.Logger] = None

    def start_monitoring(self, logger_name: str = "telemetry") -> None:
        """
        Start monitoring telemetry events from the specified logger.

        Args:
            logger_name: Name of the logger to monitor (default: "telemetry")
        """
        if self._handler is not None:
            raise RuntimeError("Subscriber is already monitoring")

        # Create and configure the log handler
        self._handler = TelemetryLogHandler(self._process_event)
        self._handler.setLevel(logging.INFO)

        # Get the telemetry logger and add our handler
        self._logger = logging.getLogger(logger_name)
        self._logger.addHandler(self._handler)
        self._logger.setLevel(logging.INFO)

        self._write_output(
            f"🔍 Started monitoring telemetry events from logger '{logger_name}'"
        )

    def stop_monitoring(self) -> None:
        """Stop monitoring telemetry events."""
        if self._handler is not None and self._logger is not None:
            self._logger.removeHandler(self._handler)
            self._handler = None
            self._logger = None
            self._write_output("⏹️  Stopped monitoring telemetry events")

    def _process_event(self, record: logging.LogRecord) -> None:
        """
        Process a telemetry log record.

        Args:
            record: The log record containing telemetry event data
        """
        try:
            # Extract event data from the log record
            event_data = {
                "event_type": getattr(record, "event_type", None),
                "correlation_id": getattr(record, "correlation_id", None),
                "node_id": getattr(record, "node_id", None),
                "operation": getattr(record, "operation", None),
                "timestamp": getattr(record, "timestamp", None),
                "metadata": getattr(record, "metadata", {}),
                "message": record.getMessage(),
            }

            # Apply filters
            if not self._should_process_event(event_data):
                return

            # Track active operations
            self._track_operation(event_data)

            # Format and output the event
            self._output_event(event_data)

        except Exception as e:
            self._write_output(f"❌ Error processing telemetry event: {e}")

    def _should_process_event(self, event_data: Dict[str, Any]) -> bool:
        """Check if an event should be processed based on filters."""
        correlation_id = event_data.get("correlation_id")
        node_id = event_data.get("node_id")
        operation = event_data.get("operation")

        # Apply correlation ID filter
        if (
            self.filter_correlation_ids
            and correlation_id not in self.filter_correlation_ids
        ):
            return False

        # Apply node ID filter
        if self.filter_node_ids and node_id not in self.filter_node_ids:
            return False

        # Apply operation filter
        if self.filter_operations and operation not in self.filter_operations:
            return False

        return True

    def _track_operation(self, event_data: Dict[str, Any]) -> None:
        """Track active operations for timing calculations."""
        correlation_id = event_data.get("correlation_id")
        event_type = event_data.get("event_type")

        if not correlation_id:
            return

        if event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START:
            self._active_operations[correlation_id] = {
                "start_time": time.time(),
                "node_id": event_data.get("node_id"),
                "operation": event_data.get("operation"),
                "function": event_data.get("metadata", {}).get("function"),
            }
        elif event_type in [
            OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
            OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR,
        ]:
            if correlation_id in self._active_operations:
                # Calculate total execution time
                start_info = self._active_operations.pop(correlation_id)
                total_time = time.time() - start_info["start_time"]
                event_data["total_execution_time_ms"] = round(total_time * 1000, 2)

    def _output_event(self, event_data: Dict[str, Any]) -> None:
        """Output a telemetry event in the specified format."""
        if self.output_format == TelemetryOutputFormat.JSON:
            self._output_json(event_data)
        elif self.output_format == TelemetryOutputFormat.STRUCTURED:
            self._output_structured(event_data)
        elif self.output_format == TelemetryOutputFormat.COMPACT:
            self._output_compact(event_data)
        elif self.output_format == TelemetryOutputFormat.TABLE:
            self._output_table(event_data)

    def _output_json(self, event_data: Dict[str, Any]) -> None:
        """Output event as JSON."""
        # Convert datetime objects to strings for JSON serialization
        json_data = {}
        for key, value in event_data.items():
            if isinstance(value, datetime):
                json_data[key] = value.isoformat()
            elif hasattr(value, "value"):  # Handle Enum types
                json_data[key] = value.value
            else:
                json_data[key] = value

        self._write_output(json.dumps(json_data, indent=2))

    def _output_structured(self, event_data: Dict[str, Any]) -> None:
        """Output event in structured format."""
        event_type = event_data.get("event_type", "UNKNOWN")
        correlation_id = event_data.get("correlation_id", "N/A")
        node_id = event_data.get("node_id", "N/A")
        operation = event_data.get("operation", "N/A")

        # Color coding for different event types
        if self.color_output:
            if event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START:
                color = "\033[94m"  # Blue
                symbol = "🚀"
            elif event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS:
                color = "\033[92m"  # Green
                symbol = "✅"
            elif event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR:
                color = "\033[91m"  # Red
                symbol = "❌"
            else:
                color = "\033[0m"  # Reset
                symbol = "📊"
            reset = "\033[0m"
        else:
            color = reset = ""
            symbol = {
                "TELEMETRY_OPERATION_START": "[START]",
                "TELEMETRY_OPERATION_SUCCESS": "[SUCCESS]",
                "TELEMETRY_OPERATION_ERROR": "[ERROR]",
            }.get(str(event_type), "[EVENT]")

        # Build the output line
        parts = [f"{color}{symbol} {event_type}{reset}"]

        if self.show_timestamps and event_data.get("timestamp"):
            timestamp = event_data["timestamp"]
            if isinstance(timestamp, datetime):
                time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
            else:
                time_str = str(timestamp)
            parts.append(f"[{time_str}]")

        parts.append(f"{node_id}::{operation}")
        parts.append(f"({correlation_id[:8]})")

        # Add execution time if available
        if self.show_execution_times:
            exec_time = event_data.get("total_execution_time_ms") or event_data.get(
                "metadata", {}
            ).get("execution_time_ms")
            if exec_time:
                parts.append(f"({exec_time}ms)")

        # Add error information for error events
        if event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR:
            metadata = event_data.get("metadata", {})
            error_type = metadata.get("error_type", "Unknown")
            error_msg = metadata.get("error_message", "No message")
            parts.append(f"- {error_type}: {error_msg}")

        self._write_output(" ".join(parts))

    def _output_compact(self, event_data: Dict[str, Any]) -> None:
        """Output event in compact format."""
        event_type = event_data.get("event_type", "UNKNOWN")
        # Handle enum values properly
        if hasattr(event_type, "value"):
            event_type_str = event_type.value
        else:
            event_type_str = str(event_type)

        correlation_id = event_data.get("correlation_id", "N/A")[:8]
        operation = event_data.get("operation", "N/A")

        # Compact symbols
        symbol_map = {
            "TELEMETRY_OPERATION_START": "▶",
            "TELEMETRY_OPERATION_SUCCESS": "✓",
            "TELEMETRY_OPERATION_ERROR": "✗",
        }
        symbol = symbol_map.get(event_type_str, "•")

        exec_time = event_data.get("total_execution_time_ms") or event_data.get(
            "metadata", {}
        ).get("execution_time_ms")
        time_str = f" {exec_time}ms" if exec_time else ""

        self._write_output(f"{symbol} {operation} ({correlation_id}){time_str}")

    def _output_table(self, event_data: Dict[str, Any]) -> None:
        """Output event in table format."""
        # This is a simplified table format - a full implementation would maintain column alignment
        event_type = str(event_data.get("event_type", "UNKNOWN")).replace(
            "TELEMETRY_OPERATION_", ""
        )
        correlation_id = event_data.get("correlation_id", "N/A")[:12]
        node_id = event_data.get("node_id", "N/A")[:15]
        operation = event_data.get("operation", "N/A")[:20]

        exec_time = event_data.get("total_execution_time_ms") or event_data.get(
            "metadata", {}
        ).get("execution_time_ms")
        time_str = f"{exec_time:>8.2f}ms" if exec_time else "        -"

        timestamp = ""
        if self.show_timestamps and event_data.get("timestamp"):
            ts = event_data["timestamp"]
            if isinstance(ts, datetime):
                timestamp = ts.strftime("%H:%M:%S")
            else:
                timestamp = str(ts)[:8]

        self._write_output(
            f"{timestamp:>8} | {event_type:>8} | {correlation_id:>12} | {node_id:>15} | {operation:>20} | {time_str}"
        )

    def _write_output(self, message: str) -> None:
        """Write a message to the output stream."""
        try:
            self.output_stream.write(message + "\n")
            self.output_stream.flush()
        except Exception as e:
            # Fallback to stderr if output stream fails
            sys.stderr.write(f"Telemetry output error: {e}\n")


class TelemetryLogHandler(logging.Handler):
    """Custom log handler for capturing telemetry events."""

    def __init__(self, event_processor: Callable[[logging.LogRecord], None]):
        """
        Initialize the telemetry log handler.

        Args:
            event_processor: Function to process log records
        """
        super().__init__()
        self.event_processor = event_processor

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to the event processor.

        Args:
            record: The log record to process
        """
        try:
            self.event_processor(record)
        except Exception:
            # Don't let telemetry processing break the main application
            pass


def create_cli_subscriber(
    format_type: str = "structured",
    correlation_id: Optional[str] = None,
    node_id: Optional[str] = None,
    operation: Optional[str] = None,
    no_color: bool = False,
    no_timestamps: bool = False,
    no_execution_times: bool = False,
) -> TelemetrySubscriber:
    """
    Create a telemetry subscriber configured for CLI use.

    Args:
        format_type: Output format (json, structured, compact, table)
        correlation_id: Filter by correlation ID
        node_id: Filter by node ID
        operation: Filter by operation name
        no_color: Disable colored output
        no_timestamps: Hide timestamps
        no_execution_times: Hide execution times

    Returns:
        Configured TelemetrySubscriber instance
    """
    try:
        output_format = TelemetryOutputFormat(format_type)
    except ValueError:
        output_format = TelemetryOutputFormat.STRUCTURED

    return TelemetrySubscriber(
        output_format=output_format,
        filter_correlation_ids=[correlation_id] if correlation_id else None,
        filter_node_ids=[node_id] if node_id else None,
        filter_operations=[operation] if operation else None,
        show_timestamps=not no_timestamps,
        show_execution_times=not no_execution_times,
        color_output=not no_color,
    )


def monitor_telemetry_realtime(
    duration_seconds: Optional[int] = None, **subscriber_kwargs: Any
) -> None:
    """
    Monitor telemetry events in real-time for a specified duration.

    Args:
        duration_seconds: How long to monitor (None for indefinite)
        **subscriber_kwargs: Arguments to pass to TelemetrySubscriber
    """
    subscriber = TelemetrySubscriber(**subscriber_kwargs)

    try:
        subscriber.start_monitoring()

        if duration_seconds:
            time.sleep(duration_seconds)
        else:
            # Monitor until interrupted
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
    finally:
        subscriber.stop_monitoring()


if __name__ == "__main__":
    # Simple CLI interface for testing
    import argparse

    parser = argparse.ArgumentParser(description="Monitor ONEX telemetry events")
    parser.add_argument(
        "--format",
        choices=["json", "structured", "compact", "table"],
        default="structured",
        help="Output format",
    )
    parser.add_argument("--correlation-id", help="Filter by correlation ID")
    parser.add_argument("--node-id", help="Filter by node ID")
    parser.add_argument("--operation", help="Filter by operation")
    parser.add_argument("--duration", type=int, help="Monitor duration in seconds")
    parser.add_argument(
        "--no-color", action="store_true", help="Disable colored output"
    )
    parser.add_argument("--no-timestamps", action="store_true", help="Hide timestamps")
    parser.add_argument(
        "--no-execution-times", action="store_true", help="Hide execution times"
    )

    args = parser.parse_args()

    subscriber = create_cli_subscriber(
        format_type=args.format,
        correlation_id=args.correlation_id,
        node_id=args.node_id,
        operation=args.operation,
        no_color=args.no_color,
        no_timestamps=args.no_timestamps,
        no_execution_times=args.no_execution_times,
    )

    try:
        subscriber.start_monitoring()
        print(f"Monitoring telemetry events (format: {args.format})...")
        print("Press Ctrl+C to stop")

        if args.duration:
            time.sleep(args.duration)
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping telemetry monitoring...")
    finally:
        subscriber.stop_monitoring()
