<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: changelog.md
version: 1.0.0
uuid: 4852f6d0-e928-4d79-8ae3-c83dc93658f3
author: OmniNode Team
created_at: 2025-05-22T17:18:16.675293
last_modified_at: 2025-05-22T21:19:13.562719
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 990fe8aad4c8cfdb2b8d4d53527f8ea23642ff3734a09464c7fd8cfc17cdea75
entrypoint: python@changelog.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.changelog
meta_type: tool
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
