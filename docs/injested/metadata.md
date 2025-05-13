# OmniBase Metadata & Graph Schema

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

Every OmniBase component—validators, tools, test cases, data artifacts—must include a canonical metadata block. Metadata enables registry indexing, dependency resolution, version enforcement, and lineage tracking via UUID-based graphs.

---

## Canonical Metadata Block (YAML)

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
      - id: "data_example_uuid"
        type: "data_artifact"
        version_spec: "1.0.0"
        required: false
    tags: ["canary", "pre-commit", "schema-validation"]
    lifecycle: "canary"
    status: "active"
    idempotent: true
    description: "A canonical example of a validator metadata block."
    # === /OmniNode:Metadata ===

---

## Key Fields

- `uuid`: Unique ID for graph construction
- `version`: SemVer, required for version resolution
- `protocols_supported`: List of supported protocol versions
- `parent_id` / `child_ids`: Define DAG structure for inheritance/lineage
- `dependencies`: Typed, versioned references to other components
- `idempotent`: Declares input-stability of results
- `lifecycle` / `status`: Used by orchestrators to enforce gating
- `tags`: Indexing and filtering

---

## Versioning Contracts

Version keys must follow:

| Field                | Format         | Rule                                  |
|---------------------|----------------|----------------------------------------|
| `metadata_version`  | SemVer         | Same major + minor = compatible        |
| `schema_version`    | SemVer         | Same major = compatible                |
| `version` (component) | SemVer       | Used in dependency resolution          |

Incompatibilities trigger warnings or blocks depending on severity.

---

## Dependency Schema

Each entry in `dependencies:` includes:

- `id`: UUID of dependency
- `type`: e.g., `tool`, `validator`, `data_artifact`
- `version_spec`: SemVer-compatible range (e.g., `>=0.1.0,<0.2.0`)
- `required`: Boolean

---

## UUID-Based Graph Model

The metadata block enables graph-based introspection:
- Parent/child relationships
- Transitive dependency resolution
- Cycle detection
- Impact analysis: "What depends on this component?"

---

## Graph Use Cases

- Pipeline simulation
- Orchestration planning
- Live migration planning
- Audit trails and forensic debugging
- Agent-guided improvement based on lineage graphs

---

## Metadata File Placement

- Embedded at top of `.py` or `.yaml` file (comment-prefixed)
- Or sidecar file: `example_validator.metadata.yaml`

Sidecar must use same UUID and filename prefix.

---

## Metadata Validator Tool

CLI command:

    omnibase validate metadata <path_or_uuid>

Performs:
- Schema validation
- Type enforcement
- Version rule compliance
- Dependency resolution checks
- Graph cycle detection

---

## Next Steps

- [ ] Lock metadata schema version `0.2.1`
- [ ] Implement graph extraction utilities
- [ ] Build visualizer for metadata graph
- [ ] Add impact analysis and downstream queries

---

> Metadata is the control plane of OmniBase. Without it, nothing moves.