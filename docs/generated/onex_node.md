<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: 53f4ffd4-6cab-40d7-9baf-9aba806f8f1f -->
<!-- name: onex_node.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:19:51.942081 -->
<!-- last_modified_at: 2025-05-19T16:19:51.942084 -->
<!-- description: Stamped Markdown file: onex_node.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: 4800c219cd1ae98e254879eb38ade0acbc531964888db166b6bbf88e43c3a5f5 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'onex_node.md'} -->
<!-- namespace: onex.stamped.onex_node.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

# ONEX Node Metadata Schema

**Version:** 1.0.0

Canonical schema for ONEX node metadata (.onex). All ONEX nodes must conform to this schema.
This schema is versioned and will support prerelease/build metadata in future versions. For migration and changelog, see /docs/changelog.md.
For error taxonomy and validation failure codes, see /docs/error_taxonomy.md.



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
| `schema_version` | `string` | Yes | ONEX metadata schema version (semver, e.g., '0.1.0'). Future versions may support prerelease (-beta.1) and build (+build123) metadata. |  |
| `name` | `string` | Yes | Unique node name. |  |
| `version` | `string` | Yes | Node version (semver, e.g., '0.1.0'). Future versions may support prerelease (-rc.1) and build (+build123) tags. |  |
| `uuid` | `string` | Yes | Node UUID (RFC 4122). Must follow standard hyphenation pattern. |  |
| `author` | `string` | Yes | Author or maintainer. |  |
| `created_at` | `string` | Yes | Creation timestamp (ISO 8601). |  |
| `last_modified_at` | `string` | Yes | Last modification timestamp (ISO 8601). |  |
| `description` | `string` | Yes | Human-readable description of the node. |  |
| `state_contract` | `string` | Yes | Canonical URI to the state contract schema (e.g., state_contract://summary_block_schema.json). Must match URI format. |  |
| `lifecycle` | `string` | Yes | Node lifecycle state. | `draft`, `active`, `deprecated`, `archived` |
| `hash` | `string` | Yes | SHA256 hash (64-character hex) of the canonicalized metadata block, excluding this field itself. |  |
| `entrypoint` | `object` | Yes | Entrypoint specification for node execution. |  |
| `runtime_language_hint` | `string` | No | Optional language or interpreter hint (e.g., 'python>=3.10', 'bash', 'node16'). |  |
| `namespace` | `string` | Yes | Node namespace (e.g., 'omninode.tools.<name>'). |  |
| `meta_type` | `string` | Yes | Node type. Must be one of: tool, validator, agent, model, schema, plugin. | `tool`, `validator`, `agent`, `model`, `schema`, `plugin` |
| `tags` | `array` | No | List of tags or categories. (Optional) |  |
| `trust_score_stub` | `object` | No | Stub for trust scoring. (Optional, extensible via x-extensions) |  |
| `x_extensions` | `object` | No | Custom extension fields (optional). |  |
| `protocols_supported` | `array` | No | List of supported protocols (optional). Each must be a canonical URI. |  |
| `base_class` | `array` | No | List of base classes (optional). Each must be a canonical URI. |  |
| `dependencies` | `array` | No | List of dependencies (optional). Each must be a canonical URI. |  |
| `environment` | `array` | No | List of environment requirements (optional). |  |
| `license` | `string` | No | License identifier (optional). |  |
| `signature_block` | `object` | No | Cryptographic signature metadata for integrity and trust. (Optional) |  |



## Example

```yaml
metadata_version: '0.1'
protocol_version: 1.0.0
schema_version: 0.1.0
name: extract_summary_block
version: 1.0.0
uuid: 65dfc205-96f3-4f86-8497-cf6d8a1c4b95
author: foundation
owner: foundation
copyright: 2025 Foundation, All Rights Reserved
created_at: '2025-05-17T10:05:00Z'
last_modified_at: '2025-05-17T10:15:00Z'
description: Parses a metadata block and extracts summary and status fields for display.
state_contract: state_contract://summary_block_schema.json
lifecycle: active
hash: abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
entrypoint: src/omnibase/tools/cli_extract_summary_block.py
namespace: omninode.tools.extract_summary_block
meta_type: tool
runtime_language_hint: python
tags:
- metadata
- docs
- summary
trust_score_stub:
  runs: 12
  failures: 0
  trust_score: 1.0
x_extensions: {}
protocols_supported:
- validator://core.schema_validator@1.0.0
base_class:
- validator://core.schema_validator@1.0.0
dependencies:
- tool://tools.tree_generator@>=0.2.0
environment: []
license: Apache-2.0

```

 
