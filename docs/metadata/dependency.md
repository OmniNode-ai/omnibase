<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: ee772f4a-52a8-4de4-852c-393203b00512 -->
<!-- name: dependency.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:19:59.469121 -->
<!-- last_modified_at: 2025-05-19T16:19:59.469123 -->
<!-- description: Stamped Markdown file: dependency.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: a6b502cc35a68599633881ac5166353a4a7b05f323961d6ba284593acba11486 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'dependency.md'} -->
<!-- namespace: onex.stamped.dependency.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

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
