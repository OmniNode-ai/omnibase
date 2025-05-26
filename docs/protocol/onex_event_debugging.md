<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: onex_event_debugging.md
version: 1.0.0
uuid: e6b04020-800c-4c5a-9175-b7791a47a37c
author: OmniNode Team
created_at: 2025-05-25T14:16:19.608891
last_modified_at: 2025-05-25T18:17:32.897205
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: f4b95cc75559c7cb7cce55392209c90576cf06ddacf4d7aed4bcbb3d9bef3162
entrypoint: python@onex_event_debugging.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.onex_event_debugging
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Event Debugging and Observability Patterns

> **Version:** 1.0.0  
> **Status:** Draft  
> **Last Updated:** 2025-05-25  
> **Purpose:** Debugging techniques and observability patterns for the ONEX event system

## Overview

This document provides comprehensive debugging techniques and observability patterns for the ONEX event system. It covers event tracing, correlation analysis, performance debugging, and troubleshooting common issues.

## Event Tracing and Correlation

### Correlation ID Tracking

#### End-to-End Tracing

```python
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class EventTrace:
    correlation_id: str
    events: List[OnexEvent] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def add_event(self, event: OnexEvent):
        self.events.append(event)
        
        if self.start_time is None:
            self.start_time = event.timestamp
        
        self.end_time = event.timestamp
    
    def get_duration_ms(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None
    
    def get_event_chain(self) -> List[str]:
        return [event.event_type for event in self.events]

class EventTracer:
    def __init__(self):
        self.traces: Dict[str, EventTrace] = {}
    
    def track_event(self, event: OnexEvent):
        correlation_id = event.correlation_id
        
        if correlation_id not in self.traces:
            self.traces[correlation_id] = EventTrace(correlation_id=correlation_id)
        
        self.traces[correlation_id].add_event(event)
    
    def get_trace(self, correlation_id: str) -> Optional[EventTrace]:
        return self.traces.get(correlation_id)
    
    def get_incomplete_traces(self, timeout_minutes: int = 30) -> List[EventTrace]:
        """Find traces that haven't completed within timeout."""
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        
        incomplete = []
        for trace in self.traces.values():
            if trace.end_time and trace.end_time < cutoff_time:
                # Check if trace has success/failure event
                event_types = {event.event_type for event in trace.events}
                if not (OnexEventTypeEnum.NODE_SUCCESS in event_types or 
                       OnexEventTypeEnum.NODE_FAILURE in event_types):
                    incomplete.append(trace)
        
        return incomplete
```

#### Cross-Node Correlation

```python
class CrossNodeTracer:
    def __init__(self):
        self.node_interactions: Dict[str, List[str]] = {}
        self.correlation_graph: Dict[str, Set[str]] = {}
    
    def track_node_interaction(self, correlation_id: str, from_node: str, to_node: str):
        """Track when one node triggers another."""
        if correlation_id not in self.node_interactions:
            self.node_interactions[correlation_id] = []
        
        self.node_interactions[correlation_id].append(f"{from_node} -> {to_node}")
        
        # Build correlation graph
        if correlation_id not in self.correlation_graph:
            self.correlation_graph[correlation_id] = set()
        
        self.correlation_graph[correlation_id].add(from_node)
        self.correlation_graph[correlation_id].add(to_node)
    
    def get_interaction_chain(self, correlation_id: str) -> List[str]:
        return self.node_interactions.get(correlation_id, [])
    
    def get_involved_nodes(self, correlation_id: str) -> Set[str]:
        return self.correlation_graph.get(correlation_id, set())
```

### Event Flow Visualization

#### Flow Diagram Generator

