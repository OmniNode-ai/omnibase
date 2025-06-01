"""
Telemetry subscriber utility for ONEX node telemetry events.

This module provides utilities to subscribe to telemetry decorator events/logs
and print/process them in real time for local development and CI use.
"""
import json
import sys
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO
from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevel
from omnibase.model.model_onex_event import OnexEventTypeEnum
_COMPONENT_NAME = Path(__file__).stem
_IN_ERROR_HANDLER = False


class TelemetryOutputFormat(Enum):
    """Output format options for telemetry subscriber."""
    JSON = 'json'
    STRUCTURED = 'structured'
    COMPACT = 'compact'
    TABLE = 'table'


class TelemetrySubscriber:
    """
    Real-time telemetry event subscriber and processor.

    This subscriber can capture telemetry events from the logging system
    and process them in various formats for monitoring and debugging.
    """

    def __init__(self, output_format: TelemetryOutputFormat=
        TelemetryOutputFormat.STRUCTURED, output_stream: Optional[TextIO]=
        None, filter_correlation_ids: Optional[List[str]]=None,
        filter_node_ids: Optional[List[str]]=None, filter_operations:
        Optional[List[str]]=None, show_timestamps: bool=True,
        show_execution_times: bool=True, color_output: bool=True):
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
        self.color_output = color_output and hasattr(sys.stdout, 'isatty'
            ) and sys.stdout.isatty()
        self._active_operations: Dict[str, Dict[str, Any]] = {}
        self._event_bus: Optional[Any] = None
        self._is_monitoring: bool = False

    def start_monitoring(self, event_bus: Optional[Any]=None) ->None:
        """
        Start monitoring telemetry events from the event bus.

        Args:
            event_bus: Event bus to subscribe to (optional, will use global if not provided)
        """
        if self._is_monitoring:
            raise OnexError('Subscriber is already monitoring',
                CoreErrorCode.INVALID_STATE)
        if event_bus is None:
            from omnibase.core.core_structured_logging import get_global_event_bus
            event_bus = get_global_event_bus()
        if event_bus is None:
            raise OnexError('No event bus available for telemetry monitoring',
                CoreErrorCode.DEPENDENCY_UNAVAILABLE)
        self._event_bus = event_bus
        self._event_bus.subscribe(self._process_event)
        self._is_monitoring = True
        emit_log_event(LogLevel.INFO,
            'Started monitoring telemetry events from event bus', node_id=
            _COMPONENT_NAME, event_bus=self._event_bus)
        self._write_output(
            '🔍 Started monitoring telemetry events from event bus')

    def stop_monitoring(self) ->None:
        """Stop monitoring telemetry events."""
        if self._is_monitoring and self._event_bus is not None:
            self._event_bus.unsubscribe(self._process_event)
            emit_log_event(LogLevel.INFO,
                'Stopped monitoring telemetry events', node_id=
                _COMPONENT_NAME, event_bus=self._event_bus)
            self._event_bus = None
            self._is_monitoring = False
            self._write_output('⏹️  Stopped monitoring telemetry events')

    def _process_event(self, event: Any) ->None:
        """
        Process a telemetry event from the event bus.

        Args:
            event: The OnexEvent containing telemetry data
        """
        try:
            if not hasattr(event, 'event_type') or not str(event.event_type
                ).startswith('TELEMETRY'):
                return
            event_data = {'event_type': event.event_type, 'correlation_id':
                getattr(event, 'correlation_id', None), 'node_id': getattr(
                event, 'node_id', None), 'operation': getattr(event,
                'metadata', {}).get('operation', None), 'timestamp':
                getattr(event, 'timestamp', None), 'metadata': getattr(
                event, 'metadata', {}), 'message': getattr(event,
                'metadata', {}).get('message', '')}
            if not self._should_process_event(event_data):
                return
            self._track_operation(event_data)
            self._output_event(event_data)
        except Exception as e:
            emit_log_event(LogLevel.ERROR,
                f'Error processing telemetry event: {e}', node_id=
                _COMPONENT_NAME, event_bus=self._event_bus)
            self._write_output(f'❌ Error processing telemetry event: {e}')

    def _should_process_event(self, event_data: Dict[str, Any]) ->bool:
        """Check if an event should be processed based on filters."""
        correlation_id = event_data.get('correlation_id')
        node_id = event_data.get('node_id')
        operation = event_data.get('operation')
        if (self.filter_correlation_ids and correlation_id not in self.
            filter_correlation_ids):
            return False
        if self.filter_node_ids and node_id not in self.filter_node_ids:
            return False
        if self.filter_operations and operation not in self.filter_operations:
            return False
        return True

    def _track_operation(self, event_data: Dict[str, Any]) ->None:
        """Track active operations for timing calculations."""
        correlation_id = event_data.get('correlation_id')
        event_type = event_data.get('event_type')
        if not correlation_id:
            return
        if event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START:
            self._active_operations[correlation_id] = {'start_time': time.
                time(), 'node_id': event_data.get('node_id'), 'operation':
                event_data.get('operation'), 'function': event_data.get(
                'metadata', {}).get('function')}
        elif event_type in [OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS,
            OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR]:
            if correlation_id in self._active_operations:
                start_info = self._active_operations.pop(correlation_id)
                total_time = time.time() - start_info['start_time']
                event_data['total_execution_time_ms'] = round(total_time * 
                    1000, 2)

    def _output_event(self, event_data: Dict[str, Any]) ->None:
        """Output a telemetry event in the specified format."""
        if self.output_format == TelemetryOutputFormat.JSON:
            self._output_json(event_data)
        elif self.output_format == TelemetryOutputFormat.STRUCTURED:
            self._output_structured(event_data)
        elif self.output_format == TelemetryOutputFormat.COMPACT:
            self._output_compact(event_data)
        elif self.output_format == TelemetryOutputFormat.TABLE:
            self._output_table(event_data)

    def _output_json(self, event_data: Dict[str, Any]) ->None:
        """Output event as JSON."""
        json_data = {}
        for key, value in event_data.items():
            if isinstance(value, datetime):
                json_data[key] = value.isoformat()
            elif hasattr(value, 'value'):
                json_data[key] = value.value
            else:
                json_data[key] = value
        self._write_output(json.dumps(json_data, indent=2))

    def _output_structured(self, event_data: Dict[str, Any]) ->None:
        """Output event in structured format."""
        event_type = event_data.get('event_type', 'UNKNOWN')
        correlation_id = event_data.get('correlation_id', 'N/A')
        node_id = event_data.get('node_id', 'N/A')
        operation = event_data.get('operation', 'N/A')
        if self.color_output:
            if event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_START:
                color = '\x1b[94m'
                symbol = '🚀'
            elif event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS:
                color = '\x1b[92m'
                symbol = '✅'
            elif event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR:
                color = '\x1b[91m'
                symbol = '❌'
            else:
                color = '\x1b[0m'
                symbol = '📊'
            reset = '\x1b[0m'
        else:
            color = reset = ''
            symbol = {'TELEMETRY_OPERATION_START': '[START]',
                'TELEMETRY_OPERATION_SUCCESS': '[SUCCESS]',
                'TELEMETRY_OPERATION_ERROR': '[ERROR]'}.get(str(event_type),
                '[EVENT]')
        parts = [f'{color}{symbol} {event_type}{reset}']
        if self.show_timestamps and event_data.get('timestamp'):
            timestamp = event_data['timestamp']
            if isinstance(timestamp, datetime):
                time_str = timestamp.strftime('%H:%M:%S.%f')[:-3]
            else:
                time_str = str(timestamp)
            parts.append(f'[{time_str}]')
        parts.append(f'{node_id}::{operation}')
        parts.append(f'({correlation_id[:8]})')
        if self.show_execution_times:
            exec_time = event_data.get('total_execution_time_ms'
                ) or event_data.get('metadata', {}).get('execution_time_ms')
            if exec_time:
                parts.append(f'({exec_time}ms)')
        if event_type == OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR:
            metadata = event_data.get('metadata', {})
            error_type = metadata.get('error_type', 'Unknown')
            error_msg = metadata.get('error_message', 'No message')
            parts.append(f'- {error_type}: {error_msg}')
        self._write_output(' '.join(parts))

    def _output_compact(self, event_data: Dict[str, Any]) ->None:
        """Output event in compact format."""
        event_type = event_data.get('event_type', 'UNKNOWN')
        if hasattr(event_type, 'value'):
            event_type_str = event_type.value
        else:
            event_type_str = str(event_type)
        correlation_id = event_data.get('correlation_id', 'N/A')[:8]
        operation = event_data.get('operation', 'N/A')
        symbol_map = {'TELEMETRY_OPERATION_START': '▶',
            'TELEMETRY_OPERATION_SUCCESS': '✓', 'TELEMETRY_OPERATION_ERROR':
            '✗'}
        symbol = symbol_map.get(event_type_str, '•')
        exec_time = event_data.get('total_execution_time_ms'
            ) or event_data.get('metadata', {}).get('execution_time_ms')
        time_str = f' {exec_time}ms' if exec_time else ''
        self._write_output(f'{symbol} {operation} ({correlation_id}){time_str}'
            )

    def _output_table(self, event_data: Dict[str, Any]) ->None:
        """Output event in table format."""
        event_type = str(event_data.get('event_type', 'UNKNOWN')).replace(
            'TELEMETRY_OPERATION_', '')
        correlation_id = event_data.get('correlation_id', 'N/A')[:12]
        node_id = event_data.get('node_id', 'N/A')[:15]
        operation = event_data.get('operation', 'N/A')[:20]
        exec_time = event_data.get('total_execution_time_ms'
            ) or event_data.get('metadata', {}).get('execution_time_ms')
        time_str = f'{exec_time:>8.2f}ms' if exec_time else '        -'
        timestamp = ''
        if self.show_timestamps and event_data.get('timestamp'):
            ts = event_data['timestamp']
            if isinstance(ts, datetime):
                timestamp = ts.strftime('%H:%M:%S')
            else:
                timestamp = str(ts)[:8]
        self._write_output(
            f'{timestamp:>8} | {event_type:>8} | {correlation_id:>12} | {node_id:>15} | {operation:>20} | {time_str}'
            )

    def _write_output(self, message: str) ->None:
        """Write a message to the output stream."""
        try:
            self.output_stream.write(message + '\n')
            self.output_stream.flush()
        except Exception as e:
            try:
                sys.stderr.write(f'Telemetry output error: {e}\n')
                sys.stderr.write(f'Original message: {message}\n')
                sys.stderr.flush()
            except Exception:
                pass


