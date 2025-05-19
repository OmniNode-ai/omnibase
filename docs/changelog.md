<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: a2ffd94c-8958-4f44-b8de-148471994cda -->
<!-- name: changelog.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:19:52.254663 -->
<!-- last_modified_at: 2025-05-19T16:19:52.254666 -->
<!-- description: Stamped Markdown file: changelog.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: 5dbbfee41725247c691949bf0406fe2be0a8853eb664c87bf4a6e126374b77e1 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'changelog.md'} -->
<!-- namespace: onex.stamped.changelog.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

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
