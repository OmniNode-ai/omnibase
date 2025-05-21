<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: lineage.md -->
<!-- version: 1.0.0 -->
<!-- uuid: ef4d7b22-f582-421f-bd14-aa6094598c03 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.158916 -->
<!-- last_modified_at: 2025-05-21T16:42:46.084733 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 2387b84edac9452f4a0a82021aede7607c33c57adfad17ff91d9d34ba9696be3 -->
<!-- entrypoint: {'type': 'python', 'target': 'lineage.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.lineage -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: lineage.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 442f1c63-8cc1-42cd-9efb-24f919895449 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.433926 -->
<!-- last_modified_at: 2025-05-21T16:39:56.128407 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 20b5efc1ca5b4b204fd493dcb75995109ee79aaf576ccf62503ea623210bcf86 -->
<!-- entrypoint: {'type': 'python', 'target': 'lineage.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.lineage -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: lineage.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 1e7d2e32-8057-4905-84f4-799dc1233bce -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.662192 -->
<!-- last_modified_at: 2025-05-21T16:24:00.293480 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 47acd147de994798dd382ba06f1ad179712ed59702db4a99e95f0cbf60895233 -->
<!-- entrypoint: {'type': 'python', 'target': 'lineage.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.lineage -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

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
