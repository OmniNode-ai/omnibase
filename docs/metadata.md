# OmniBase Metadata Specification

> **Status:** Draft  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

Every OmniBase component—validators, tools, test cases, data artifacts—must include a canonical metadata block. Metadata enables registry indexing, dependency resolution, version enforcement, and lineage tracking via UUID-based graphs. This document defines the canonical format, field semantics, dependency schema, lineage/federation, and validation mechanisms.

---

## Canonical Metadata Block & Field Semantics

### Canonical Metadata Block (YAML)

```yaml
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
```

### Field Semantics

| Field                | Description                                                       |
|---------------------|-------------------------------------------------------------------|
| `uuid`              | Globally unique identifier (UUIDv4)                               |
| `name`              | Human-readable label                                              |
| `namespace`         | Hierarchical scope (e.g. `foundation.script.validate`)            |
| `version`           | Component version (SemVer required)                               |
| `entrypoint`        | Path to Python script or module                                   |
| `type`              | One of: validator, tool, test, artifact, etc.                     |
| `protocols_supported` | Which protocol versions this component conforms to              |
| `created_at`        | RFC 3339 timestamp                                                |
| `last_modified_at`  | RFC 3339 timestamp                                                |
| `parent_id`         | UUID of parent metadata (optional)                                |
| `child_ids`         | List of UUIDs of derived components (optional)                    |
| `dependencies`      | Referenced UUIDs, with version specifiers and type                |
| `tags`              | Filterable tags for execution stages, domain, lifecycle, etc.     |
| `lifecycle`         | One of: canary, experimental, stable, deprecated                  |
| `status`            | One of: active, inactive, pending_review                          |
| `idempotent`        | If true, function produces same output for same input             |
| `description`       | Optional freeform description                                     |

---

## Dependency Schema & Resolution

Each entry in `dependencies:` includes:
- `id`: UUID of dependency
- `type`: e.g., `tool`, `validator`, `data_artifact`
- `version_spec`: SemVer-compatible range (e.g., `>=0.1.0,<0.2.0`)
- `required`: Boolean

### Dependency Resolution
- Uses a modified Pubgrub algorithm
- Supports SemVer-compatible version ranges
- Conflicts yield descriptive errors
- Local overrides for testing supported
- Retains resolved versions in execution report

### Graph Semantics
- **Node:** Any component with a UUID
- **Edge:** `depends_on`, `inherits_from`, or `generated_by`
- **Use cases:** Lineage tracking, impact analysis, caching

---

## Lineage & Federation

### Registry Federation
OmniBase supports a federated registry model for distributed, multi-org collaboration.

#### Federation Modes
| Mode         | Description                                      |
|--------------|--------------------------------------------------|
| Centralized  | One authoritative registry, local caches         |
| Hierarchical | Parent-child registries, policy-controlled sync  |
| Mesh         | Peer-to-peer sync across trusted registries      |

Default: centralized → optional mesh with ACLs

#### Sync Patterns
- Pull-only: local registry pulls from upstream (read-only)
- Push: changes propagate to remote registries (if permitted)
- Partial sync: filter by tags, lifecycle, namespace
- Full sync: entire DAG of referenced entries

#### Security Controls
- Signature-based verification of remote metadata
- Trust roots for federation
- Version pinning of critical components
- Audit logs of federation events
- Optional sandboxing of newly pulled components

### Metadata Lineage Graph
Each metadata block supports:
- `parent_id`: single upstream (inheritance)
- `child_ids`: list of known descendants
- `dependencies`: typed, versioned edges
- `produced_by`: execution UUID or agent ID

Lineage graph forms a directed acyclic graph (DAG).

#### Use Cases
- Trace validator ancestry for debugging
- Replay execution history of toolchains
- Visualize test case evolution
- Filter components derived from agent-generated roots
- Detect component drift via lineage comparison

#### Lineage Visualizer (Planned)
CLI and web-based DAG viewer:
```bash
omnibase visualize lineage <uuid>
omnibase lineage diff --base <uuid1> --compare <uuid2>
```
Supports:
- Node coloring by lifecycle
- Edge labeling by dependency type
- Breadcrumb traces

---

## CLI/Validation

CLI command:
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

Validation is enforced in CLI and CI. Non-conforming entries are rejected at the registry level.

---

## Versioning Contracts

| Field                | Format         | Rule                                  |
|---------------------|----------------|----------------------------------------|
| `metadata_version`  | SemVer         | Same major + minor = compatible        |
| `schema_version`    | SemVer         | Same major = compatible                |
| `version` (component) | SemVer       | Used in dependency resolution          |

Incompatibilities trigger warnings or blocks depending on severity.

Version compatibility is enforced via:
```python
def check_compat(local: str, remote: str) -> Compatibility:
    # Major mismatch = incompatible
    # Minor mismatch = warning
    # Patch mismatch = compatible
```

---

## Planned Enhancements
- [ ] Lock metadata schema version `0.2.1`
- [ ] Implement graph extraction utilities
- [ ] Build visualizer for metadata graph
- [ ] Add impact analysis and downstream queries
- [ ] Metadata diff viewer
- [ ] Inferred metadata from component introspection
- [ ] Metadata explorer UI
- [ ] Pydantic-backed schema generation for static validation
- [ ] Lineage tree visualizer for docs
- [ ] Trust level annotations and audit chain
- [ ] Custom metadata injection for agents
- [ ] Federated sync agent and ACL config
- [ ] Lineage graph extract + diff tool
- [ ] Visualization engine (CLI first)
- [ ] Trust and signature enforcement CLI
- [ ] Provenance-aware execution logs

---

## References & Deep Dives
- See `docs/metadata/dependency.md` for advanced dependency resolution details
- See `docs/metadata/lineage.md` for federation and lineage deep dive
- See `docs/metadata/validation.md` for validation and CLI usage 