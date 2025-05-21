<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: tree_format.md -->
<!-- version: 1.0.0 -->
<!-- uuid: a47ad7eb-68ce-4fb7-8683-c2a65c23bf43 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.158135 -->
<!-- last_modified_at: 2025-05-21T16:42:46.059836 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: d842bc9dfa3602b104650036ae4da1c700066b78a24c67357c02ed2f24ef7e0a -->
<!-- entrypoint: {'type': 'python', 'target': 'tree_format.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.tree_format -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: tree_format.md -->
<!-- version: 1.0.0 -->
<!-- uuid: f2b628bc-c834-418c-90c7-b872957b1db8 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.432953 -->
<!-- last_modified_at: 2025-05-21T16:39:56.025801 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: a9ae35b5f1d483e81c73bcd726d64c7dbcd826e442824f8dc7074ea011a6b5af -->
<!-- entrypoint: {'type': 'python', 'target': 'tree_format.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.tree_format -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: tree_format.md -->
<!-- version: 1.0.0 -->
<!-- uuid: c228a7fd-31e0-46d9-bdb8-3bb0bfdf3a36 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.661415 -->
<!-- last_modified_at: 2025-05-21T16:24:00.342473 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: b5a7983ea83e127885851d49fde453c7c9d397a39186f85915d64f242ae14e5f -->
<!-- entrypoint: {'type': 'python', 'target': 'tree_format.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.tree_format -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

# tree_format

**Version:** 1.0.0

Canonical schema for ONEX .tree files. Captures the directory/file hierarchy as a nested tree.



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



## Example

```yaml
name: root
type: directory
children:
- name: src
  type: directory
  children:
  - name: nodes
    type: directory
    children:
    - name: validator.check.namegen
      type: directory
      children:
      - name: metadata.yaml
        type: file
      - name: code.py
        type: file
      - name: test.py
        type: file

```
