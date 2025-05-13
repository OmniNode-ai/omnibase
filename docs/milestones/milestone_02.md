# Milestone 02 – Core Registry & Basic Orchestrators

> **Status:** Planned
> **Owners:** foundation‑team / platform‑runtime
> **Target version tag:** `v0.5.0`
> **Planned start:** 2025‑05‑25
> **Planned end (code‑complete):** 2025‑06‑21
> **Stabilisation buffer:** 1 week

---

## 1 Purpose & Overview

This milestone delivers the *minimum‑viable runtime* that lets developers **register**, **discover** and **execute** OmniBase components via a consistent orchestration layer.

* **Registry v1** – backed by PostgreSQL + local write‑through cache; provides CRUD & query API for Validators, Tools, TestCases.
* **Orchestrator v1** – command‑line entry points and core classes for the *pre‑commit* and *CI* stages.
* **CLI integration** – `omnibase list`, `omnibase cachestatus`, `omnibase orch --stage …`.

With these in place, later work (pipelines, async, advanced security) can iterate on a solid, observable runtime.

---

## 2 Scope

### In‑Scope

| Area          | Deliverable                                                                            |      |
| ------------- | -------------------------------------------------------------------------------------- | ---- |
| Registry      | PostgreSQL schema (DDL), SQLAlchemy models, CRUD service layer                         |      |
| Registry      | File‑based cache (JSON Lines) with sync job & cache‑TTL config                         |      |
| Registry      | Graph‑aware *query* endpoints (filter by tags, lifecycle, types, UUID)                 |      |
| Registry      | REST-ish internal API module (non‑network), raised errors use `RegistryError` taxonomy |      |
| Orchestrators | `PreCommitOrchestrator` & `CIOrchestrator` classes implementing `OrchestratorABC`      |      |
| Orchestrators | CLI glue: \`omnibase orch --stage pre-commit                                           | ci\` |
| Observability | Structured logging + timer metrics for all registry & orchestrator calls               |      |
| Config        | Registry + orchestrator settings in global config schema                               |      |

### Out‑of‑Scope (deferred)

* Async orchestration & task queue
* Pipeline orchestration (`PipelineOrchestrator`)
* Federated registry replication
* Web/HTTP API surface

---

## 3 Epics & Key Issues

| **Epic**                       | **Key Issues**                                                                                       |
| ------------------------------ | ---------------------------------------------------------------------------------------------------- |
| **REG‑001** – Registry Core    | *REG‑001‑01* DDL & migrations<br>*REG‑001‑02* SQLAlchemy models<br>*REG‑001‑03* CRUD service layer   |
| **REG‑002** – Cache Layer      | *REG‑002‑01* Cache write‑through impl<br>*REG‑002‑02* Sync scheduler<br>*REG‑002‑03* Cache stats CLI |
| **REG‑003** – Query Engine     | *REG‑003‑01* filter expressions<br>*REG‑003‑02* graph traversal helpers                              |
| **ORCH‑001** – Runtime ABC     | *ORCH‑001‑01* `OrchestratorABC` + `RunReport` models                                                 |
| **ORCH‑002** – Pre‑commit Impl | *ORCH‑002‑01* implementation<br>*ORCH‑002‑02* unit tests                                             |
| **ORCH‑003** – CI Impl         | *ORCH‑003‑01* implementation<br>*ORCH‑003‑02* unit tests                                             |
| **CLI‑001**                    | *CLI‑001‑01* `omnibase list` command<br>*CLI‑001‑02* `omnibase orch` command                         |

---

## 4 Acceptance Criteria

* `omnibase list validators --tag canary` returns correct rows (<100 ms for 1 k entries).
* `omnibase orch --stage pre-commit` executes at least one registered validator and exits non‑zero on failure.
* Registry functions raise typed errors (`RegistryLookupError`, etc.).
* All public classes/functions contain docstrings & type hints – `mypy --strict` passes.
* Unit test coverage ≥ 90 % for registry & orchestrator modules.
* Structured logs include `correlation_id`, `component_id`, and duration for each call.

---

## 5 Deliverables

1. **Source code** under `core/registry/`, `core/orchestrator_*.py` and `cli/`.
2. **Database migration scripts** (`alembic`).
3. **Developer guide** at `docs/registry/usage.md`.
4. **Milestone demo script**: `scripts/demo_milestone02.sh`.

---

## 6 Dependencies

* Milestone 01 – Core Protocols & Error Taxonomy (interfaces imported here)
* Dev‑tooling baseline (flake8‑omnibase rules, mypy infra)
* Postgres dev instance (Docker compose file provided in repo root)

---

## 7 Timeline & Work Breakdown

| Week | Focus                              | Expected Output                                           |
| ---- | ---------------------------------- | --------------------------------------------------------- |
| 1    | Registry DDL & models              | Passing unit tests (`REG‑001` complete)                   |
| 2    | CRUD & cache write‑through         | Cache integration tests (`REG‑002` 50 %)                  |
| 3    | Query layer & CLI `list`           | End‑to‑end list command demo                              |
| 4    | Orchestrator ABC + pre‑commit impl | `ORCH‑001`, `ORCH‑002` green; demo validates staged files |
| 5    | CI orchestrator & coverage raise   | `ORCH‑003` green; GH Actions workflow sample              |
| 6    | Docs polish & freeze               | Developer guide, milestone demo script                    |

---

## 8 Risks & Mitigations

* **DB schema churn** → freeze DDL end of week 1; later changes via migrations.
* **Perf regressions in query engine** → add regression benchmark in CI.
* **Cache desync** → write‑through + nightly forced sync job.

---

*Prepared by foundation‑team – 2025‑05‑24*
