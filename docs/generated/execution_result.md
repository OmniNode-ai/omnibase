<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: 1fc3c0b7-8bfe-4dda-8919-d769524622be -->
<!-- name: execution_result.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:20:00.554288 -->
<!-- last_modified_at: 2025-05-19T16:20:00.554290 -->
<!-- description: Stamped Markdown file: execution_result.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: afb1b08e3a2f86b09302ee8dd50835e3bf5cf348f1ca0aeaaa1797a571ab950c -->
<!-- entrypoint: {'type': 'markdown', 'target': 'execution_result.md'} -->
<!-- namespace: onex.stamped.execution_result.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

# ONEX Node Execution Result Schema

**Version:** 1.0.0

Canonical schema for ONEX node execution results. Used for CI, batch, and runtime reporting.



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
| `batch_id` | `string` | Yes | Unique batch identifier |  |
| `status` | `string` | Yes | Batch execution status | `success`, `partial`, `failure` |
| `results` | `array` | Yes | List of node execution results |  |
| `trust_delta` | `number` | No | Trust score delta (optional) |  |
| `started_at` | `string` | Yes | Batch start timestamp (ISO 8601) |  |
| `completed_at` | `string` | Yes | Batch completion timestamp (ISO 8601) |  |



## Example

```yaml
batch_id: validator_patch_v3
status: partial
results:
- node_id: validator.check.format
  success: true
  execution_time_ms: 101
  status: success
- node_id: validator.check.deprecated
  success: false
  status: failure
  errors:
  - Unexpected global import
trust_delta: -0.02
started_at: 2025-05-14 08:01:12+00:00
completed_at: 2025-05-14 08:01:23+00:00

```

 
