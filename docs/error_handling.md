<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:40:26.250769'
description: Stamped by ONEX
entrypoint: python://error_handling.md
hash: 91e058d4e0b7d440c1dd9d2fa5181bf0c774688111dc846571895147b12d502f
last_modified_at: '2025-05-29T11:50:14.861699+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: error_handling.md
namespace: omnibase.error_handling
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: f57b4c16-fd07-436f-be70-63d824349c0d
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# OmniBase Error Handling Specification

> **Status:** Draft  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

All OmniBase execution paths—validators, tools, tests—must return structured results and errors. Errors must be machine-readable, semantically classified, and fully traceable. This document defines the canonical result model, error taxonomy, retry/backoff, circuit breaker, observability, CLI output, and design guarantees.

---

## Result Model & Error Object

### Result Protocol

```python
class Result(Protocol[U]):
    status: str
    output: Optional[U]
    errors: Optional[List[ErrorObject]]
    messages: List[str]
    produced_at: datetime
    artifact_refs: List[UUID]
```

### Canonical Result Types
- `ValidationResult`: For validators
- `TransformResult`: For tools
- `TestResult`: For test cases
- All inherit from a unified `UnifiedResultModel`.

### UnifiedResultModel Fields

| Field         | Type                | Description                                |
|---------------|---------------------|--------------------------------------------|
| `status`      | `str`               | One of: `pass`, `fail`, `warn`, `skip`     |
| `errors`      | `List[ErrorObject]` | Structured error payloads (optional)       |
| `messages`    | `List[str]`         | Human-readable summaries                   |
| `output`      | `Any`               | Optional typed output                      |
| `produced_at` | `datetime`          | ISO timestamp                              |
| `artifact_refs` | `List[UUID]`      | References to output artifacts             |

### Canonical Error Object

```json
{
  "error_code": "VALIDATOR_ERROR_001",
  "error_type": "ValidationError",
  "message": "Human-readable error message",
  "location": {
    "file_path": "path/to/file.py",
    "line_number": 42
  },
  "timestamp": "2025-05-15T10:00:00Z",
  "context": {
    "validator_id": "uuid_of_validator",
    "artifact_id": "uuid_of_artifact"
  },
  "severity": "error",
  "suggestions": [
    "Consider fixing X by doing Y",
    "Documentation at: URL"
  ]
}
```

---

## Error Taxonomy

- All errors are subclasses of `OmniBaseError`.
- Canonical error classes:
    - `RegistryError`, `ArtifactError`, `ProtocolError`, `ExecutionError`, `SecurityError`, etc.
    - Each has at least one subclass (e.g., `RegistryLookupError`, `ArtifactNotFoundError`).
- Error categories:
    - `RetryableError`: Transient I/O, timeouts, auth
    - `NonRetryableError`: Invalid input, logic failure
    - `SecurityError`: Capability violation, sandbox

---

## Retry & Backoff

- Retry logic is enabled for `idempotent: true` components.
- Decorator-based retry control:

```python
@retry(max_attempts=3, delay_ms=100, backoff_factor=2.0)
def run(...): ...
```
- Supports exponential backoff with logging and traceback capture per attempt.
- Automatically retries transient errors classified under `RetryableError`.

---

## Circuit Breaker

- Protects against runaway retries and repeated failures.
- Standard CLOSED → OPEN → HALF_OPEN transition.

```python
breaker = get_circuit_breaker("validator_tool_runner")
breaker.execute(run)
```
- Implements failure threshold, timeout before retry, limited half-open retry, and manual reset override.

---

## Observability

- Every error and retry emits:
    - OpenTelemetry span trace with status
    - Structured log (JSON)
    - Tagged error ID and executor UUID
    - Retry count and final resolution status
    - Correlation ID for pipeline grouping
- All failures emit:
    - Span trace (OpenTelemetry)
    - Structured log entry
    - Tagged error code
    - Retry count / final disposition
    - Capability state (if relevant)

---

## CLI Output

- Output formats:
    - `--format human`: emoji + color + first error message
    - `--format json`: full error object list
    - `--format yaml`: block-formatted, ideal for agents
- Formatter fallback is triggered via:
    - `TERM=dumb`, `CI=true`, `--no-color`, or `isatty=False`

---

## Design Guarantees

- No `sys.exit()` allowed in tools/tests/validators
- All unexpected behavior must raise an `OmniBaseError`
- No `print()` for user-facing output—use loggers or CLI emitters
- All errors must include `error_code`, `severity`, and `suggestions` if recoverable
- All validators/tools/tests must raise from OmniBase error types

---

## Planned Enhancements
- [ ] Finalize `UnifiedResultModel`
- [ ] Complete subclass mapping for validator, tool, and test results
- [ ] Enforce structured errors in CI
- [ ] Build automatic formatter selection logic
- [ ] Implement backoff metrics in orchestrator logs
- [ ] Full registry of error codes and meanings
- [ ] Retry metadata in `Result` output block
- [ ] Failure pattern classification
- [ ] Retry frequency alerts and anomaly detection
- [ ] Explainability metadata per error (AI/agent readable)
- [ ] Finalize error taxonomy in `omnibase/errors/`
- [ ] Enforce result model in orchestrator
- [ ] Track error recurrence and type frequency in metrics
- [ ] Integrate circuit breaker state with CLI feedback

---

## References & Deep Dives
- See `docs/error_handling/observability.md` for advanced observability and tracing details
- See `docs/error_handling/retry.md` for retry and circuit breaker deep dive
