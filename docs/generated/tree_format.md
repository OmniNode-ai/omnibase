<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: 4bad4f25-642b-4195-8ce3-bfb777d5ecba -->
<!-- name: tree_format.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:19:52.512918 -->
<!-- last_modified_at: 2025-05-19T16:19:52.512923 -->
<!-- description: Stamped Markdown file: tree_format.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: b24307089ba771f0901442076a11fad426dfda0eceb8cace970e70e35fef3a0d -->
<!-- entrypoint: {'type': 'markdown', 'target': 'tree_format.md'} -->
<!-- namespace: onex.stamped.tree_format.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

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

 
