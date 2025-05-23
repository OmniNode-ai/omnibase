<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: dependency.md
version: 1.0.0
uuid: a48ab79d-1a98-4e34-9bdf-88ebe90a6994
author: OmniNode Team
created_at: 2025-05-22T17:18:16.684606
last_modified_at: 2025-05-22T21:19:13.491897
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 2f412ea21b0504decca346c43b01b40c0fecc755ad91d12a740bf165f80340ed
entrypoint: python@dependency.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.dependency
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Metadata Dependency Schema & Resolution

See the [Metadata Specification](../metadata.md) for the canonical overview and field definitions.

---

## Dependency Schema

Each entry in the `dependencies:` field of a metadata block includes:
- `id`: UUID of the dependency
- `type`: e.g., `tool`, `validator`, `data_artifact`
- `version_spec`: SemVer-compatible range (e.g., `>=0.1.0,<0.2.0`)
- `required`: Boolean (true if required for execution)

### Example

```yaml
# ...
dependencies:
  - id: "tool_fix_format_headers_uuid"
    type: "tool"
    version_spec: ">=0.1.0,<0.2.0"
    required: true
  - id: "data_example_uuid"
    type: "data_artifact"
    version_spec: "1.0.0"
    required: false
# ...
```

---

## Dependency Resolution

- Uses a modified Pubgrub algorithm for version solving
- Supports SemVer-compatible version ranges
- Conflicts yield descriptive errors
- Local overrides for testing supported
- Retains resolved versions in execution report

### CLI Examples

```bash
omnibase validate metadata my_file.metadata.yaml
omnibase inspect metadata validator_abc
omnibase visualize dependencies tool_xyz
```

---

## Graph Semantics

- **Node:** Any component with a UUID
- **Edge:** `depends_on`, `inherits_from`, or `generated_by`
- **Use cases:**
  - Lineage tracking
  - Impact analysis
  - Caching
  - Cycle detection

---

## Advanced Use Cases

- Transitive dependency resolution
- Cycle detection and reporting
- Impact analysis: "What depends on this component?"
- Dependency graph visualization (planned)

---

## Planned Features

- [ ] Metadata diffing and patching CLI
- [ ] Lineage tree visualizer for docs
- [ ] Trust level annotations and audit chain
- [ ] Custom metadata injection for agents

---

Return to [Metadata Deep Dives Index](index.md)
