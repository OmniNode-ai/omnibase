<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: graph_extraction.md
version: 1.0.0
uuid: c612549e-c05d-4d8d-a817-4438d262423c
author: OmniNode Team
created_at: 2025-05-22T17:18:16.683332
last_modified_at: 2025-05-22T21:19:13.525495
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 2f1666565ecd5cb2a164a391f06c072d892b3a0b221258b89ca4b487d17b4dc3
entrypoint: python@graph_extraction.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.graph_extraction
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# OmniBase Graph Extraction and Schema Documentation

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

> **Note:** This document is a technical reference for graph extraction and schema tooling. It is closely related to the [Metadata Spec](./metadata.md), [Registry Spec](./registry.md), and [Orchestration Spec](./orchestration.md).

---

## Graph Extraction

OmniBase metadata is graph-oriented by design. Nodes (validators, tools, tests) link via:

- `dependencies`
- `parent_id`, `child_ids`
- `produced_by`, `referenced_artifacts`

The graph forms a directed acyclic graph (DAG) and is used for:

- Lineage tracing
- Impact analysis
- Execution planning
- Cycle detection
- Provenance validation

---

### CLI Examples

```bash
omnibase graph extract --uuid tool-fix_headers --format json
omnibase graph lineage --uuid validator-abc
omnibase graph visualize --tags canary --depth 2
```

---

### Query Filters

- `--uuid`  
- `--tags`  
- `--type`  
- `--lifecycle`  
- `--affected-by tool-xyz`  
- `--downstream-only`  
- `--upstream-only`  

---

## Metadata Graph Schema

All edges are typed:

```yaml
dependencies:
  - id: "validator-uuid"
    type: "validator"
    version_spec: ">=0.2.0"
    required: true
  - id: "data-uuid"
    type: "data_artifact"
```

Each UUID is resolved to a metadata block. See [Metadata Spec](./metadata.md) for canonical field definitions.

---

## Graph Diff Tool (Planned)

```bash
omnibase graph diff --base tool-v1 --compare tool-v2
```

Outputs:

- New/deleted dependencies
- Version mismatches
- Changed lineage paths

---

## Schema Documentation

All schemas are:

- Defined as `pydantic.BaseModel` classes
- Exported to OpenAPI and JSON Schema
- Versioned (`schema_version`)
- Validated at runtime

---

### CLI

```bash
omnibase schema describe validator
omnibase schema export --format json
omnibase schema list
```

See also: [Metadata Spec](./metadata.md) and [Registry Spec](./registry.md) for schema and validation details.

---

### Output

```json
{
  "title": "ValidatorMetadata",
  "type": "object",
  "properties": {
    "uuid": { "type": "string", "format": "uuid" },
    "entrypoint": { "type": "string" },
    "tags": { "type": "array", "items": { "type": "string" } }
  }
}
```

---

## API Explorer (Planned)

- Live schema explorer (Swagger UI)
- Try-it mode for tools/validators/tests
- Link to source and examples

---

> If it has a UUID, it's on the graph. If it's on the graph, we can trace it. If we can trace it, we can trust it.
