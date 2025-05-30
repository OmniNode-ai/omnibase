<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: execution_result.md
version: 1.0.0
uuid: 5c74e40c-51ee-47d6-a4d1-e68243976840
author: OmniNode Team
created_at: '2025-05-28T12:40:26.318721'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://execution_result
namespace: markdown://execution_result
meta_type: tool

<!-- === /OmniNode:Metadata === -->
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