```python
import graphviz
from typing import Dict, List

class EventFlowVisualizer:
    def __init__(self):
        self.flows: Dict[str, List[OnexEvent]] = {}
    
    def add_event_flow(self, correlation_id: str, events: List[OnexEvent]):
        self.flows[correlation_id] = events
    
    def generate_flow_diagram(self, correlation_id: str) -> str:
        """Generate Graphviz DOT notation for event flow."""
        events = self.flows.get(correlation_id, [])
        if not events:
            return ""
        
        dot = graphviz.Digraph(comment=f'Event Flow: {correlation_id}')
        dot.attr(rankdir='TB')
        
        # Add nodes
        for i, event in enumerate(events):
            node_id = f"event_{i}"
            label = f"{event.event_type}\\n{event.node_id}\\n{event.timestamp}"
            
            # Color based on event type
            color = self._get_event_color(event.event_type)
            dot.node(node_id, label, style='filled', fillcolor=color)
            
            # Add edge to next event
            if i < len(events) - 1:
                next_node_id = f"event_{i+1}"
                dot.edge(node_id, next_node_id)
        
        return dot.source
    
    def _get_event_color(self, event_type: OnexEventTypeEnum) -> str:
        color_map = {
            OnexEventTypeEnum.NODE_START: 'lightblue',
            OnexEventTypeEnum.NODE_SUCCESS: 'lightgreen',
            OnexEventTypeEnum.NODE_FAILURE: 'lightcoral',
            OnexEventTypeEnum.TELEMETRY_OPERATION_START: 'lightyellow',
            OnexEventTypeEnum.TELEMETRY_OPERATION_SUCCESS: 'lightgreen',
            OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR: 'lightcoral'
        }
        return color_map.get(event_type, 'lightgray')
```

## Performance Debugging

### Event Timing Analysis

```python
from collections import defaultdict
import statistics

class EventPerformanceAnalyzer:
    def __init__(self):
        self.operation_times: Dict[str, List[float]] = defaultdict(list)
        self.node_performance: Dict[str, List[float]] = defaultdict(list)
        self.event_sizes: Dict[str, List[int]] = defaultdict(list)
    
    def analyze_event(self, event: OnexEvent):
        # Track operation duration
        if 'duration_ms' in event.metadata:
            duration = event.metadata['duration_ms']
            operation = event.metadata.get('operation', 'unknown')
            
            self.operation_times[operation].append(duration)
            self.node_performance[event.node_id].append(duration)
        
        # Track event size
        event_size = len(str(event.model_dump()))
        self.event_sizes[event.event_type].append(event_size)
    
    def get_performance_stats(self, operation: str) -> Dict[str, float]:
        times = self.operation_times.get(operation, [])
        if not times:
            return {}
        
        return {
            'count': len(times),
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'p95_ms': self._percentile(times, 95),
            'p99_ms': self._percentile(times, 99),
            'min_ms': min(times),
            'max_ms': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def get_slow_operations(self, threshold_ms: float = 1000) -> List[str]:
        slow_ops = []
        for operation, times in self.operation_times.items():
            if times and statistics.mean(times) > threshold_ms:
                slow_ops.append(operation)
        return slow_ops
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
```

### Memory Usage Tracking

```python
import psutil
import gc
from typing import Dict, List

class EventMemoryTracker:
    def __init__(self):
        self.memory_snapshots: List[Dict[str, float]] = []
        self.event_memory_impact: Dict[str, List[float]] = defaultdict(list)
    
    def track_event_memory(self, event: OnexEvent):
        # Take memory snapshot before processing
        memory_before = self._get_memory_usage()
        
        # Process event (placeholder)
        self._process_event(event)
        
        # Take memory snapshot after processing
        memory_after = self._get_memory_usage()
        
        # Calculate memory impact
        memory_delta = memory_after['rss'] - memory_before['rss']
        self.event_memory_impact[event.event_type].append(memory_delta)
        
        # Store snapshot
        snapshot = {
            'timestamp': event.timestamp,
            'event_type': event.event_type,
            'memory_before_mb': memory_before['rss'],
            'memory_after_mb': memory_after['rss'],
            'memory_delta_mb': memory_delta
        }
        self.memory_snapshots.append(snapshot)
    
    def _get_memory_usage(self) -> Dict[str, float]:
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
        }
    
    def _process_event(self, event: OnexEvent):
        # Placeholder for actual event processing
        pass
    
    def get_memory_leaks(self, threshold_mb: float = 10) -> List[str]:
        """Identify event types that consistently increase memory usage."""
        leaky_events = []
        
        for event_type, deltas in self.event_memory_impact.items():
            if deltas and statistics.mean(deltas) > threshold_mb:
                leaky_events.append(event_type)
        
        return leaky_events
    
    def force_garbage_collection(self):
        """Force garbage collection and return collected objects."""
        collected = gc.collect()
        return collected
```

## Error Analysis and Debugging

### Error Pattern Detection

