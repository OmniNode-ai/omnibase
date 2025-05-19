<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: 8702b54b-65b1-4027-80a8-887af9a9d866 -->
<!-- name: state_contract.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:20:05.548353 -->
<!-- last_modified_at: 2025-05-19T16:20:05.548354 -->
<!-- description: Stamped Markdown file: state_contract.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: 304088e6008fc319b75abcd72a39799e48ed599ca2db84dd0c4a44ec7181c129 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'state_contract.md'} -->
<!-- namespace: onex.stamped.state_contract.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

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


 
