# OmniBase Metadata & Dependency Schema

> **Status:** Draft  
> **Split From:** `omnibase_design_spec.md (v0.4.1)`  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16

---

## Overview

All OmniBase components (validators, tools, tests, data artifacts) are described using structured metadata blocks. These blocks support discovery, graph traversal, versioning, dependency resolution, and execution filtering.

---

## Canonical Metadata Block (YAML)

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
child_ids:
  - "uuid_of_child1_metadata"
  - "uuid_of_child2_metadata"
dependencies:
  - id: "tool_fix_format_headers_uuid"
    type: "tool"
    version_spec: ">=0.1.0,<0.2.0"
    required: true
  - id: "data_example_uuid"
    type: "data_artifact"
    version_spec: "1.0.0"
    required: false
tags:
  - "canary"
  - "pre-commit"
  - "schema-validation"
lifecycle: "canary"
status: "active"
idempotent: true
description: "A canonical example of a validator metadata block."
# === /OmniNode:Metadata ===
```

---

## Key Concepts

| Field            | Purpose                                                |
|------------------|--------------------------------------------------------|
| `uuid`           | Globally unique ID for this component                  |
| `parent_id`      | Link to source or inherited component                  |
| `child_ids`      | Logical extensions or dependent variants               |
| `version`        | Component version (SemVer)                             |
| `protocols_supported` | Execution contracts adhered to                    |
| `dependencies`   | Typed + versioned required components                  |
| `tags`           | Orchestration / filter / lifecycle control             |
| `idempotent`     | Safe for retry, caching, parallelism                   |
| `status`         | Active, pending_review, deprecated, etc.              |

---

## Dependency Resolution

- Uses modified Pubgrub algorithm
- Supports SemVer-compatible version ranges
- Conflicts yield descriptive errors
- Local overrides for testing supported
- Retains resolved versions in execution report

---

## Graph Semantics

- **Node:** Any component with a UUID
- **Edge:** `depends_on`, `inherits_from`, or `generated_by`
- **Use cases:** Lineage tracking, impact analysis, caching

---

## Metadata Enforcement

- All registered components must have valid metadata
- Schema-validated via Pydantic
- Enforced in CLI and CI
- Non-conforming entries rejected at registry level

---

## CLI Examples

```bash
omnibase validate metadata my_file.metadata.yaml
omnibase inspect metadata validator_abc
omnibase visualize dependencies tool_xyz
```

---

## Planned Features

- [ ] Metadata diffing and patching CLI
- [ ] Lineage tree visualizer for docs
- [ ] Trust level annotations and audit chain
- [ ] Custom metadata injection for agents

---

> Metadata is the protocol of visibility. Nothing runs unless it is declared and discoverable.
