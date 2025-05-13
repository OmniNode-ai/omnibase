# OmniBase Registry System

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

The OmniBase Registry system is responsible for tracking all registered components:
- Validators
- Tools (transformers)
- Test Cases

Registries enable discoverability, dynamic execution, dependency resolution, and metadata-driven orchestration.

---

## Registry Types

### 1. `ValidatorRegistry`

Tracks all validator components. Discoverable by:
- Artifact type
- Tags (e.g. `schema`, `canary`)
- Version
- Lifecycle

### 2. `ToolRegistry`

Tracks transformation functions. Supports:
- Toolchain construction
- Versioned composition
- Metadata-based filtering

### 3. `TestCaseRegistry`

Tracks declarative test cases. Filters by:
- Test type (unit, integration, e2e)
- Tags and targets
- Lifecycle phase

---

## Query Patterns

All registries support query-by:
- Input/output types (via `Artifact[T]` and `Result[U]`)
- Tags (`canary`, `pre-commit`, etc.)
- Version (`SemVer` range supported)
- Lifecycle (`canary`, `stable`, `deprecated`)
- Source (`hardcoded`, `agent-generated`, `external`)
- UUID or name

---

## Metadata Block (Canonical Schema)

Each registered component must have a metadata block (in-file or sidecar).

    # === OmniNode:Metadata ===
    metadata_version: "0.2.1"
    schema_version: "1.1.0"
    uuid: "123e4567-e89b-12d3-a456-426614174000"
    name: "example_validator"
    namespace: "foundation.script.validate"
    version: "0.1.0"
    type: "validator"
    entrypoint: "python_validate_example.py"
    protocols_supported: ["O.N.E. Core v0.1"]
    author: "OmniNode Team"
    owner: "foundation-team"
    created_at: "2025-05-12T12:00:00+00:00"
    last_modified_at: "2025-05-13T10:00:00+00:00"
    parent_id: "uuid_of_root_validator_metadata_block"
    child_ids: ["uuid_of_child1_metadata", "uuid_of_child2_metadata"]
    dependencies:
      - id: "tool_fix_format_headers_uuid"
        type: "tool"
        version_spec: ">=0.1.0,<0.2.0"
        required: true
    tags: ["canary", "pre-commit"]
    lifecycle: "canary"
    status: "active"
    idempotent: true
    description: "A canonical example of a validator metadata block."
    # === /OmniNode:Metadata ===

---

## Version Resolution

Registry uses a modified Pubgrub algorithm:
- Enforces SemVer compatibility
- Prefers newer compatible versions
- Flags major mismatches
- Allows local override

---

## UUID Graph Model

- Each component has a UUID
- `parent_id` and `child_ids` form a DAG
- Enables:
  - Lineage queries
  - Inheritance resolution
  - Impact analysis

---

## Registry Backend

Authoritative store: **PostgreSQL**

    - JSON/JSONB columns for metadata
    - Fast indexed lookups by UUID, tag, type, etc.
    - Transactional integrity

Cache layer: **Write-through file-based**

    - Used for CLI and local workflows
    - Periodic sync
    - Optional read-only offline mode

---

## CLI Examples

    omnibase list validators --tag canary
    omnibase run tool fix_format_headers --input example.py
    omnibase inspect metadata 123e4567-e89b-12d3-a456-426614174000
    omnibase validate metadata my_validator.yaml
    omnibase visualize dependencies fix_format_headers
    omnibase compose pipeline --from fix_format_headers --to check_header_spacing

---

## Registry Policy

- Components must have a valid, parseable metadata block
- All entries must include:
  - UUID
  - Version (SemVer)
  - Tags
  - Lifecycle
  - Idempotency flag
- All registry reads/writes validated against schema
- CI blocks unversioned or malformed entries

---

## Next Steps

- [ ] Implement versioned PostgreSQL registry schema
- [ ] Implement CLI-backed file cache
- [ ] Add schema validators for metadata structure
- [ ] Create visualization tools for UUID graph traversal

---

> Registry state is the source of truth for all validation, execution, and orchestration decisions.