```python
from collections import Counter
import re

class ErrorPatternAnalyzer:
    def __init__(self):
        self.error_patterns: Dict[str, List[OnexEvent]] = defaultdict(list)
        self.error_frequencies: Counter = Counter()
        self.error_correlations: Dict[str, Set[str]] = defaultdict(set)
    
    def analyze_error_event(self, event: OnexEvent):
        if event.event_type not in [OnexEventTypeEnum.NODE_FAILURE, OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR]:
            return
        
        error_msg = event.metadata.get('error', '')
        error_type = event.metadata.get('error_type', 'Unknown')
        
        # Extract error pattern
        pattern = self._extract_error_pattern(error_msg)
        
        # Track pattern
        self.error_patterns[pattern].append(event)
        self.error_frequencies[pattern] += 1
        
        # Track correlations
        self.error_correlations[pattern].add(event.node_id)
        self.error_correlations[pattern].add(error_type)
    
    def _extract_error_pattern(self, error_msg: str) -> str:
        """Extract generic pattern from error message."""
        # Replace specific values with placeholders
        patterns = [
            (r'\d+', '<NUMBER>'),
            (r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '<UUID>'),
            (r'/[^\s]+', '<PATH>'),
            (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '<EMAIL>'),
            (r'https?://[^\s]+', '<URL>')
        ]
        
        pattern = error_msg
        for regex, replacement in patterns:
            pattern = re.sub(regex, replacement, pattern)
        
        return pattern
    
    def get_top_error_patterns(self, limit: int = 10) -> List[tuple]:
        """Get most frequent error patterns."""
        return self.error_frequencies.most_common(limit)
    
    def get_error_hotspots(self) -> Dict[str, int]:
        """Get nodes with most errors."""
        node_errors = Counter()
        
        for events in self.error_patterns.values():
            for event in events:
                node_errors[event.node_id] += 1
        
        return dict(node_errors)
```

### Event Validation Debugging

```python
class EventValidationDebugger:
    def __init__(self):
        self.validation_errors: List[Dict[str, any]] = []
        self.schema_violations: Dict[str, List[str]] = defaultdict(list)
    
    def debug_validation_failure(self, event_data: dict, validation_error: Exception):
        """Debug why event validation failed."""
        debug_info = {
            'timestamp': datetime.now(),
            'event_data': event_data,
            'error_type': type(validation_error).__name__,
            'error_message': str(validation_error),
            'missing_fields': self._find_missing_fields(event_data),
            'invalid_fields': self._find_invalid_fields(event_data),
            'schema_violations': self._find_schema_violations(event_data)
        }
        
        self.validation_errors.append(debug_info)
        
        # Track schema violations
        for violation in debug_info['schema_violations']:
            self.schema_violations[violation['field']].append(violation['issue'])
    
    def _find_missing_fields(self, event_data: dict) -> List[str]:
        required_fields = ['event_id', 'timestamp', 'node_id', 'event_type']
        return [field for field in required_fields if field not in event_data]
    
    def _find_invalid_fields(self, event_data: dict) -> List[Dict[str, str]]:
        invalid = []
        
        # Check field types
        if 'timestamp' in event_data:
            try:
                datetime.fromisoformat(event_data['timestamp'])
            except (OnexError, TypeError):
                invalid.append({'field': 'timestamp', 'issue': 'Invalid timestamp format'})
        
        if 'event_type' in event_data:
            valid_types = [e.value for e in OnexEventTypeEnum]
            if event_data['event_type'] not in valid_types:
                invalid.append({'field': 'event_type', 'issue': 'Invalid event type'})
        
        return invalid
    
    def _find_schema_violations(self, event_data: dict) -> List[Dict[str, str]]:
        violations = []
        
        # Check metadata size
        metadata = event_data.get('metadata', {})
        metadata_size = len(str(metadata))
        if metadata_size > 100 * 1024:  # 100KB
            violations.append({
                'field': 'metadata',
                'issue': f'Metadata too large: {metadata_size} bytes'
            })
        
        return violations
    
    def get_validation_summary(self) -> Dict[str, any]:
        """Get summary of validation issues."""
        if not self.validation_errors:
            return {'total_errors': 0}
        
        error_types = Counter(error['error_type'] for error in self.validation_errors)
        common_violations = Counter()
        
        for violations in self.schema_violations.values():
            common_violations.update(violations)
        
        return {
            'total_errors': len(self.validation_errors),
            'error_types': dict(error_types),
            'common_violations': dict(common_violations.most_common(5)),
            'recent_errors': self.validation_errors[-5:]  # Last 5 errors
        }
```

## Observability Dashboards

### Real-Time Event Monitoring

