<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: retry.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 382a1a0f-c9b2-47d5-806a-8705becc8401 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.157631 -->
<!-- last_modified_at: 2025-05-21T16:42:46.117506 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 516ba41cb5cc44dacd553bd94a488c9d8683a815cdba802fe302d28e3b7bd3bd -->
<!-- entrypoint: {'type': 'python', 'target': 'retry.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.retry -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: retry.md -->
<!-- version: 1.0.0 -->
<!-- uuid: cb84e7a0-5ea5-48b7-bd7f-48aaffaed69f -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.432427 -->
<!-- last_modified_at: 2025-05-21T16:39:55.983261 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 63e7f19ea4c17e1b839f4157850f4d057500ef1d2e94881043824b323f3f8e75 -->
<!-- entrypoint: {'type': 'python', 'target': 'retry.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.retry -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: retry.md -->
<!-- version: 1.0.0 -->
<!-- uuid: a9e50a63-4593-4d2d-807b-79850762bf65 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.660904 -->
<!-- last_modified_at: 2025-05-21T16:24:00.339344 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: add7495bc3a000131b394b8ec7e295667a41f3d5addae2847f58d84ef9207b7f -->
<!-- entrypoint: {'type': 'python', 'target': 'retry.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.retry -->
<!-- meta_type: tool -->
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
