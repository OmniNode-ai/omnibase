<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: observability.md
version: 1.0.0
uuid: 14a496af-3b92-4259-9759-13b7914e779f
author: OmniNode Team
created_at: 2025-05-27T07:24:09.370102
last_modified_at: 2025-05-27T17:26:51.803671
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 6a6fd2ebde795ac4ac37e7bcb41f02f1e24373f21876d6041d1f26550835ae0a
entrypoint: python@observability.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.observability
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Error Handling Observability & Tracing

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Define observability and tracing for error handling in ONEX  
> **Audience:** Platform engineers, SRE teams, developers  
> **Companion:** [Error Handling Specification](../error_handling.md), [Monitoring Specification](../monitoring.md)

---

## Overview

The ONEX error handling system provides comprehensive observability through structured logging, distributed tracing, and metrics collection. Every error, retry, and recovery operation is instrumented to provide visibility into system behavior and facilitate debugging.

---

## Observability Hooks

Every error and retry operation emits comprehensive observability data:

### Distributed Tracing
- **OpenTelemetry Spans**: Each operation creates a span with error status and metadata
- **Trace Correlation**: Errors are correlated across distributed operations
- **Span Attributes**: Include error codes, retry counts, and context information
- **Parent-Child Relationships**: Maintain trace hierarchy for complex operations

### Structured Logging
- **JSON Format**: All logs use structured JSON for machine readability
- **Error Context**: Include full error context, stack traces, and metadata
- **Correlation IDs**: Link related operations across system boundaries
- **Severity Levels**: Appropriate log levels (ERROR, WARN, INFO, DEBUG)

### Metrics and Tags
- **Error Counters**: Track error frequency by type and component
- **Retry Metrics**: Monitor retry attempts and success rates
- **Latency Tracking**: Measure operation duration and retry delays
- **Component Tags**: Tag metrics by executor UUID, node type, and operation

---

## Error Emission Standards

All failures must emit the following observability data:

### Required Fields
```json
{
  "timestamp": "2025-05-27T10:30:00Z",
  "level": "ERROR",
  "error_code": "SC001",
  "error_message": "Capability denied for file access",
  "component": "stamper_node",
  "executor_uuid": "uuid-12345",
  "correlation_id": "corr-67890",
  "retry_count": 2,
  "final_disposition": "failed",
  "capability_state": "denied",
  "stack_trace": "...",
  "suggestions": ["Check file permissions", "Verify capability grants"]
}
```

### Span Attributes
```python
span.set_attributes({
    "error.code": "SC001",
    "error.severity": "high",
    "error.retryable": True,
    "component.name": "stamper_node",
    "component.version": "1.0.0",
    "operation.retry_count": 2,
    "operation.max_retries": 3,
    "capability.required": "file.write",
    "capability.granted": False
})
```

---

## Design Requirements

### Prohibited Patterns
- **No `sys.exit()`**: Never allowed in tools, tests, or validators
- **No `print()` for Output**: Use loggers or CLI emitters for user-facing output
- **No Silent Failures**: All unexpected behavior must raise an `OmniBaseError`
- **No Unstructured Logs**: All logs must be structured and machine-readable

### Required Patterns
- **Error Codes**: All errors must include standardized error codes
- **Severity Levels**: Appropriate severity classification (low, medium, high, critical)
- **Actionable Suggestions**: Include recovery suggestions for retryable errors
- **Context Preservation**: Maintain full error context through the call stack

---

## CLI Output Modes

The ONEX CLI supports multiple output formats for different use cases:

| Format | Use Case | Description |
|--------|----------|-------------|
| `human` | Developer CLI usage | Human-readable, colored output with formatting |
| `json` | CI/CD pipelines | Machine-readable JSON for automation |
| `yaml` | Agent inspection | YAML format for configuration and inspection |

### Output Format Examples

#### Human Format
```
❌ Error SC001: Capability denied for file access
   Component: stamper_node
   Retry: 2/3 attempts
   Suggestions:
   • Check file permissions
   • Verify capability grants
```

