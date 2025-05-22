<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: tree_format.md
version: 1.0.0
uuid: 10092bdc-5618-42b4-a01d-01bd8db2e3c5
author: OmniNode Team
created_at: 2025-05-22T17:18:16.683200
last_modified_at: 2025-05-22T21:19:13.434467
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 603e78d15abdd6dc5fdf32a373dc984255cfaaa2d3c7b5a1b4841ccbbb86d94b
entrypoint: python@tree_format.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.tree_format
meta_type: tool
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
