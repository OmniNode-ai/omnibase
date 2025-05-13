# OmniBase Error Handling & Retry Logic

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

OmniBase mandates structured, retry-aware error handling across all validator, tool, and test executions. Every error must be machine-readable, semantically classified, and fully traceable.

---

## Unified Result Model

All execution paths must return a `Result[U]` object containing:

- `status`: `pass`, `fail`, `warn`, `skip`
- `errors`: list of structured error objects
- `messages`: short summaries for human output
- `output`: result payload (if successful)
- `produced_at`: timestamp
- `artifact_refs`: output UUIDs (if any)

---

## Canonical Error Object

```json
{
  "error_code": "VALIDATOR_ERROR_001",
  "error_type": "ValidationError",
  "message": "Expected a header comment at top of file.",
  "location": {
    "file_path": "src/module/foo.py",
    "line_number": 3
  },
  "timestamp": "2025-05-13T12:34:00Z",
  "context": {
    "validator_id": "abc123",
    "artifact_id": "def456"
  },
  "severity": "error",
  "suggestions": [
    "Add a license or documentation header",
    "See internal style guide at https://intranet/style"
  ]
}
```

---

## Retryable Error Handling

Errors can be classified for retry using:

- `RetryableError` (e.g., I/O failure, transient auth)
- `NonRetryableError` (e.g., invalid input, logic error)
- `SecurityError` (e.g., capability denied)

---

## Retry Decorator

```python
@retry(max_attempts=3, delay_ms=100, backoff_factor=2.0)
def run(...): ...
```

Applies exponential backoff between attempts and logs each failure with traceback.

---

## Circuit Breaker

```python
breaker = get_circuit_breaker("validator_tool_runner")
breaker.execute(run)
```

Prevents repeated execution of failing code. Follows standard CLOSED → OPEN → HALF_OPEN transition.

---

## Observability Integration

Every failure emits:

- Span trace (OpenTelemetry)
- Structured log entry
- Tagged error code
- Retry count / final disposition
- Capability state (if relevant)

---

## CLI Failure Output

Formats:

- `--format human`: emoji + color + first error message
- `--format json`: full error object list
- `--format yaml`: block-formatted, ideal for agents

---

## Design Guarantees

- No `print()` debugging; all output is structured or observable
- No `sys.exit()` in component code; use exceptions
- All validators/tools/tests must raise from OmniBase error types

---

## Next Steps

- [ ] Finalize error taxonomy in `omnibase/errors/`
- [ ] Enforce result model in orchestrator
- [ ] Track error recurrence and type frequency in metrics
- [ ] Integrate circuit breaker state with CLI feedback

---

> Errors are inevitable. Unstructured errors are inexcusable.