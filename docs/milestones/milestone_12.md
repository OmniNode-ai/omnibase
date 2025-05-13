# OmniBase Consolidated Roadmap — Milestones 12 → 21

> **Status:** Planned
> **Scope:** Combines the remaining milestones into a single, umbrella document to accelerate approval & onboarding.
> **Last Updated:** 2025‑05‑16

---

## Purpose

This document groups the final ten milestone tracks (originally 12 → 21) into one reference so teams can plan, cross‑link, and de‑risk work without flipping among many files. Each section follows the **Problem → Solution → Deliverables → Acceptance** pattern that earlier milestone docs use.

---

## M12 – Function‑Composition Framework

### Problem

Complex validator/tool pipelines require ergonomic composition, dependency resolution, and parallel execution support.

### Solution Synopsis

* Build a DAG‑based composition engine that consumes YAML/JSON pipeline descriptors.
* Support topological sort, automatic fan‑out/fan‑in, and cycle detection.
* Integrate with Orchestrator for execution scheduling.

### Deliverables

1. `core/composition/engine.py` (API: `compose(pipeline_spec) -> Pipeline`)
2. DSL schema (`schema/pipeline_descriptor.schema.json`)
3. Unit & integration tests (covering DAG creation, error paths, and execution order)

### Acceptance Criteria

* Given a valid descriptor the engine resolves, orders, and executes ≥ 95 % of reference pipelines in <1 s.
* Rejects cycles with a clear `PipelineCycleError`.

---

## M13 – Metrics & Instrumentation Framework

### Problem

Lack of standard telemetry impairs observability, capacity planning, and SLA enforcement.

### Solution Synopsis

* Provide `core/observability/metrics.py` collector (single‑ton pattern) with pluggable reporters.
* Default reporters: stdout (dev), Prometheus (prod), OTLP (cloud).
* Offer decorator `@timed("metric.name")` and context manager `TimerContext`.

### Deliverables

1. Pydantic model `Metric`
2. Prometheus exporter under `adapters/prometheus/`
3. Docs & examples in `docs/observability/metrics.md`

### Acceptance Criteria

* Metrics emitted from sample pipeline visible in Prometheus UI within 5 s.

---

## M14 – Unified Output Formatter Implementation Snapshot

*(Marked **in‑progress** earlier – this milestone finalises and documents the human/json/yaml formatter work.)*

### Key Tasks Remaining

* Stabilise emoji/ASCII fallback mapping tables.
* Finalise JSON schema versioning.
* Add Golden tests verifying byte‑for‑byte output with `TERM=dumb`.

### Hard Exit Criteria

* CI job `formatter‑snapshot` passes with no diff on locked fixtures.

---

## M15 – Orchestrator Scaffolds

| Orchestrator | Use‑case              | Binary                             | Config Key                  |
| ------------ | --------------------- | ---------------------------------- | --------------------------- |
| Pre‑Commit   | local validation hook | `omnibase orch --stage pre‑commit` | `orchestrator.pre_commit.*` |
| CI           | headless validation   | `--stage ci`                       | `orchestrator.ci.*`         |
| Pipeline     | DAG execution         | `--stage pipeline`                 | `orchestrator.pipeline.*`   |
| Test         | registry test harness | `--stage test`                     | `orchestrator.test.*`       |
| Registry     | admin operations      | `--stage registry`                 | `orchestrator.registry.*`   |

### Deliverables

* Individual `core/orchestrator_<stage>.py` modules with a shared `BaseOrchestrator` ABC.
* CLI wiring via `cli/orch.py`.

---

## M16 – Repository Restructure Migration Plan

### Scope

Transition existing mono‑repo to the 2‑level directory rule without breaking import paths.

### Migration Phases

1. **Analysis:** Map current files → future location (generate CSV).
2. **Shim Phase:** Introduce import forwarders with deprecation warnings.
3. **Cut‑over:** Move files; drop shims one minor version later.

### Key Artifact

* `docs/migrations/2025‑repo‑refactor.md` with step‑by‑step guide & timeline.

---

## M17 – `flake8‑omnibase` Rule OB101 Guide

*Rule OB101: Block runtime imports from `protocols.testing`.*

### Implementation Steps

1. Extend plugin AST walker to flag `ImportFrom` & `Import` nodes matching `omnibase.protocols.testing`.
2. Provide automated fixer suggestion via `--omnibase‑fix` flag.

### Guide Content

* Rationale, examples, suppression pattern.

---

## M18 – Schema‑Doc Generation Toolkit

### Goal

Auto‑produce JSON‑Schema, OpenAPI, and human docs from Pydantic models & Protocols.

### Planned Stack

* `datamodel‑code‑generator` or `pydantic‑schemas` for JSONSchema.
* `mkdocs + mkdocstrings` for human docs.
* GitHub Actions job `schema‑docs` generating site under `docs/api/*`.

---

## M19 – Version‑Compatibility Checker & Matrix Tooling

### Deliverables

1. Library `core/compat/check.py` (implements table & enum from spec).
2. CLI `omnibase compat` producing Markdown or CSV matrices.
3. CI job `compat‑matrix` gating merges if new incompatibilities introduced.

---

## M20 – Hierarchical Configuration System Spec

* Formalise YAML schema with `$merge`, `$delete` operations following RFC 7396.
* Provide `ConfigManager` (see earlier code snippet) plus hot‑reload watcher.
* Include security considerations (redaction, secret placeholders).

---

## M21 – Full `flake8‑omnibase` Plugin Blueprint

Beyond OB101, the plugin will include:

* **OB102:** Enforce `SCHEMA_VERSION`/`__protocol_version__` constant presence.
* **OB103:** Maximum directory depth check in path analysis.
* **OB104:** Ban direct use of `print()` in production code.

### Roadmap

1. Draft rule specs → community review.
2. Implement & release `v0.1.0` (OB101‑103).
3. Enable in repo CI; iterate based on false positives.

---

## Global Acceptance Gate

*All consolidated milestones enter **beta‑complete** state when:*

* CI passes with **all** new jobs (`metrics`, `formatter‑snapshot`, `compat‑matrix`).
* Docs site auto‑publishes from `main` with generated schema pages.
* First real pipeline composed & executed via new Composition Framework.

---

> **Next Action:** break out task tickets per milestone section and assign owners in the project board.