#### JSON Format
```json
{
  "status": "error",
  "error_code": "SC001",
  "component": "stamper_node",
  "retry_count": 2,
  "max_retries": 3,
  "suggestions": ["Check file permissions", "Verify capability grants"]
}
```

#### YAML Format
```yaml
status: error
error_code: SC001
component: stamper_node
retry_count: 2
max_retries: 3
suggestions:
  - Check file permissions
  - Verify capability grants
```

---

## Formatter Registry

All output uses a centralized formatter registry with automatic fallback:

```python
class OutputFormatterRegistry:
    """Registry for output formatters with fallback support."""
    
    def get_formatter(self, format_type: str, is_tty: bool) -> OutputFormatter:
        """Get formatter with automatic fallback for non-TTY environments."""
        if not is_tty and format_type == "human":
            return self.get_formatter("json", is_tty)
        
        return self._formatters.get(format_type, self._default_formatter)
```

### Automatic Fallback
- **TTY Detection**: Automatically switch to JSON format when `isatty=False`
- **CI/CD Compatibility**: Ensure machine-readable output in automated environments
- **Graceful Degradation**: Fall back to default formatter if requested format unavailable

---

## Correlation and Tracing

### Correlation IDs
- **Pipeline Grouping**: Group related operations with correlation IDs
- **Cross-Service Tracking**: Maintain correlation across service boundaries
- **Request Tracing**: Track requests from CLI to completion
- **Error Aggregation**: Group related errors for analysis

### Trace Context Propagation
```python
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

def propagate_trace_context(operation_context: dict) -> dict:
    """Propagate trace context across operation boundaries."""
    tracer = trace.get_tracer(__name__)
    propagator = TraceContextTextMapPropagator()
    
    # Inject current trace context
    propagator.inject(operation_context)
    return operation_context
```

---

## Monitoring Integration

### Metrics Collection
- **Error Rate Monitoring**: Track error rates by component and error type
- **Retry Success Rates**: Monitor retry effectiveness and patterns
- **Latency Percentiles**: Track operation latency distributions
- **Capacity Utilization**: Monitor resource usage during error conditions

### Alerting Integration
- **Threshold-Based Alerts**: Alert on error rate thresholds
- **Anomaly Detection**: Detect unusual error patterns
- **Escalation Policies**: Define escalation for critical errors
- **Recovery Notifications**: Alert on successful recovery operations

---

## Implementation Examples

### Error Emission
```python
import logging
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

def emit_error(error: OmniBaseError, context: dict):
    """Emit comprehensive error observability data."""
    
    # Structured logging
    logger.error(
        "Operation failed",
        extra={
            "error_code": error.error_code,
            "component": context.get("component"),
            "correlation_id": context.get("correlation_id"),
            "retry_count": context.get("retry_count", 0),
            "suggestions": error.suggestions
        }
    )
    
    # Span annotation
    span = trace.get_current_span()
    span.set_status(trace.Status(trace.StatusCode.ERROR, str(error)))
    span.set_attributes({
        "error.code": error.error_code,
        "error.severity": error.severity,
        "error.retryable": error.retryable
    })
```

### Retry Observability
```python
def observe_retry_attempt(attempt: int, max_attempts: int, error: Exception):
    """Observe retry attempt with full context."""
    
    logger.warning(
        "Retry attempt",
        extra={
            "attempt": attempt,
            "max_attempts": max_attempts,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
    )
    
    # Update span with retry information
    span = trace.get_current_span()
    span.add_event(
        "retry_attempt",
        attributes={
            "retry.attempt": attempt,
            "retry.max_attempts": max_attempts,
            "retry.reason": str(error)
        }
    )
```

---

## References

- [Error Handling Specification](../error_handling.md)
- [Error Taxonomy](../error_taxonomy.md)
- [Monitoring Specification](../monitoring.md)
- [CLI Interface](../cli_interface.md)

---

**Note:** Comprehensive observability is essential for maintaining and debugging the ONEX system. All components must implement these observability patterns to ensure system reliability and debuggability.
