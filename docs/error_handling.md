<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: error_handling.md
version: 1.0.0
uuid: c68fd834-8206-4acf-a8ba-2b4e6b0da624
author: OmniNode Team
created_at: 2025-05-27T05:39:38.793154
last_modified_at: 2025-05-27T17:26:51.880262
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: cc377e1c80cdd9cf015b2e03f3fbbb7fb82ed1dfb4f11fc9db2b52582e08dcd1
entrypoint: python@error_handling.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.error_handling
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# OmniBase Error Handling Specification

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the canonical result model, error taxonomy, retry/backoff, circuit breaker, observability, and CLI output

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

## Error Code Registry

### Core Error Codes

| Code | Category | Description |
|------|----------|-------------|
| E001 | Validation | Direct dependency instantiation |
| E002 | Metadata | Missing metadata block |
| E003 | Registry | Registry bypass forbidden |
| E004 | Standards | Naming convention violation |
| E005 | Testing | Inline fixture definition |
| E006 | Lifecycle | Missing lifecycle/status declaration |

### Validator Error Codes

| Code | Description |
|------|-------------|
| VALIDATOR_ERROR_001 | Expected header missing |
| VALIDATOR_ERROR_002 | Schema validation failure |
| VALIDATOR_ERROR_003 | Type annotation missing |

### Registry Error Codes

| Code | Description |
|------|-------------|
| REGISTRY_ERROR_001 | Component not found |
| REGISTRY_ERROR_002 | Version conflict |
| REGISTRY_ERROR_003 | Dependency resolution failure |

### Protocol Error Codes

| Code | Description |
|------|-------------|
| PROTOCOL_ERROR_001 | Interface mismatch |
| PROTOCOL_ERROR_002 | Version incompatibility |
| PROTOCOL_ERROR_003 | Missing required method |

---

## Error Handling Best Practices

### For Node Developers

1. **Always use structured errors**: Raise `OmniBaseError` subclasses with proper error codes
2. **Include context**: Provide file paths, line numbers, and relevant metadata
3. **Suggest fixes**: Include actionable suggestions in error messages
4. **Use appropriate severity**: Choose between `error`, `warning`, `info`

### For CLI Tools

1. **Respect output format**: Use the formatter registry for consistent output
2. **Provide correlation IDs**: Enable tracing across distributed operations
3. **Log retry attempts**: Include retry count and backoff timing
4. **Handle circuit breaker states**: Gracefully degrade when circuits are open

### For Testing

1. **Test error paths**: Ensure error conditions are properly handled
2. **Validate error structure**: Check that errors include required fields
3. **Test retry logic**: Verify exponential backoff and circuit breaker behavior
4. **Mock external failures**: Simulate transient and permanent failures

---

## Integration with ONEX CLI

### Error Reporting

```bash
# Get detailed error information
onex run my_node --format json | jq '.errors'

# Filter by error severity
onex run my_node --format json | jq '.errors[] | select(.severity == "error")'

# Get error suggestions
onex run my_node --format json | jq '.errors[].suggestions[]'
```

### Debugging

```bash
# Run with verbose error output
onex run my_node --verbose

# Enable debug logging
onex run my_node --debug

# Get error correlation traces
onex run my_node --trace-id abc-123-xyz
```

---

## References & Deep Dives
- See `docs/error_handling/observability.md` for advanced observability and tracing details
- See `docs/error_handling/retry.md` for retry and circuit breaker deep dive
