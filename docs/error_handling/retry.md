# Error Handling Retry & Circuit Breaker

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define retry logic and circuit breaker patterns for ONEX error handling  
> **Audience:** Developers, platform engineers, SRE teams  
> **Companion:** [Error Handling Specification](../error_handling.md), [Observability](observability.md)

---

## Overview

The ONEX error handling system implements sophisticated retry logic and circuit breaker patterns to handle transient failures gracefully while preventing cascade failures. This document details the implementation patterns and best practices for resilient error handling.

---

## Retryable Error Classification

Errors are classified into categories that determine retry behavior:

### Error Types

#### RetryableError
Transient failures that may succeed on retry:
- **I/O Failures**: Network timeouts, temporary file locks
- **Resource Contention**: Database connection limits, rate limiting
- **Transient Auth**: Token expiration, temporary permission issues
- **Service Unavailable**: Temporary service outages, load balancing issues

#### NonRetryableError
Permanent failures that will not succeed on retry:
- **Invalid Input**: Malformed data, schema validation failures
- **Logic Errors**: Programming errors, assertion failures
- **Configuration Errors**: Missing required configuration, invalid settings
- **Resource Not Found**: Missing files, non-existent endpoints

#### SecurityError
Security-related failures requiring special handling:
- **Capability Denied**: Insufficient permissions for operation
- **Authentication Failed**: Invalid credentials, expired tokens
- **Authorization Denied**: Access control violations
- **Security Policy Violation**: Operations blocked by security policies

---

## Retry Implementation

### Retry Decorator

The retry decorator provides declarative retry behavior with exponential backoff:

```python
from omnibase.core.retry import retry, RetryableError

@retry(max_attempts=3, delay_ms=100, backoff_factor=2.0)
def execute_operation(context: ExecutionContext) -> Result:
    """Execute operation with automatic retry on transient failures."""
    try:
        return perform_operation(context)
    except IOError as e:
        # Convert to retryable error for automatic retry
        raise RetryableError(f"I/O operation failed: {e}") from e
    except ValueError as e:
        # Non-retryable error - no retry attempted
        raise NonRetryableError(f"Invalid input: {e}") from e
```

### Retry Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_attempts` | int | 3 | Maximum number of retry attempts |
| `delay_ms` | int | 100 | Initial delay between retries (milliseconds) |
| `backoff_factor` | float | 2.0 | Exponential backoff multiplier |
| `max_delay_ms` | int | 30000 | Maximum delay between retries |
| `jitter` | bool | True | Add random jitter to prevent thundering herd |

### Exponential Backoff

The retry system implements exponential backoff with jitter:

```python
def calculate_delay(attempt: int, base_delay_ms: int, backoff_factor: float, 
                   max_delay_ms: int, jitter: bool = True) -> int:
    """Calculate retry delay with exponential backoff and jitter."""
    delay = min(base_delay_ms * (backoff_factor ** attempt), max_delay_ms)
    
    if jitter:
        # Add ±25% jitter to prevent thundering herd
        jitter_range = delay * 0.25
        delay += random.uniform(-jitter_range, jitter_range)
    
    return max(0, int(delay))
```

### Retry Observability

Every retry attempt is fully instrumented:

```python
def log_retry_attempt(attempt: int, max_attempts: int, error: Exception, 
                     delay_ms: int, component: str):
    """Log retry attempt with full context."""
    logger.warning(
        "Retry attempt",
        extra={
            "component": component,
            "attempt": attempt,
            "max_attempts": max_attempts,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "delay_ms": delay_ms,
            "retry_reason": "transient_failure"
        }
    )
    
    # Emit OpenTelemetry event
    span = trace.get_current_span()
    span.add_event(
        "retry_attempt",
        attributes={
            "retry.attempt": attempt,
            "retry.max_attempts": max_attempts,
            "retry.delay_ms": delay_ms,
            "retry.reason": str(error)
        }
    )
```

---

## Circuit Breaker Pattern

Circuit breakers protect against runaway retries and repeated failures by temporarily disabling operations that are likely to fail.

### Circuit Breaker States

#### CLOSED (Normal Operation)
- All requests are allowed through
- Failure count is tracked
- Transitions to OPEN when failure threshold is exceeded

#### OPEN (Failing Fast)
- All requests are immediately rejected
- No actual operation attempts are made
- Transitions to HALF_OPEN after timeout period

#### HALF_OPEN (Testing Recovery)
- Limited number of test requests are allowed
- Transitions to CLOSED if requests succeed
- Transitions back to OPEN if requests fail

### Circuit Breaker Implementation

```python
from omnibase.core.circuit_breaker import CircuitBreaker, CircuitBreakerError

# Get circuit breaker for specific component
breaker = get_circuit_breaker("validator_tool_runner")

def execute_with_circuit_breaker(operation_func, *args, **kwargs):
    """Execute operation with circuit breaker protection."""
    try:
        return breaker.execute(operation_func, *args, **kwargs)
    except CircuitBreakerError as e:
        logger.warning(
            "Circuit breaker open",
            extra={
                "component": "validator_tool_runner",
                "breaker_state": e.state,
                "failure_count": e.failure_count,
                "last_failure_time": e.last_failure_time
            }
        )
        raise
```

### Circuit Breaker Configuration

