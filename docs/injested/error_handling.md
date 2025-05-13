# OmniBase Error Handling & Result Model

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

All OmniBase functions must return structured results adhering to the `Result[U]` protocol. These include execution status, error information, diagnostic messages, and output references.

Errors must follow a canonical taxonomy and format for human and machine consumption.

---

## Result Protocol

    class Result(Protocol[U]):
        status: str
        output: Optional[U]
        errors: Optional[List[ErrorObject]]
        messages: List[str]
        produced_at: datetime
        artifact_refs: List[UUID]

---

## Canonical Result Types

- `ValidationResult`: For validators
- `TransformResult`: For tools
- `TestResult`: For test cases

All inherit from a unified `UnifiedResultModel`.

---

## UnifiedResultModel Fields

| Field         | Type              | Description                                |
|---------------|-------------------|--------------------------------------------|
| `status`      | `str`             | One of: `pass`, `fail`, `warn`, `skip`     |
| `errors`      | `List[ErrorObject]` | Structured error payloads (optional)     |
| `messages`    | `List[str]`       | Human-readable summaries                   |
| `output`      | `Any`             | Optional typed output                      |
| `produced_at` | `datetime`        | ISO timestamp                              |
| `artifact_refs` | `List[UUID]`    | References to output artifacts             |

---

## Canonical Error Object

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

## Error Taxonomy Seeds

    class OmniBaseError(Exception): ...
    class RegistryError(OmniBaseError): ...
    class ArtifactError(OmniBaseError): ...
    class ProtocolError(OmniBaseError): ...
    class ExecutionError(OmniBaseError): ...
    class SecurityError(OmniBaseError): ...

Each has at least one subclass (e.g., `RegistryLookupError`, `ArtifactNotFoundError`).

---

## Retry & Backoff Decorator

Retry logic is enabled for `idempotent: true` components:

```python
@retry(max_attempts=3, delay_ms=100, backoff_factor=2.0)
def run(...): ...
```

Automatically retries transient errors classified under `RetryableError`.

---

## Circuit Breaker Pattern

    get_circuit_breaker("validator_runner").execute(some_func)

Protects against runaway retries and repeated failures. Moves between CLOSED → OPEN → HALF_OPEN states.

---

## CLI Output Flags

- `--format json`: Stable, machine-parseable
- `--format yaml`: For debugging, agent inspection
- `--format human`: For developers, colorized and emoji-enhanced

Formatter fallback is triggered via:

- `TERM=dumb`
- `CI=true`
- `--no-color`

---

## Next Steps

- [ ] Finalize `UnifiedResultModel`
- [ ] Complete subclass mapping for validator, tool, and test results
- [ ] Enforce structured errors in CI
- [ ] Build automatic formatter selection logic
- [ ] Implement backoff metrics in orchestrator logs

---

> Functions fail. But failure should always be explicit, structured, and actionable.