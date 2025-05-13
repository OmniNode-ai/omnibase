# OmniBase Metadata Protocol & Canonical Format

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

Every OmniBase component (validator, tool, test, artifact, etc.) must be associated with a canonical metadata block. This metadata defines the component’s identity, compatibility, lineage, capabilities, and lifecycle.

---

## Metadata Block Format

The canonical format is YAML and follows this structure:

```yaml
# === OmniNode:Metadata ===
metadata_version: "0.2.1"
schema_version: "1.1.0"
uuid: "123e4567-e89b-12d3-a456-426614174000"
name: "example_validator"
namespace: "foundation.script.validate"
version: "0.1.0"
type: "validator"
entrypoint: "validators/example.py"
protocols_supported: ["O.N.E. Core v0.1"]
author: "OmniNode Team"
owner: "foundation-team"
created_at: "2025-05-12T12:00:00+00:00"
last_modified_at: "2025-05-13T10:00:00+00:00"
parent_id: "uuid_of_parent"
child_ids: ["uuid_of_child1", "uuid_of_child2"]
dependencies:
  - id: "uuid_of_tool"
    type: "tool"
    version_spec: ">=0.1.0,<0.2.0"
    required: true
tags: ["canary", "pre-commit"]
lifecycle: "canary"
status: "active"
idempotent: true
description: "Validator that checks for missing headers."
# === /OmniNode:Metadata ===
```

---

## Field Semantics

| Field              | Description                                                       |
|-------------------|-------------------------------------------------------------------|
| `uuid`            | Globally unique identifier (UUIDv4)                               |
| `name`            | Human-readable label                                              |
| `namespace`       | Hierarchical scope (e.g. `foundation.script.validate`)            |
| `version`         | Component version (SemVer required)                               |
| `entrypoint`      | Path to Python script or module                                   |
| `type`            | One of: validator, tool, test, artifact, etc.                     |
| `protocols_supported` | Which protocol versions this component conforms to            |
| `created_at`      | RFC 3339 timestamp                                                |
| `parent_id`       | UUID of parent metadata (optional)                                |
| `child_ids`       | List of UUIDs of derived components (optional)                    |
| `dependencies`    | Referenced UUIDs, with version specifiers and type                |
| `tags`            | Filterable tags for execution stages, domain, lifecycle, etc.     |
| `lifecycle`       | One of: canary, experimental, stable, deprecated                  |
| `status`          | One of: active, inactive, pending_review                          |
| `idempotent`      | If true, function produces same output for same input             |
| `description`     | Optional freeform description                                     |

---

## Metadata Placement

1. **Inline** in the component file
2. **Sidecar** `.metadata.yaml` file
3. **Registry** ingestion via CLI or Python

---

## CLI Validation

```bash
omnibase validate metadata path/to/file_or_metadata.yaml
```

Checks include:

- Required fields
- UUID format
- Version format (SemVer)
- Valid lifecycle/status values
- Dependency resolution

---

## Versioning

| Field               | Rule                              |
|--------------------|-----------------------------------|
| `metadata_version` | Version of the metadata schema     |
| `schema_version`   | Version of the referenced object   |

Version compatibility is enforced via:

```python
def check_compat(local: str, remote: str) -> Compatibility:
    # Major mismatch = incompatible
    # Minor mismatch = warning
    # Patch mismatch = compatible
```

---

## Planned Enhancements

- [ ] Metadata diff viewer
- [ ] Inferred metadata from component introspection
- [ ] Metadata explorer UI
- [ ] Pydantic-backed schema generation for static validation

---

> Metadata is not decoration. It’s the source of truth that enables structure, discoverability, and control.