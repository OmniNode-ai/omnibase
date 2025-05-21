<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: observability.md -->
<!-- version: 1.0.0 -->
<!-- uuid: fab05b04-a299-4b36-8642-a4edd490db0b -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.157457 -->
<!-- last_modified_at: 2025-05-21T16:42:46.065999 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: a5b6f434f0a700b16049fd5a914969c6780b2451196d2877c3e52d55c86c5ad2 -->
<!-- entrypoint: {'type': 'python', 'target': 'observability.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.observability -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: observability.md -->
<!-- version: 1.0.0 -->
<!-- uuid: f3d5e570-b805-4a7e-a813-86473bd94701 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.432353 -->
<!-- last_modified_at: 2025-05-21T16:39:55.982461 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: a07eee7873e45cad403771fc35b32b8e5a212fbdf56ab8eb1fddbde11a646025 -->
<!-- entrypoint: {'type': 'python', 'target': 'observability.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.observability -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: observability.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 9d4fb9f7-d4be-48cb-a976-9fa8aef8b9ef -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.660830 -->
<!-- last_modified_at: 2025-05-21T16:24:00.377907 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: d7e7c7628e8c4cfda84d0562b4227cdea485a4104a5bda65c9c49fe9ac0d3449 -->
<!-- entrypoint: {'type': 'python', 'target': 'observability.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.observability -->
<!-- meta_type: tool -->
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
