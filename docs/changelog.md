<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:40:25.945853'
description: Stamped by ONEX
entrypoint: python://changelog.md
hash: 09584a7b88c713a9335c09887ae2655ee87396a102697b31e326f10e3e8e265b
last_modified_at: '2025-05-29T11:50:14.647943+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: changelog.md
namespace: omnibase.changelog
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: cfd1e538-0c14-44e6-b9b8-4bd34c5db769
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


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