```python
import time
from threading import Thread, Lock

class RealTimeEventMonitor:
    def __init__(self, update_interval: int = 5):
        self.update_interval = update_interval
        self.metrics = {
            'events_per_second': 0,
            'error_rate': 0,
            'avg_processing_time': 0,
            'active_correlations': 0
        }
        self.event_buffer = []
        self.lock = Lock()
        self.running = False
    
    def start_monitoring(self):
        self.running = True
        monitor_thread = Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def stop_monitoring(self):
        self.running = False
    
    def record_event(self, event: OnexEvent, processing_time_ms: float):
        with self.lock:
            self.event_buffer.append({
                'event': event,
                'processing_time': processing_time_ms,
                'timestamp': time.time()
            })
    
    def _monitor_loop(self):
        while self.running:
            self._update_metrics()
            self._print_dashboard()
            time.sleep(self.update_interval)
    
    def _update_metrics(self):
        with self.lock:
            current_time = time.time()
            recent_events = [
                e for e in self.event_buffer 
                if current_time - e['timestamp'] <= self.update_interval
            ]
            
            if recent_events:
                # Events per second
                self.metrics['events_per_second'] = len(recent_events) / self.update_interval
                
                # Error rate
                error_events = [
                    e for e in recent_events 
                    if e['event'].event_type in [OnexEventTypeEnum.NODE_FAILURE, OnexEventTypeEnum.TELEMETRY_OPERATION_ERROR]
                ]
                self.metrics['error_rate'] = len(error_events) / len(recent_events) * 100
                
                # Average processing time
                processing_times = [e['processing_time'] for e in recent_events]
                self.metrics['avg_processing_time'] = sum(processing_times) / len(processing_times)
                
                # Active correlations
                correlations = {e['event'].correlation_id for e in recent_events}
                self.metrics['active_correlations'] = len(correlations)
            
            # Clean old events
            self.event_buffer = [
                e for e in self.event_buffer 
                if current_time - e['timestamp'] <= 60  # Keep 1 minute of history
            ]
    
    def _print_dashboard(self):
        print("\n" + "="*50)
        print("ONEX Event System - Real-Time Dashboard")
        print("="*50)
        print(f"Events/sec:        {self.metrics['events_per_second']:.2f}")
        print(f"Error rate:        {self.metrics['error_rate']:.2f}%")
        print(f"Avg proc time:     {self.metrics['avg_processing_time']:.2f}ms")
        print(f"Active corr IDs:   {self.metrics['active_correlations']}")
        print("="*50)
```

### Health Check System

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Callable

class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class HealthCheck:
    name: str
    check_function: Callable[[], bool]
    warning_threshold: float = 0.8
    critical_threshold: float = 0.5

class EventSystemHealthMonitor:
    def __init__(self):
        self.health_checks: List[HealthCheck] = []
        self.health_history: Dict[str, List[bool]] = defaultdict(list)
    
    def register_health_check(self, check: HealthCheck):
        self.health_checks.append(check)
    
    def run_health_checks(self) -> Dict[str, HealthStatus]:
        results = {}
        
        for check in self.health_checks:
            try:
                result = check.check_function()
                self.health_history[check.name].append(result)
                
                # Keep only recent history
                if len(self.health_history[check.name]) > 100:
                    self.health_history[check.name] = self.health_history[check.name][-100:]
                
                # Calculate health score
                recent_results = self.health_history[check.name][-10:]  # Last 10 checks
                success_rate = sum(recent_results) / len(recent_results)
                
                # Determine status
                if success_rate >= check.warning_threshold:
                    status = HealthStatus.HEALTHY
                elif success_rate >= check.critical_threshold:
                    status = HealthStatus.WARNING
                else:
                    status = HealthStatus.CRITICAL
                
                results[check.name] = status
                
            except Exception as e:
                results[check.name] = HealthStatus.CRITICAL
                print(f"Health check '{check.name}' failed: {e}")
        
        return results
    
    def get_overall_health(self) -> HealthStatus:
        check_results = self.run_health_checks()
        
        if any(status == HealthStatus.CRITICAL for status in check_results.values()):
            return HealthStatus.CRITICAL
        elif any(status == HealthStatus.WARNING for status in check_results.values()):
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY

# Example health checks
def event_emission_health_check() -> bool:
    """Check if events are being emitted successfully."""
    # Implementation would check recent event emission success rate
    return True

def event_validation_health_check() -> bool:
    """Check if event validation is working."""
    # Implementation would check validation success rate
    return True

