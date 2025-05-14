# Error Handling Observability & Tracing

See the [Error Handling Specification](../error_handling.md) for the canonical overview and result model.

---

## Observability Hooks

Every error and retry emits:
- OpenTelemetry span trace with status
- Structured log (JSON)
- Tagged error ID and executor UUID
- Retry count and final resolution status
- Correlation ID for pipeline grouping

All failures emit:
- Span trace (OpenTelemetry)
- Structured log entry
- Tagged error code
- Retry count / final disposition
- Capability state (if relevant)

---

## Design Requirements

- No `sys.exit()` allowed in tools/tests/validators
- All unexpected behavior must raise an `OmniBaseError`
- No `print()` for user-facing output—use loggers or CLI emitters
- All errors must include `error_code`, `severity`, and `suggestions` if recoverable

---

## CLI Output Modes

| Format     | Use Case            |
|------------|---------------------|
| `human`    | Developer CLI usage |
| `json`     | CI pipelines        |
| `yaml`     | Agent inspection    |

All output uses formatter registry with fallback if `isatty=False`.

---

## Future Enhancements

- [ ] Full registry of error codes and meanings
- [ ] Retry metadata in `Result` output block
- [ ] Failure pattern classification
- [ ] Retry frequency alerts and anomaly detection
- [ ] Explainability metadata per error (AI/agent readable)

---

Return to [Error Handling Deep Dives Index](index.md) 