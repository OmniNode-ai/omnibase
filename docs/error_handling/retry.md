<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: retry.md
version: 1.0.0
uuid: b9b99d49-fed9-4609-bf56-0b55d2c7f392
author: OmniNode Team
created_at: '2025-05-28T12:40:26.279560'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://retry
namespace: markdown://retry
meta_type: tool

<!-- === /OmniNode:Metadata === -->
# Error Handling Retry & Circuit Breaker

See the [Error Handling Specification](../error_handling.md) for the canonical overview and result model.

---

## Retryable Error Handling

- Errors can be classified for retry using:
    - `RetryableError` (e.g., I/O failure, transient auth)
    - `NonRetryableError` (e.g., invalid input, logic error)
    - `SecurityError` (e.g., capability denied)
- Retry logic is enabled for `idempotent: true` components.

---

## Retry Decorator

```python
@retry(max_attempts=3, delay_ms=100, backoff_factor=2.0)
def run(...): ...
```
- Applies exponential backoff between attempts and logs each failure with traceback.
- Supports exponential backoff with logging and traceback capture per attempt.
- Automatically retries transient errors classified under `RetryableError`.

---

## Circuit Breaker Pattern

```python
breaker = get_circuit_breaker("validator_tool_runner")
breaker.execute(run)
```
- Protects against runaway retries and repeated failures.
- Standard CLOSED → OPEN → HALF_OPEN transition.
- Implements failure threshold, timeout before retry, limited half-open retry, and manual reset override.

---

## Observability Integration

- Every failure emits:
    - Span trace (OpenTelemetry)
    - Structured log entry
    - Tagged error code
    - Retry count / final disposition
    - Capability state (if relevant)

---

## Design Guarantees

- No `print()` debugging; all output is structured or observable
- No `sys.exit()` in component code; use exceptions
- All validators/tools/tests must raise from OmniBase error types

---

## Planned Enhancements
- [ ] Retry metadata in `Result` output block
- [ ] Failure pattern classification
- [ ] Retry frequency alerts and anomaly detection
- [ ] Integrate circuit breaker state with CLI feedback

---

Return to [Error Handling Deep Dives Index](index.md)