def create_cli_subscriber(format_type: str='structured', correlation_id:
    Optional[str]=None, node_id: Optional[str]=None, operation: Optional[
    str]=None, no_color: bool=False, no_timestamps: bool=False,
    no_execution_times: bool=False) ->TelemetrySubscriber:
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
    except OnexError:
        output_format = TelemetryOutputFormat.STRUCTURED
    return TelemetrySubscriber(output_format=output_format,
        filter_correlation_ids=[correlation_id] if correlation_id else None,
        filter_node_ids=[node_id] if node_id else None, filter_operations=[
        operation] if operation else None, show_timestamps=not
        no_timestamps, show_execution_times=not no_execution_times,
        color_output=not no_color)


def monitor_telemetry_realtime(duration_seconds: Optional[int]=None, **
    subscriber_kwargs: Any) ->None:
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
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
    finally:
        subscriber.stop_monitoring()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=
        'Monitor ONEX telemetry events')
    parser.add_argument('--format', choices=['json', 'structured',
        'compact', 'table'], default='structured', help='Output format')
    parser.add_argument('--correlation-id', help='Filter by correlation ID')
    parser.add_argument('--node-id', help='Filter by node ID')
    parser.add_argument('--operation', help='Filter by operation')
    parser.add_argument('--duration', type=int, help=
        'Monitor duration in seconds')
    parser.add_argument('--no-color', action='store_true', help=
        'Disable colored output')
    parser.add_argument('--no-timestamps', action='store_true', help=
        'Hide timestamps')
    parser.add_argument('--no-execution-times', action='store_true', help=
        'Hide execution times')
    args = parser.parse_args()
    subscriber = create_cli_subscriber(format_type=args.format,
        correlation_id=args.correlation_id, node_id=args.node_id, operation
        =args.operation, no_color=args.no_color, no_timestamps=args.
        no_timestamps, no_execution_times=args.no_execution_times)
    try:
        subscriber.start_monitoring()
        emit_log_event(LogLevel.INFO,
            f'Monitoring telemetry events (format: {args.format})...',
            node_id=_COMPONENT_NAME, event_bus=self._event_bus)
        emit_log_event(LogLevel.INFO, 'Press Ctrl+C to stop', node_id=
            _COMPONENT_NAME, event_bus=self._event_bus)
        if args.duration:
            time.sleep(args.duration)
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        emit_log_event(LogLevel.INFO,
            'Stopping telemetry monitoring...', node_id=_COMPONENT_NAME,
            event_bus=self._event_bus)
    finally:
        subscriber.stop_monitoring()
