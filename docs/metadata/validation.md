<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: validation.md
version: 1.0.0
uuid: 94fded8a-61ae-4372-94c4-3da75817f0d7
author: OmniNode Team
created_at: 2025-05-28T12:40:26.516756
last_modified_at: 2025-05-28T17:20:04.168043
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 6fa4219e3cdd880378c8b25690e44afc72c4da07742e104320ed6f3689391484
entrypoint: python@validation.md
runtime_language_hint: python>=3.11
namespace: omnibase.stamped.validation
meta_type: tool
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
