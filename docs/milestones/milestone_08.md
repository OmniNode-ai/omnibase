## Milestone 8 ― Federated Registry & Marketplace

### Objective

Build out support for **distributed, federated OmniBase registries** so that independent organizations (or teams) can publish, discover, and reuse validators, tools, and pipelines while retaining sovereignty over their own infrastructure.

### Key Outcomes

1. **Federation Protocol (v1)**  ‒ gRPC + OpenAPI definitions for cross‑registry discovery, metadata exchange, and artifact pull‑through.
2. **Trust & Capability Policies**  ‒ integrate Cedar‑based policy engine for fine‑grained allow/deny rules when mirroring or executing remote components.
3. **Selective Sync CLI**  ‒ `omnibase registry sync <remote> [--include tag=stable]` with resumable, content‑addressable transfers.
4. **Marketplace UI/CLI**  ‒ list/search external components, show provenance & security scorecard, one‑click import into local registry.
5. **Security Hardening**  ‒ mutual‑TLS between registries, OIDC tokens for identity, automated vulnerability scanning on import.
6. **Observability Hooks**  ‒ cross‑registry metrics (latency, error rates), trace propagation, audit logging of import/export events.

### Deliverables

| # | Artifact                          | Owner           | Definition of Done                                             |
| - | --------------------------------- | --------------- | -------------------------------------------------------------- |
| 1 | `federation.proto` + OpenAPI spec | foundation‑team | Merged, version‑tagged (`REGISTRY_PROTO v1`), lint passes      |
| 2 | Go + Python reference gateway     | core‑infra      | Passes conformance suite, handles 10k QPS mock load            |
| 3 | Cedar policy pack templates       | security‑team   | ≥ 90% coverage in policy tests                                 |
| 4 | CLI sync command                  | cli‑team        | End‑to‑end sync of >1 GB artifacts in <15 min on 100 Mbps link |
| 5 | Web marketplace (React)           | ux‑team         | Deployed preview behind feature flag, UX review signed off     |
| 6 | Pen‑test report                   | sec‑ops         | All high/critical findings fixed or accepted w/ waiver         |

### Timeline

*Speculative* – subject to quarterly planning

* **Kick‑off:** 2025‑09‑01
* **Alpha (interop demo):** 2025‑10‑15
* **Beta (public preview):** 2025‑11‑30
* **GA:** 2026‑01‑31

### Risks & Mitigations

| Risk                            | Likelihood | Impact | Mitigation                                                     |
| ------------------------------- | ---------- | ------ | -------------------------------------------------------------- |
| Trust policy complexity         | Med        | High   | Ship opinionated defaults; provide wizards & templates         |
| Network variability             | Med        | Med    | Implement chunked, resumable transfers + back‑pressure         |
| Security surface expansion      | High       | High   | Mandatory pen‑test + continuous vulnerability scanning         |
| Version skew between registries | Med        | Med    | Embed compatibility negotiation; fall back to read‑only mirror |

### Exit Criteria

* Federation protocol tests green across 3 independent registries
* Selective sync CLI copies tagged subset with byte‑for‑byte integrity
* Marketplace lists >200 remote components with live provenance data
* Cedar policies evaluated in <10 ms P95 during import/execution guard
* Security audit signed‑off (no criticals, ≤2 medium outstanding)

---

*Approved by foundation‑team / Milestone owner: @omnibase‑pm*
