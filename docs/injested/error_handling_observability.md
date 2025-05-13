# OmniBase Error Handling, Observability, and Retry Logic

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

OmniBase requires all execution paths to provide structured, retry-aware, observable error reporting. These mechanisms support traceability, automation, safety, and system resilience.

---

## Result Object Structure

Each execution returns a `Result[U]` containing:

- `status`: `pass`, `fail`, `warn`, `skip`
- `errors`: list of structured `ErrorObject`s
- `messages`: human-readable summaries
- `output`: typed payload (optional)
- `produced_at`: ISO-8601 timestamp
- `artifact_refs`: content digests of outputs (if any)

---

## Canonical Error Format

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

## Error Categories

| Class             | Example Causes                    |
|------------------|-----------------------------------|
| `RetryableError` | Transient I/O, timeouts, auth     |
| `NonRetryableError` | Invalid input, logic failure    |
| `SecurityError`  | Capability violation, sandbox     |

All subclasses of `OmniBaseError`.

---

## Retry & Backoff Logic

Decorator-based retry control:

```python
@retry(max_attempts=3, delay_ms=100, backoff_factor=2.0)
def run(...): ...
```

Supports exponential backoff with logging and traceback capture per attempt.

---

## Circuit Breaker Integration

```python
breaker = get_circuit_breaker("validator_tool_runner")
breaker.execute(run)
```

Implements:
- Failure threshold
- Timeout before retry (OPEN state)
- Limited half-open retry
- Manual reset override

---

## Observability Hooks

Every error and retry emits:

- OpenTelemetry span trace with status
- Structured log (JSON)
- Tagged error ID and executor UUID
- Retry count and final resolution status
- Correlation ID for pipeline grouping

---

## CLI Output Modes

| Format     | Use Case            |
|------------|---------------------|
| `human`    | Developer CLI usage |
| `json`     | CI pipelines         |
| `yaml`     | Agent inspection     |

All output uses formatter registry with fallback if `isatty=False`.

---

## Design Requirements

- No `sys.exit()` allowed in tools/tests/validators
- All unexpected behavior must raise an `OmniBaseError`
- No `print()` for user-facing output—use loggers or CLI emitters
- All errors must include `error_code`, `severity`, and `suggestions` if recoverable

---

## Future Enhancements

- [ ] Full registry of error codes and meanings
- [ ] Retry metadata in `Result` output block
- [ ] Failure pattern classification
- [ ] Retry frequency alerts and anomaly detection
- [ ] Explainability metadata per error (AI/agent readable)

---

> If it failed, show me what, why, and how to fix it—don’t make me guess.