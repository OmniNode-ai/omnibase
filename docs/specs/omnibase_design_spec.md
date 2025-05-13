# OmniBase Design Spec (canonical)

> **Note:** The full, *living* design specification for OmniBase is large (\~200 KB) and is tracked in a separate version‑controlled file to keep routine docs browsing lightweight.
>
> ▸ **Canonical file**: `docs/omnibase/omnibase_design_spec.md`
> ▸ **Current version**: v0.4.1 (2025‑05‑16)
> ▸ **Status**: Draft / Living Document

---

## Quick Navigation

| Section                    | Purpose                                                    |
| -------------------------- | ---------------------------------------------------------- |
| **Overview**               | High‑level goals, scope, and component summary             |
| **Canonical Principles**   | Seven guiding principles that drive all design choices     |
| **Repository Layout**      | Enforced two‑level directory structure & import rules      |
| **Metadata Schema**        | UUID‑backed, dependency‑aware metadata block               |
| **Unified Output Formats** | Human/JSON/YAML formatter contract & emoji map             |
| **Orchestrators**          | Pre‑commit, CI, pipeline, test, and registry orchestrators |
| **Protocols vs ABCs**      | Strict separation policy, version compatibility matrix     |
| **Configuration**          | RFC 7396 merge semantics, precedence ladder                |
| **Maintenance Policies**   | Release, deprecation, CI enforcement rules                 |
| **Addendum v0.4.1**        | Async interface, idempotency, error taxonomy, GC spec      |

> Use your editor’s outline or the table above to jump directly to the section you need.

---

## Why this wrapper file?

1. **Discoverability** – It keeps the main `docs/index.md` table small while still making the spec easy to find via repo search.
2. **Modularity** – Large design docs can evolve independently of the docs site structure.
3. **Future split‑outs** – As we extract milestone‑specific blueprints (e.g., *M1 Core Protocols*, *M2 Registry MVP*), we’ll link them here so downstream teams don’t have to hunt for context.

---

## Editing workflow

* **Minor tweaks** (typos, wording) – Edit directly in the canonical file and open a PR.
* **Major structural changes** – Propose in `docs/reviews/<yyyy-mm-dd>_*.md` first, then integrate after approval.
* **Milestone carve‑outs** – Create a new file under `docs/omnibase/milestones/` and link it below.

---

## Milestone Blueprints

| Milestone                      | Document | Status  |
| ------------------------------ | -------- | ------- |
| M1 — Core Protocol Definitions | *(TBD)*  | planned |
| M2 — Registry MVP              | *(TBD)*  | planned |
| M3 — Orchestrator Framework    | *(TBD)*  | planned |
| M4 — Security & Sandbox        | *(TBD)*  | planned |
| M5 — Observability Suite       | *(TBD)*  | planned |

---

*For the full specification, open the canonical file or view it on the docs site build.*
