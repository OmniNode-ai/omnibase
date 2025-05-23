<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: observability.md
version: 1.0.0
uuid: 52506e06-3b86-4c73-bbf9-1454ee276ee7
author: OmniNode Team
created_at: 2025-05-22T17:18:16.681601
last_modified_at: 2025-05-22T21:19:13.373352
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 2e42073ccf9ab2a95fa19db02560b0e7fda33ac63e228a5780236fff84c31ea4
entrypoint: python@observability.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.observability
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
