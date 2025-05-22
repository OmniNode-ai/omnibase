<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: state_contract.md
version: 1.0.0
uuid: 2afd0c69-6096-43ee-b645-5da8ae5ecf8a
author: OmniNode Team
created_at: 2025-05-22T17:18:16.683034
last_modified_at: 2025-05-22T21:19:13.464560
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 6ef072371689abfeb71a6d75396a44f9056b9c799196fc975c5e13310765a965
entrypoint: python@state_contract.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.state_contract
meta_type: tool
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
