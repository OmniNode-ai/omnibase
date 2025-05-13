# Milestone 04 – Registry MVP

> **Status:** Planned
> **Owner:** Registry Squad (core + infra)
> **Target Version:** v0.6.x
> **ETA:** 4 weeks after Milestone 03 exit

---

## 1 – Objective

Deliver a production‑ready **Validator/Tool/Test Registry** that supports basic CRUD operations, metadata validation, dependency graph queries, and local write‑through caching. This unlocks component discoverability, provenance tracking, and orchestration.

## 2 – Scope

* **Authoritative store**: PostgreSQL schema with JSONB columns for metadata and indices for UUID, tags, lifecycle, and version.
* **Registry API** (python package `omnibase.core.registry`):

  * `register(component_meta: Metadata) -> UUID`
  * `update(uuid, patch: MetadataPatch)` (RFC 7396 merge semantics)
  * `lookup(uuid | name, *, version_spec=None) -> Metadata`
  * `search(tags=[], type=None, lifecycle=None, text=None) -> Iterable[Metadata]`
  * `dependency_graph(root_uuid) -> Graph`
* **Validation layer**: Pydantic models + JSON Schema for metadata; rejects non‑conformant entries.
* **Local cache**: file‑based, write‑through with periodic background sync; readonly fallback for air‑gapped execution.
* **CLI integration**:

  * `omnibase registry add <metadata.yml>`
  * `omnibase registry ls --tag canary`
  * `omnibase registry get <uuid>`
* **Observability**: structured logs, registry‑specific metrics (`total_components`, `query_latency_ms`, `cache_hit_ratio`).
* **Security hook**: capability checks for `REGISTRY_READ/WRITE`.

*Out of scope*: federation, advanced diff queries, RBAC UI, soft‑delete/archival policies.

## 3 – Deliverables

| #  | Deliverable                      | Description                                                                         |
| -- | -------------------------------- | ----------------------------------------------------------------------------------- |
| D1 | `omnibase.core.registry` package | DB models, service layer, cache implementation                                      |
| D2 | Alembic migrations               | Declarative schema, CI migration smoke test                                         |
| D3 | Metadata validator               | Pydantic + jsonschema, CLI `omnibase validate metadata` now backed by same routines |
| D4 | Basic CLI commands               | `registry add/ls/get` with human/json/yaml output                                   |
| D5 | Grafana dashboard JSON           | Latency + ops/s + cache metrics                                                     |
| D6 | Runbooks                         | Ops docs for DB backup/restore, cache purge, troubleshooting                        |

## 4 – Timeline (4 weeks)

| Week | Goals                                                                             |
| ---- | --------------------------------------------------------------------------------- |
| 1    | Finalize DB schema & Pydantic models; stand‑up local Postgres in dev‑containers   |
| 2    | Implement CRUD service + validator; unit tests (≥90 % coverage)                   |
| 3    | File‑cache layer + sync daemon; integration tests; observability hooks            |
| 4    | CLI wiring, docs, load‑test (10 k components < 100 ms P95); release candidate tag |

## 5 – Exit Criteria

* ✅ All deliverables merged to `main`
* ✅ End‑to‑end demo: register ⇒ lookup ⇒ dependency\_graph within 150 ms
* ✅ Unit + integration tests passing in CI; coverage ≥ 90 %
* ✅ Load test: 50 concurrent writes, 200 concurrent reads sustain 500 ops/s with < 300 ms P95
* ✅ Deployment manifests (docker‑compose / k8s) published

## 6 – Dependencies

* Milestone 01 protocols (stable identifiers)
* Milestone 03 formatter CLI foundation
* Cloud‑hosted Postgres instance provisioned by DevOps

## 7 – Risks & Mitigations

| Risk                              | Impact          | Likelihood | Mitigation                                                   |
| --------------------------------- | --------------- | ---------- | ------------------------------------------------------------ |
| Schema churn from protocol tweaks | Migration churn | Med        | Freeze core metadata schema v0.3 pre‑dev; use SQL migrations |
| Cache consistency lag             | Stale reads     | Low        | TTL config + explicit `registry sync` command                |
| DB performance under load         | Slow lookups    | Low        | Indices + connection pool + perf tests                       |

## 8 – Acceptance Tests (BDD‑style)

```
Scenario: Register new validator
  Given a valid metadata file "validator.yml"
  When I run "omnibase registry add validator.yml"
  Then the command exits 0
  And the output contains "registered: true"
  And "validator.yml" UUID is retrievable via "registry get"

Scenario: Reject invalid metadata (missing uuid)
  Given an invalid metadata file "bad.yml"
  When I run "omnibase registry add bad.yml"
  Then the command exits with code 2
  And stderr contains "MetadataValidationError"

Scenario: Dependency graph API
  Given a component UUID "abc-123"
  When I call `dependency_graph(abc-123)`
  Then the result is a DAG with >=1 node
```

---

> *Next planned milestone*: **Milestone 05 – Security Model & Sandbox (Capability‑based + gVisor)**