def correlation_tracking_health_check() -> bool:
    """Check if correlation tracking is working."""
    # Implementation would check correlation ID propagation
    return True

# Setup health monitoring
health_monitor = EventSystemHealthMonitor()
health_monitor.register_health_check(HealthCheck("event_emission", event_emission_health_check))
health_monitor.register_health_check(HealthCheck("event_validation", event_validation_health_check))
health_monitor.register_health_check(HealthCheck("correlation_tracking", correlation_tracking_health_check))
```

## Debugging Tools and Utilities

### Event Inspector

```python
class EventInspector:
    def __init__(self):
        self.inspection_rules: List[Callable[[OnexEvent], Dict[str, any]]] = []
    
    def add_inspection_rule(self, rule: Callable[[OnexEvent], Dict[str, any]]):
        self.inspection_rules.append(rule)
    
    def inspect_event(self, event: OnexEvent) -> Dict[str, any]:
        inspection_results = {
            'event_id': event.event_id,
            'basic_info': self._get_basic_info(event),
            'validation_status': self._validate_event(event),
            'metadata_analysis': self._analyze_metadata(event),
            'custom_inspections': []
        }
        
        # Run custom inspection rules
        for rule in self.inspection_rules:
            try:
                result = rule(event)
                inspection_results['custom_inspections'].append(result)
            except Exception as e:
                inspection_results['custom_inspections'].append({
                    'error': f"Inspection rule failed: {e}"
                })
        
        return inspection_results
    
    def _get_basic_info(self, event: OnexEvent) -> Dict[str, any]:
        return {
            'event_type': event.event_type,
            'node_id': event.node_id,
            'correlation_id': event.correlation_id,
            'timestamp': event.timestamp,
            'metadata_size': len(str(event.metadata)),
            'has_correlation_id': bool(event.correlation_id)
        }
    
    def _validate_event(self, event: OnexEvent) -> Dict[str, any]:
        try:
            # Use the event schema validator
            from omnibase.runtimes.onex_runtime.v1_0_0.telemetry.event_schema_validator import validate_event_schema
            validate_event_schema(event)
            return {'valid': True, 'errors': []}
        except Exception as e:
            return {'valid': False, 'errors': [str(e)]}
    
    def _analyze_metadata(self, event: OnexEvent) -> Dict[str, any]:
        metadata = event.metadata
        
        analysis = {
            'field_count': len(metadata),
            'nested_levels': self._count_nested_levels(metadata),
            'large_fields': self._find_large_fields(metadata),
            'sensitive_fields': self._find_sensitive_fields(metadata)
        }
        
        return analysis
    
    def _count_nested_levels(self, obj, level=0) -> int:
        if not isinstance(obj, dict):
            return level
        
        max_level = level
        for value in obj.values():
            if isinstance(value, dict):
                max_level = max(max_level, self._count_nested_levels(value, level + 1))
        
        return max_level
    
    def _find_large_fields(self, metadata: dict, threshold: int = 1000) -> List[str]:
        large_fields = []
        
        for key, value in metadata.items():
            if len(str(value)) > threshold:
                large_fields.append(key)
        
        return large_fields
    
    def _find_sensitive_fields(self, metadata: dict) -> List[str]:
        sensitive_patterns = ['password', 'token', 'key', 'secret', 'credential']
        sensitive_fields = []
        
        for key in metadata.keys():
            if any(pattern in key.lower() for pattern in sensitive_patterns):
                sensitive_fields.append(key)
        
        return sensitive_fields

# Example custom inspection rule
def check_duration_anomaly(event: OnexEvent) -> Dict[str, any]:
    """Check for unusually long operation durations."""
    duration = event.metadata.get('duration_ms', 0)
    
    if duration > 30000:  # 30 seconds
        return {
            'rule': 'duration_anomaly',
            'status': 'warning',
            'message': f'Operation took {duration}ms, which is unusually long'
        }
    
    return {
        'rule': 'duration_anomaly',
        'status': 'ok',
        'message': 'Duration within normal range'
    }
```

### Event Replay System

```python
import json
from typing import List, Optional

