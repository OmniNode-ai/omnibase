<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: 4e6569c2-45ba-420c-97f4-2f510cc809e9 -->
<!-- name: observability.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:19:57.551689 -->
<!-- last_modified_at: 2025-05-19T16:19:57.551693 -->
<!-- description: Stamped Markdown file: observability.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: b8b1b40bb95a5524075c11aca3e4b300aca0cf8adcb04690b56ac805ccb39911 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'observability.md'} -->
<!-- namespace: onex.stamped.observability.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

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
