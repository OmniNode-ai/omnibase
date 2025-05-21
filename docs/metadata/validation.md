<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: validation.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 82589c9d-f02d-4aa8-8db6-4b75da83642e -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.158991 -->
<!-- last_modified_at: 2025-05-21T16:42:46.041982 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 5580ad9c2d67c75900894be931de8f856db5235e027814686e4033e09e4138e7 -->
<!-- entrypoint: {'type': 'python', 'target': 'validation.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.validation -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: validation.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 729ecee2-225e-4ce6-b297-9eb46435346d -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.434006 -->
<!-- last_modified_at: 2025-05-21T16:39:56.129348 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 8c4f818c30aa5e1d51dbf22e5ff8af66264d61af5a15b9ed7b2ae2a4ae1830a6 -->
<!-- entrypoint: {'type': 'python', 'target': 'validation.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.validation -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: validation.md -->
<!-- version: 1.0.0 -->
<!-- uuid: d4ac29d3-fb10-4211-a18d-e01c544af096 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.662264 -->
<!-- last_modified_at: 2025-05-21T16:24:00.305189 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 85cbf4afab1d1296ab0af09822b2606dbb035412a880bc38316d6bd6c92aef16 -->
<!-- entrypoint: {'type': 'python', 'target': 'validation.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.validation -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

# Metadata Validation & CLI

See the [Metadata Specification](../metadata.md) for the canonical overview and field definitions.

---

## CLI Validation

The OmniBase CLI provides commands for validating and inspecting metadata blocks:

```bash
omnibase validate metadata <path_or_uuid>
```
Performs:
- Schema validation
- Type enforcement
- Version rule compliance
- Dependency resolution checks
- Graph cycle detection

Other CLI examples:
```bash
omnibase inspect metadata validator_abc
omnibase visualize dependencies tool_xyz
```

---

## Schema Enforcement

- All registered components must have valid metadata
- Schema-validated via Pydantic
- Enforced in CLI and CI
- Non-conforming entries are rejected at the registry level

---

## CI Integration

- Metadata validation should be part of the continuous integration pipeline
- Failures in schema, type, or dependency checks block merges
- Planned: automated metadata diffing and patching in CI

---

## Planned Validation Tooling

- [ ] Metadata diff viewer
- [ ] Inferred metadata from component introspection
- [ ] Metadata explorer UI
- [ ] Pydantic-backed schema generation for static validation

---

## Layered Validation & Normalization

- **Handler validation**: File-type-specific syntax, schema, and block extraction.
- **Engine validation**: Protocol-level field presence, canonical formatting, uniqueness, block placement, hash/timestamp consistency, idempotency.
- **All validation is protocol-driven and type-enforced.**
- **All stamping, normalization, and validation logic is centralized in the engine.**
- All metadata blocks must be wrapped in canonical comment delimiters (see metadata spec).
- Canonical normalization: all string fields normalized to empty string, lists to empty list, enums as `.value`, deterministic YAML serialization.

---

Return to [Metadata Deep Dives Index](index.md)
