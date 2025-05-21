<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: state_contract.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 93633834-9c7b-42e4-9b52-b3f266b78250 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.158067 -->
<!-- last_modified_at: 2025-05-21T16:42:46.085626 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 5c0734e0a2b83b00569865b8fbd624f9bbb6f755da876c2ae9d352e450d1936c -->
<!-- entrypoint: {'type': 'python', 'target': 'state_contract.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.state_contract -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: state_contract.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 950910b2-afd1-4991-889e-21d0f780401a -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.432884 -->
<!-- last_modified_at: 2025-05-21T16:39:56.025199 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 102fb2f2eda42239a3447d66c194fcdc381ad9abafad16202cdc65be59e7e4dd -->
<!-- entrypoint: {'type': 'python', 'target': 'state_contract.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.state_contract -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: state_contract.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 1bc6d7df-cafa-40fb-9f64-fc4ebed7058c -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.661340 -->
<!-- last_modified_at: 2025-05-21T16:24:00.308733 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 9feee36549563a5f11ca9873573f8471fceacf1b48e59f5fb052602faa003688 -->
<!-- entrypoint: {'type': 'python', 'target': 'state_contract.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.state_contract -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

# ONEX State Contract Schema (Stub)

**Version:** 1.0.0

Minimal stub for ONEX node state contract. See docs/nodes/node_contracts.md for full specification.


## Changelog
# Schema Changelog

## 1.0.0 (2024-06-09)

- Initial release of all canonical schemas:
  - `onex_node.yaml`
  - `tree_format.yaml`, `tree_format.json`
  - `execution_result.yaml`, `execution_result.json`
  - `state_contract.yaml`, `state_contract.json`
- All schemas include a `SCHEMA_VERSION` field at the top-level.
- Dual-format (YAML/JSON) support for all schemas.
- Registry-driven, protocol-injected tests and usage examples for all formats.

---

## Deprecation Policy

- All schema deprecations must be documented in this changelog.
- Deprecated fields or versions must be marked in the schema and referenced here.
- Breaking changes require a major version bump and migration notes.
- Backward-compatible changes require a minor version bump.
- Patch version increments are for bugfixes or clarifications only.



## Fields
| Name | Type | Required | Description | Enum |
|------|------|----------|-------------|------|
| `state` | `object` | Yes | Stub state object. Extend in M1+ with canonical fields. |  |