```python
@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    failure_threshold: int = 5          # Failures before opening
    timeout_seconds: int = 60           # Time before trying half-open
    half_open_max_calls: int = 3        # Max calls in half-open state
    success_threshold: int = 2          # Successes to close from half-open
    monitoring_window_seconds: int = 300 # Window for failure rate calculation
```

### Circuit Breaker Observability

Circuit breaker state changes are fully observable:

```python
def observe_circuit_breaker_state_change(breaker_name: str, old_state: str, 
                                       new_state: str, context: dict):
    """Observe circuit breaker state transitions."""
    logger.info(
        "Circuit breaker state change",
        extra={
            "breaker_name": breaker_name,
            "old_state": old_state,
            "new_state": new_state,
            "failure_count": context.get("failure_count"),
            "success_count": context.get("success_count"),
            "last_failure_time": context.get("last_failure_time")
        }
    )
    
    # Emit metric for monitoring
    circuit_breaker_state_gauge.set(
        1 if new_state == "OPEN" else 0,
        tags={"breaker_name": breaker_name, "state": new_state}
    )
```

---

## Integration Patterns

### Idempotent Operations

Retry logic is only enabled for operations marked as idempotent:

```python
@retry(max_attempts=3, delay_ms=100)
@idempotent
def stamp_file(file_path: Path, metadata: dict) -> Result:
    """Stamp file with metadata - safe to retry."""
    # Implementation ensures idempotent behavior
    pass

@non_idempotent
def generate_uuid() -> str:
    """Generate UUID - not safe to retry."""
    # No retry decorator - would change result
    pass
```

### Capability-Aware Retry

Security errors are handled specially in retry logic:

```python
def should_retry_error(error: Exception, attempt: int) -> bool:
    """Determine if error should be retried."""
    if isinstance(error, SecurityError):
        # Never retry security errors
        return False
    
    if isinstance(error, NonRetryableError):
        # Never retry logic errors
        return False
    
    if isinstance(error, RetryableError):
        # Retry transient errors up to max attempts
        return attempt < MAX_ATTEMPTS
    
    # Unknown error type - don't retry
    return False
```

---

## Design Guarantees

### Prohibited Patterns
- **No `print()` debugging**: All output must be structured or observable
- **No `sys.exit()` in components**: Use exceptions for error handling
- **No silent failures**: All errors must be explicitly handled and reported
- **No infinite retries**: Always enforce maximum attempt limits

### Required Patterns
- **Structured error types**: Use OmniBase error hierarchy
- **Observability integration**: Log all retry attempts and circuit breaker events
- **Exponential backoff**: Prevent overwhelming failing services
- **Jitter implementation**: Avoid thundering herd problems

---

## Monitoring and Alerting

### Key Metrics

#### Retry Metrics
- **Retry Rate**: Percentage of operations requiring retry
- **Retry Success Rate**: Percentage of retries that eventually succeed
- **Retry Latency**: Additional latency introduced by retries
- **Max Retries Reached**: Operations that exhausted all retry attempts

#### Circuit Breaker Metrics
- **Circuit Breaker State**: Current state of each circuit breaker
- **State Transition Rate**: Frequency of state changes
- **Failure Rate**: Rate of failures leading to circuit breaker activation
- **Recovery Time**: Time spent in OPEN state before recovery

### Alerting Thresholds

```yaml
alerts:
  high_retry_rate:
    condition: retry_rate > 10%
    severity: warning
    description: "High retry rate may indicate service degradation"
  
  circuit_breaker_open:
    condition: circuit_breaker_state == "OPEN"
    severity: critical
    description: "Circuit breaker open - service unavailable"
  
  retry_exhaustion:
    condition: max_retries_reached_rate > 5%
    severity: critical
    description: "High rate of retry exhaustion - investigate root cause"
```

---

## Implementation Examples

### Complete Retry Implementation

```python
from typing import TypeVar, Callable, Any
from functools import wraps
import time
import random
import logging

T = TypeVar('T')

def retry(max_attempts: int = 3, delay_ms: int = 100, 
         backoff_factor: float = 2.0, max_delay_ms: int = 30000):
    """Decorator for automatic retry with exponential backoff."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except RetryableError as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            "Max retry attempts reached",
                            extra={
                                "function": func.__name__,
                                "attempt": attempt,
                                "max_attempts": max_attempts,
                                "error": str(e)
                            }
                        )
                        raise
                    
                    # Calculate delay with exponential backoff and jitter
                    delay = min(delay_ms * (backoff_factor ** (attempt - 1)), max_delay_ms)
                    jitter = delay * 0.25 * random.uniform(-1, 1)
                    actual_delay = max(0, delay + jitter) / 1000  # Convert to seconds
                    
                    logger.warning(
                        "Retry attempt",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_attempts": max_attempts,
                            "delay_seconds": actual_delay,
                            "error": str(e)
                        }
                    )
                    
                    time.sleep(actual_delay)
                    
                except (NonRetryableError, SecurityError):
                    # Don't retry these error types
                    raise
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator
```

---

## References

- [Error Handling Specification](../error_handling.md)
- [Error Taxonomy](../error_taxonomy.md)
- [Observability & Tracing](observability.md)
- [Monitoring Specification](../monitoring.md)

---

**Note:** Proper retry and circuit breaker implementation is crucial for building resilient systems. All components should follow these patterns to ensure graceful handling of transient failures while preventing cascade failures. 