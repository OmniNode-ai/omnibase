# OmniBase Registry Specification

> **Status:** Draft  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

The OmniBase Registry system is responsible for tracking all registered components:
- Validators
- Tools (transformers)
- Test Cases
- Artifacts
- Pipelines

Registries enable discoverability, dynamic execution, dependency resolution, and metadata-driven orchestration. All validators, tools, tests, and artifacts must be registered and queryable via a uniform protocol.

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

### 4. `Artifact` and `Pipeline`
Artifacts are typed input/output units in CAS. Pipelines are ordered chains of tools/validators.

---

## Discovery Protocol

```python
class Registry(Protocol):
    def find(self, query: RegistryQuery) -> list[RegistryEntry]: ...
    def resolve(self, uuid: str, version: Optional[str] = None) -> RegistryEntry: ...
    def search(self, filters: dict[str, Any]) -> list[RegistryEntry]: ...
    def register(self, entry: RegistryEntry) -> None: ...
```

---

## Query Patterns

All registries support query-by:
- Input/output types (via `Artifact[T]` and `Result[U]`)
- Tags (`canary`, `pre-commit`, etc.)
- Version (`SemVer` range supported)
- Lifecycle (`canary`, `stable`, `deprecated`, `experimental`)
- Source (`hardcoded`, `agent-generated`, `external`)
- UUID or name
- Capabilities
- Status (`active`, `deprecated`, `draft`)

### Query Fields

| Field          | Description                        |
|----------------|------------------------------------|
| `uuid`         | Global identifier                  |
| `name`         | Human-readable label               |
| `tags`         | Filter execution stages, CLI runs  |
| `type`         | Validator, tool, test, etc.        |
| `version_spec` | SemVer range (`>=0.1.0,<0.2.0`)     |
| `capabilities` | Required permissions               |
| `status`       | `active`, `deprecated`, `draft`    |
| `lifecycle`    | `canary`, `stable`, `experimental` |

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

- Registry uses a modified Pubgrub algorithm:
    - Enforces SemVer compatibility
    - Prefers newer compatible versions
    - Flags major mismatches
    - Allows local override
- Registry maintains a `resolved_versions.json` file for reproducibility

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
    omnibase list --type tool --tags canary
    omnibase search --filter 'name=fix_header,type=tool'
    omnibase resolve validator:abc123
    omnibase inspect uuid-of-component

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

## Federation Strategy (Planned)

- Future registries can sync with one another
- Priority order controlled by trust/config
- Conflicts resolved using `source_precedence`
- Components may be promoted/demoted based on validation success

---

## Planned Enhancements
- [ ] Implement versioned PostgreSQL registry schema
- [ ] Implement CLI-backed file cache
- [ ] Add schema validators for metadata structure
- [ ] Create visualization tools for UUID graph traversal
- [ ] GraphQL adapter for registry access
- [ ] Federation metadata schema (`registry_remote.yaml`)
- [ ] Trust scoring for source registries
- [ ] Differential sync for CI pipelines

---

> Registry state is the source of truth for all validation, execution, and orchestration decisions. 