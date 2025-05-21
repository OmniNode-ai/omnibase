<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: execution_result.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 6ac71e56-e551-4de4-aae3-5bbeffa27c21 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.157908 -->
<!-- last_modified_at: 2025-05-21T16:42:46.040564 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 59bbeaf433f6d503293dce60d05e6d531a7338c0fb4d2e71dfaa9de5c682e15c -->
<!-- entrypoint: {'type': 'python', 'target': 'execution_result.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.execution_result -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: execution_result.md -->
<!-- version: 1.0.0 -->
<!-- uuid: a21704a9-0203-4939-8b0c-ca776f7a335a -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.432724 -->
<!-- last_modified_at: 2025-05-21T16:39:56.023605 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 6c9ecb35150e95c75546099314a721c46eb7d597856f939a86722455fc850211 -->
<!-- entrypoint: {'type': 'python', 'target': 'execution_result.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.execution_result -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: execution_result.md -->
<!-- version: 1.0.0 -->
<!-- uuid: f7247e90-5b56-4b7a-8581-d674e9f68bbd -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.661199 -->
<!-- last_modified_at: 2025-05-21T16:24:00.336226 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 3ee5fe501c226e46b8a2172bd03503eacfde02b487ae01d8f9eecb9ba9c51697 -->
<!-- entrypoint: {'type': 'python', 'target': 'execution_result.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.execution_result -->
<!-- meta_type: tool -->
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
