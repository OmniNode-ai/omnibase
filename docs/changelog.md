<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: changelog.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 20d57e7d-6601-426b-9ab5-a4310ecba238 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.155910 -->
<!-- last_modified_at: 2025-05-21T16:42:46.102900 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: cf45a634276005dfcafb6bb3e5e5335fac9f57310d5bfb610e8f8e2eb748a3e0 -->
<!-- entrypoint: {'type': 'python', 'target': 'changelog.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.changelog -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: changelog.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 708717af-e3e7-4c0b-bb64-98afc57a297a -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.430990 -->
<!-- last_modified_at: 2025-05-21T16:39:55.746912 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 905a886799106222f02eef7a0a584dc08e6ce6fc4ca98304c036a3a0528efeaa -->
<!-- entrypoint: {'type': 'python', 'target': 'changelog.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.changelog -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: changelog.md -->
<!-- version: 1.0.0 -->
<!-- uuid: e84cd592-62e4-43ae-8ef9-40a68652ef53 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.659282 -->
<!-- last_modified_at: 2025-05-21T16:24:00.344238 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 30e3c55c88ef405bcd1367755cf362870a688b885394861f31cf38b0753b93a6 -->
<!-- entrypoint: {'type': 'python', 'target': 'changelog.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.changelog -->
<!-- meta_type: tool -->
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
