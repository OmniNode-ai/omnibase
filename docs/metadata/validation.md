<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: b61656f2-b4f7-4a97-aca6-1f100b58b279 -->
<!-- name: validation.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:19:55.435439 -->
<!-- last_modified_at: 2025-05-19T16:19:55.435441 -->
<!-- description: Stamped Markdown file: validation.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: 0f4c42f7a5a18b9881759d16249e545803ac2934ff8bf08434b4b27c158a8b9f -->
<!-- entrypoint: {'type': 'markdown', 'target': 'validation.md'} -->
<!-- namespace: onex.stamped.validation.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

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
