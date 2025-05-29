<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode Team
created_at: '2025-05-28T12:40:26.338575'
description: Stamped by ONEX
entrypoint: python://state_contract.md
hash: 6aa22b5d2729a633f22e85b6dd76db336d74bc9061c34bda5450c0cb11ff5cdc
last_modified_at: '2025-05-29T11:50:14.915867+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: state_contract.md
namespace: omnibase.state_contract
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: 8566dc0f-68bb-41c6-af52-ff5df5c43a08
version: 1.0.0

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
