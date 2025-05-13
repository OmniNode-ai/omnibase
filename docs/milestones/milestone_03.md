```markdown
# Milestone 03 – CLI Foundation & Unified Output Formatters

> **Status:** Draft  
> **Location:** docs/milestones/milestone_03_cli_output_formatters.md  
> **Maintainers:** tooling-team (lead: @cli-lead)  
> **Target Start:** 2025‑06‑02  
> **Target Finish:** 2025‑06‑23  
> **Duration:** 3 weeks (+1 week stabilization)  
> **Depends‑on:** Milestone 02 (Core Registry & Basic Orchestrators)

---

## 1  Purpose
Establish a cohesive **command‑line interface** that developers, CI systems, and agents can use to interact with OmniBase.  Deliver a plug‑in formatter subsystem that renders CLI output in **human**, **JSON**, and **YAML** styles (per Unified Output Formats spec).

This milestone provides the primary user entry‑point and is the first vertically‑integrated slice touching core protocols, registries, orchestrators, and formatting utilities.

---

## 2  Scope
* **CLI binary:** `omnibase` single‑entry command with sub‑commands.
* **Formatter plug‑in registry:** `omnibase.cli.formatters` auto‑discovery & versioned API.
* **Initial commands** (read‑only):
  * `omnibase list` (validators | tools | pipelines | tests)
  * `omnibase inspect metadata <uuid-or-path>`
  * `omnibase schema describe <schema-name>`
  * `omnibase orch --stage <stage>` (delegates to orchestrator from M02)
* **Global flags:** `--format`, `--no-color`, `--verbose`, `--help`.
* **Human formatter features:** ANSI color, emoji fallbacks, ≤100‑char line wrapping.
* **Machine formatters:** Canonical key order, stable schema, YAML block style.

_Out‑of‑scope:_ Mutating commands (e.g., `omnibase register …`), auth, remote execution.

---

## 3  Epics & Tasks
| ID | Epic | Description | Owner |
|----|------|-------------|-------|
| CLI‑E1 | **Argument Parsing & Sub‑command Router** | Scaffold `omnibase` click/typer‑based entry; route to handlers. | @cli‑lead |
| CLI‑E2 | **Formatter Plug‑in System** | Implement versioned registry; load formatters by entry‑point group `omnibase.formatter`. | @format‑guru |
| CLI‑E3 | **Human Formatter** | Color + emoji + width handling; respects `TERM`, `CI`, `--no-color`. | @ux‑dev |
| CLI‑E4 | **JSON/YAML Formatters** | Canonical ordering, error object schema compliance. | @api‑dev |
| CLI‑E5 | **List Command Family** | Wire to `Registry.query()`; support tag/phase filters. | @cli‑lead |
| CLI‑E6 | **Inspect Metadata** | Pretty‑print raw YAML & validate against schema. | @cli‑lead |
| CLI‑E7 | **Schema Describe** | Dump generated JSON Schema for a given model. | @schema‑maint |
| CLI‑E8 | **Orchestrator Bridge** | Pass‑through to `omnibase.core.orchestrator_*` modules; stream formatter output. | @cli‑lead |
| CLI‑E9 | **Unit & Snapshot Tests** | 90% coverage; golden output snapshots for each formatter. | @qa‑team |
| CLI‑E10 | **Docs & Examples** | Update README + new `docs/cli/usage.md`; asciinema casts. | @doc‑team |

---

## 4  Acceptance Criteria
* Running `omnibase --help` shows sub‑commands and global flags.
* `omnibase list validators --format json` returns valid JSON matching schema.
* `omnibase inspect metadata docs/examples/validator.yaml` exits 0 and prints colored human output when in TTY.
* Formatters auto‑registered via Python entry‑points; adding a new formatter requires **no core‑code change**.
* All commands respect `OMNIBASE_*` env vars and config cascade.
* CI job executes `omnibase list` with each formatter and diff‑checks against golden snapshots.

---

## 5  Deliverables
* **Source:** `cli/` package, `omnibase` console‑script entry.
* **Formatter Registry:** `cli/formatters/__init__.py` with auto‑loader.
* **Docs:** `docs/cli/usage.md`, updated diagrams.
* **Test Suite:** pytest folder `tests/cli/` with snapshot fixtures.
* **Release Artifacts:** PyPI wheel `omnibase‑cli‑0.1.0`, changelog entry.

---

## 6  Timeline
| Week | Focus |
|------|-------|
| W1 | CLI scaffold (E1), formatter registry (E2) |
| W2 | Human + JSON/YAML formatters (E3‑E4) |
| W3 | Command handlers (E5‑E7), docs (E10) |
| W4 | Stabilization, test hardening (E8‑E9), release tag v0.1.0 |

_Parallel Work_: UX design for emoji/icons and color palette can start during W1.

---

## 7  Risks & Mitigations
* **Formatter schema drift** → enforce via JSON Schema tests & snapshot CI.
* **Color/emoji compatibility** → automatic fallback path, manual `--no-color` flag.
* **Command surface creep** → lock scope; mutation commands deferred to M04.

---

## 8  Dependencies
* Milestone 02 registry query API (`Registry.query`) must be available.
* Unified Output Format spec frozen (already in v0.4.1 spec).
* Error object schema (M01) must be importable by formatter code.

---

## 9  Notes
* We’re using **Typer** for CLI (Click 8 underneath) to minimize boilerplate.
* Formatter plug‑ins use `typing.Protocol` interface `BaseFormatter` with `_SCHEMA_VERSION` to version.
```
