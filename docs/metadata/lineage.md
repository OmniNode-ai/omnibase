# Metadata Lineage & Federation

See the [Metadata Specification](../metadata.md) for the canonical overview and field definitions.

---

## Registry Federation

OmniBase supports a federated registry model for distributed, multi-org collaboration.

### Federation Modes
| Mode         | Description                                      |
|--------------|--------------------------------------------------|
| Centralized  | One authoritative registry, local caches         |
| Hierarchical | Parent-child registries, policy-controlled sync  |
| Mesh         | Peer-to-peer sync across trusted registries      |

Default: centralized → optional mesh with ACLs

### Sync Patterns
- Pull-only: local registry pulls from upstream (read-only)
- Push: changes propagate to remote registries (if permitted)
- Partial sync: filter by tags, lifecycle, namespace
- Full sync: entire DAG of referenced entries

Each registry can define sync rules in `registry/config.yml`.

### Security Controls
- Signature-based verification of remote metadata
- Trust roots for federation
- Version pinning of critical components
- Audit logs of federation events
- Optional sandboxing of newly pulled components

---

## Metadata Lineage Graph

Each metadata block supports:
- `parent_id`: single upstream (inheritance)
- `child_ids`: list of known descendants
- `dependencies`: typed, versioned edges
- `produced_by`: execution UUID or agent ID

Lineage graph forms a directed acyclic graph (DAG).

### Use Cases
- Trace validator ancestry for debugging
- Replay execution history of toolchains
- Visualize test case evolution
- Filter components derived from agent-generated roots
- Detect component drift via lineage comparison

---

## Lineage Visualizer (Planned)

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

## Planned Deliverables
- [ ] Federated sync agent and ACL config
- [ ] Lineage graph extract + diff tool
- [ ] Visualization engine (CLI first)
- [ ] Trust and signature enforcement CLI
- [ ] Provenance-aware execution logs

---

Return to [Metadata Deep Dives Index](index.md) 