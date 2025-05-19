<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: b8ffb059-593c-40fa-bbcd-cf91f0fce419 -->
<!-- name: retry.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:20:05.327821 -->
<!-- last_modified_at: 2025-05-19T16:20:05.327822 -->
<!-- description: Stamped Markdown file: retry.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: a85ecd224e58082a22e9e242383f1f3f97132305d0b4c3b47b8dc137171bb863 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'retry.md'} -->
<!-- namespace: onex.stamped.retry.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

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
