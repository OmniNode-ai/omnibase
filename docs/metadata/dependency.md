<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: dependency.md -->
<!-- version: 1.0.0 -->
<!-- uuid: d1b57d56-3e8f-4cbc-a673-fa14c7cf726c -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.158769 -->
<!-- last_modified_at: 2025-05-21T16:42:46.082854 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 0a558c044572240dbef1643b2e9405d7b940f0b847c476f6849ca3e6199b37f4 -->
<!-- entrypoint: {'type': 'python', 'target': 'dependency.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.dependency -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: dependency.md -->
<!-- version: 1.0.0 -->
<!-- uuid: c39b84e1-0b1c-4110-9a33-e09b06657ffa -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.433767 -->
<!-- last_modified_at: 2025-05-21T16:39:56.126448 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 465883945e1e77d7c49b96b24c45bbc3dbdae2b4b0c57dc951a9ee9cc7499df5 -->
<!-- entrypoint: {'type': 'python', 'target': 'dependency.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.dependency -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: dependency.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 4090b507-90dd-4530-95a0-efee6b8d59ea -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.662058 -->
<!-- last_modified_at: 2025-05-21T16:24:00.292322 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 17a9d7d6a6c5cebb72419708e48137630dd013217164f7249135db7b124b016a -->
<!-- entrypoint: {'type': 'python', 'target': 'dependency.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.dependency -->
<!-- meta_type: tool -->
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
