<!-- OmniBase Milestone 11: Version Compatibility Checker & Migration Toolkit -->

# Milestone 11 – Version Compatibility Checker & Migration Toolkit

> **Status:** Planned
> **Target Release:** 0.11.x
> **Lead:** Platform Tooling Squad
> **Last Updated:** 2025‑05‑16

---

## 1 Goals

* Provide an automated command‑line toolset (`omnibase compat`) that:

  * Detects version incompatibilities across **metadata**, **protocols**, **ABCs**, and **registries**.
  * Generates a *compatibility matrix* (MarkDown + JSON) for CI publishing.
  * Offers guided and, where possible, **automated migrations** for out‑of‑range components.
* Integrate compatibility checks into pre‑commit, CI, and orchestrator pipelines (block on `INCOMPATIBLE`, warn on `WARNING`).
* Supply a migration *lint* mode that outputs remediation steps without performing changes.

## 2 Scope

| In‑scope                                                              | Out‑of‑scope                                               |
| --------------------------------------------------------------------- | ---------------------------------------------------------- |
| SemVer parsing & rule engine (major/ minor / patch policy).           | Deep refactoring of legacy code.\*                         |
| CLI sub‑command & API hooks.                                          | Automatic code transpilation across languages.             |
| JSON report + Markdown matrix generator.                              | Runtime shim layers for incompatible versions.             |
| Migration stubs (YAML transforms, module renames, template rewrites). | Registry replication / federation upgrades (Milestone 14). |

> \*Legacy refactor scripts will be handled in Milestone 13.

## 3 Deliverables

1. **`compat` Engine** – core Python module implementing:

   * `parse_version()`, `compare()`, `resolve_constraints()`.
   * `check_component()` returning `COMPATIBLE | WARNING | INCOMPATIBLE`.
2. **CLI Sub‑command**

   ```bash
   omnibase compat scan [--format human|json] [path|--registry]
   omnibase compat migrate [--dry-run] <component‑id>
   ```
3. **CI Integration** – GitHub Action + pre‑commit hook executing `compat scan`.
4. **Artifacts** – Markdown & JSON matrices stored in `docs/compat/` per build.
5. **Migration Recipes** – YAML‑driven transformation library (e.g., renaming `__protocol_version__`).

## 4 Acceptance Criteria

* 🟢 *All* existing components pass `compat scan` (no `INCOMPATIBLE`).
* CI fails build if new PR introduces incompatibility without migration recipe.
* CLI supports human, JSON, YAML output consistent with Unified Output Formats.
* Migration command can automatically update at least **80 %** of outdated metadata blocks in internal test suite.

## 5 Timeline (T‑shirt sizing)

| Phase          | Duration | Window          |
| -------------- | -------- | --------------- |
| Design & RFC   | 1 week   | May 19 – May 26 |
| Implementation | 2 weeks  | May 27 – Jun 9  |
| Internal QA    | 1 week   | Jun 10 – Jun 17 |
| Public Beta    | 1 week   | Jun 18 – Jun 25 |
| GA Release     | 2 days   | Jun 26 – Jun 27 |

## 6 Dependencies

* **Milestone 1–6** – Core protocols, registry, and security model must be available.
* **Milestone 10** – Configuration cascade for enabling/disabling checks.

## 7 Risks & Mitigations

| Risk                                    | Impact                    | Mitigation                                                       |
| --------------------------------------- | ------------------------- | ---------------------------------------------------------------- |
| Explosion of edge‑case migration paths. | Delays + fragile scripts. | Focus on 80 % automated + manual fallback docs.                  |
| False positives blocking CI.            | Developer friction.       | Provide `--override` flag requiring explicit justification note. |
| Large compatibility matrix size.        | Slow builds.              | Cache previous run, diff only changed rows.                      |

## 8 Stretch Goals

* **IDE Plugin** showing live compatibility warnings.
* **Visualization UI** in Docs site (heatmap of component versions).
* **Registry‑level policy** to auto‑reject incompatible uploads.

---

### Notes

\* Interfaces align with the Compatibility Enum & `check_compat()` reference implementation in the design spec.
\* Migration recipes reuse JSON Merge Patch (RFC 7396) semantics for config updates.

> End of Milestone 11 document.
