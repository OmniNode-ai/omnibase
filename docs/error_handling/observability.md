<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: observability.md
version: 1.0.0
uuid: 06bdceb9-c4b4-4e22-889f-6f6286dfcacd
author: OmniNode Team
created_at: '2025-05-28T12:40:26.269860'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://observability
namespace: markdown://observability
meta_type: tool

<!-- === /OmniNode:Metadata === -->
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