class EventReplaySystem:
    def __init__(self):
        self.recorded_events: List[OnexEvent] = []
        self.replay_handlers: List[Callable[[OnexEvent], None]] = []
    
    def record_event(self, event: OnexEvent):
        """Record event for later replay."""
        self.recorded_events.append(event)
    
    def save_recording(self, filename: str):
        """Save recorded events to file."""
        events_data = [event.model_dump() for event in self.recorded_events]
        
        with open(filename, 'w') as f:
            json.dump(events_data, f, indent=2, default=str)
    
    def load_recording(self, filename: str):
        """Load recorded events from file."""
        with open(filename, 'r') as f:
            events_data = json.load(f)
        
        self.recorded_events = [
            OnexEvent(**event_data) for event_data in events_data
        ]
    
    def replay_events(self, 
                     start_index: int = 0, 
                     end_index: Optional[int] = None,
                     speed_multiplier: float = 1.0):
        """Replay recorded events."""
        if end_index is None:
            end_index = len(self.recorded_events)
        
        events_to_replay = self.recorded_events[start_index:end_index]
        
        for i, event in enumerate(events_to_replay):
            # Calculate delay based on original timing
            if i > 0:
                prev_event = events_to_replay[i-1]
                delay = (event.timestamp - prev_event.timestamp).total_seconds()
                time.sleep(delay / speed_multiplier)
            
            # Replay event
            for handler in self.replay_handlers:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Replay handler failed for event {event.event_id}: {e}")
    
    def add_replay_handler(self, handler: Callable[[OnexEvent], None]):
        """Add handler to process replayed events."""
        self.replay_handlers.append(handler)
    
    def filter_events(self, 
                     event_type: Optional[OnexEventTypeEnum] = None,
                     node_id: Optional[str] = None,
                     correlation_id: Optional[str] = None) -> List[OnexEvent]:
        """Filter recorded events by criteria."""
        filtered = self.recorded_events
        
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        
        if node_id:
            filtered = [e for e in filtered if e.node_id == node_id]
        
        if correlation_id:
            filtered = [e for e in filtered if e.correlation_id == correlation_id]
        
        return filtered
```

## Troubleshooting Guides

### Common Issues and Solutions

#### Issue: Events Not Being Emitted

**Symptoms:**
- No events appearing in logs or monitoring systems
- Event handlers not being called
- Silent failures in event emission

**Debugging Steps:**
1. Check event emitter configuration
2. Verify event bus connectivity
3. Check for exceptions in event emission code
4. Validate event schema compliance

**Solution Example:**
```python
def debug_event_emission():
    # Test basic event creation
    try:
        test_event = OnexEvent(
            event_type=OnexEventTypeEnum.NODE_START,
            node_id="debug_node",
            correlation_id="debug-test",
            metadata={"test": True}
        )
        print("✓ Event creation successful")
    except Exception as e:
        print(f"✗ Event creation failed: {e}")
        return
    
    # Test event validation
    try:
        validate_event_schema(test_event)
        print("✓ Event validation successful")
    except Exception as e:
        print(f"✗ Event validation failed: {e}")
        return
    
    # Test event emission
    try:
        emit_event(test_event)
        print("✓ Event emission successful")
    except Exception as e:
        print(f"✗ Event emission failed: {e}")
```

#### Issue: Correlation IDs Not Propagating

**Symptoms:**
- Events with different correlation IDs that should be related
- Difficulty tracing operations across nodes
- Broken event chains

**Debugging Steps:**
1. Check correlation ID generation at entry points
2. Verify correlation ID passing between components
3. Check for correlation ID overwrites
4. Validate correlation ID format

**Solution Example:**
```python
def debug_correlation_propagation(correlation_id: str):
    # Trace correlation ID through system
    tracer = EventTracer()
    
    # Find all events with this correlation ID
    related_events = [
        event for event in tracer.traces.values()
        if event.correlation_id == correlation_id
    ]
    
    if not related_events:
        print(f"No events found for correlation ID: {correlation_id}")
        return
    
    # Analyze event chain
    print(f"Found {len(related_events)} events for correlation ID: {correlation_id}")
    for event in sorted(related_events, key=lambda e: e.timestamp):
        print(f"  {event.timestamp}: {event.event_type} from {event.node_id}")
```

## References

- **Event Schema**: [ONEX Event Schema Specification](onex_event_schema.md)
- **Performance**: [ONEX Event Performance Guide](onex_event_performance.md)
- **Integration**: [ONEX Event Integration Patterns](onex_event_integration.md)
- **Error Codes**: [ONEX Error Code Taxonomy](onex_error_codes.md)

---

**Note**: Debugging and observability patterns should be adapted based on specific deployment environments and requirements. Regular monitoring and proactive debugging are essential for maintaining system health.
