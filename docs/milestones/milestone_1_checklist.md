# Milestone 1 Implementation Checklist: ONEX Node Protocol, Schema, Metadata, and CI Enforcement

> **Status:** Canonical
> **Last Updated:** 2025-05-16
> **Purpose:** This checklist enumerates all implementation steps required to complete Milestone 1 of the ONEX Execution Architecture. Each item is actionable, testable, and maps directly to the deliverables in [onex_execution_architecture.md](./onex_execution_architecture.md).

## Implementation Flow Overview

The Milestone 1 implementation bootstraps the ONEX system by defining the schemas, metadata contracts, and validation tooling that power future milestones. The high-level flow is:

1. Define `.onex` metadata schema (describes a node)  
2. Define `.tree` file format (indexes node locations in directory)  
3. Define `state_contract` (describes expected I/O/state for node)  
4. Define `execution_result` format (standardizes node output)  
5. Implement validation tools and stampers  
6. Enforce schema/lifecycle/structure correctness via CI  
7. Prepare for M2: runtime loader that will execute these nodes  

## Guiding Principles

- **Schema-First**: All node types and execution outputs must be schema-defined and validated from day one.  
- **CI Is Law**: No node can merge unless it passes CI schema validation and structural checks.  
- **Fail Fast**: Design CI to catch lifecycle, hash, and linkage issues early in development.  
- **Metadata as Code**: Metadata must be canonical, discoverable, and tracked like code.  
- **Recursive Bootstrapping**: M1 enables the runtime in M2, which runs the scaffold node that creates M1-valid node definitions.  

---

## IMPLEMENTATION CHECKLIST

### Schema & Protocol Definition
- [x] Define canonical `.onex` metadata schema (YAML-based, with explicit required fields and types)  
    Defines the metadata block for each node; referenced by `.tree`  
    - **DoD:** Schema file merged to main, referenced in docs, reviewed by Infra lead  
    - **Artifact:** `/schemas/onex_node.yaml`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [x] (YAML schema, Pydantic model, and extractor utility are now fully aligned and implemented. All field names, types, and constraints are enforced per the canonical schema.)  
    - **PR/Issue:** #  
    - [x] Unit/integration tests written and passing  
    - [x] Usage example in docs  
- [x] Define canonical `.tree` directory structure format for node discovery (with explicit required fields)  
    Defines the discoverable directory structure; references `.onex` files for each node  
    - **DoD:** Format documented, sample `.tree` file in repo, reviewed by CAIA  
    - **Artifact:** `/schemas/tree_format.yaml`  
    - **Reviewer(s):** CAIA  
    - **Status:** [x]  
    - **PR/Issue:** #  
    - [x] Unit/integration tests written and passing  
    - [x] Usage example in docs  
- [x] Add dual-format support for .tree files (YAML and JSON)  
    - **DoD:** Both .tree (YAML) and .tree.json (JSON) formats are supported, validated, and documented  
    - **Artifact:** `/schemas/tree_format.yaml`, `/schemas/tree_format.json`, example .tree.json file in repo  
    - **Reviewer(s):** CAIA  
    - **Status:** [x]  
    - [x] Unit/integration tests written and passing for both formats  
    - [x] Usage example in docs  
    - **Note:** [2024-06-09] Full audit completed: schemas, tests, docs, and examples for both formats are present and passing. See `tests/tools/test_tree_discovery.py` and `docs/registry.md` for details.
- [x] Define canonical `execution_result` schema for node output (YAML and JSON)  
    - **DoD:** Schema files merged in both formats, referenced in docs, reviewed by Runtime owner  
    - **Artifact:** `/schemas/execution_result.yaml`, `/schemas/execution_result.json`  
    - **Reviewer(s):** Runtime owner  
    - **Status:** [x]  
    - [x] Unit/integration tests written and passing for both formats  
    - [x] Usage example in docs  
    - **Note:** [2024-06-09] Full audit completed: schemas, tests, docs, and examples for both formats are present and passing. See `tests/schema/test_execution_result.py` and `docs/registry.md` for details.
- [x] Define canonical `state_contract` schema (YAML and JSON)  
    - **DoD:** Schema files merged in both formats, referenced in `.onex`, reviewed by Foundation team  
    - **Artifact:** `/schemas/state_contract.yaml`, `/schemas/state_contract.json`  
    - **Reviewer(s):** Foundation team  
    - **Status:** [x]  
    - [x] Unit/integration tests written and passing for both formats  
    - [x] Usage example in docs  
    - **Note:** [2024-06-09] Full audit completed: schemas, tests, docs, and examples for both formats are present and passing. See `tests/schema/test_state_contract.py` and `docs/registry.md` for details.
- [x] Add SCHEMA_VERSION field and create schema changelog/migration doc  
    - **DoD:** Versioning field present in all schemas, changelog doc published  
    - **Artifact:** `/schemas/SCHEMA_VERSION`, `/docs/changelog.md`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [x]  
    - [x] Changelog entry created  
    - [x] Deprecation policy documented  
    - **Note:** [2024-06-09] Full audit completed: SCHEMA_VERSION field, changelog, and deprecation policy are present and committed for all canonical schemas.

### Tooling & Automation
- [x] Build protocol docstring/Markdown doc generator for all schemas  
    - **DoD:** Tool generates docs for all schemas, output reviewed by CAIA  
    - **Artifact:** `/tools/docstring_generator.py`, `/docs/generated/`  
    - **Reviewer(s):** CAIA  
    - **Status:** [x]  
    - [x] Usage example in docs  
    - **Note:** [2024-06-09] Full audit completed: tool, generated docs, and usage example are present and passing. See `docs/generated/` and `docs/registry.md` for details.
- [ ] Write Node Author Quickstart guide (README)  
    - **DoD:** Guide published, tested by new contributor, reviewed by Foundation team  
    - **Artifact:** `/docs/quickstart.md`  
    - **Reviewer(s):** Foundation team  
    - **Status:** [ ]  
    - **PR/Issue:** #  
    - [ ] Usage example in docs  
    - [ ] Quickstart tested by new contributor  
- [ ] Build metadata stamper and `.onex` validator CLI tool  
    - **DoD:** Tool validates `.onex` files, integrated in CI, reviewed by Infra lead  
    - **Artifact:** `/tools/onex_validator.py`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [ ]  
    - **PR/Issue:** #  
    - [ ] Unit/integration tests written and passing  
    - [ ] Usage example in docs  
- [ ] Build CLI tool for automated `.tree` generation and validation  
    - **DoD:** Tool generates/validates `.tree`, integrated in CI, reviewed by CAIA  
    - **Artifact:** `/tools/tree_generator.py`  
    - **Reviewer(s):** CAIA  
    - **Status:** [ ]  
    - **PR/Issue:** #  
    - [ ] Unit/integration tests written and passing  
    - [ ] Usage example in docs  

### CI & Enforcement
- [ ] Integrate CI enforcement: all nodes must pass schema validation for metadata, execution result, and state contract  
    - **DoD:** CI blocks non-compliant commits, reviewed by Infra lead  
    - **Artifact:** `.github/workflows/ci.yml`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [ ]  
    - **PR/Issue:** #  
    - [ ] CI test coverage for all enforcement logic  
- [ ] Integrate CI enforcement: `.tree` file must match directory contents and reference valid `.onex` files  
    - **DoD:** CI blocks drift, reviewed by CAIA  
    - **Artifact:** `.github/workflows/ci.yml`  
    - **Reviewer(s):** CAIA  
    - **Status:** [ ]  
    - **PR/Issue:** #  
    - [ ] CI test coverage for all enforcement logic  
- [ ] Integrate CI enforcement: lifecycle field must be valid and hash-stamped  
    - **DoD:** CI blocks invalid lifecycle/hash, reviewed by Infra lead  
    - **Artifact:** `.github/workflows/ci.yml`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [ ]  
    - **PR/Issue:** #  
    - [ ] CI test coverage for all enforcement logic  
- [ ] Add pre-commit hooks for schema validation and `.tree` sync  
    - **DoD:** Hooks block non-compliant commits locally, reviewed by Foundation team  
    - **Artifact:** `.pre-commit-config.yaml`  
    - **Reviewer(s):** Foundation team  
    - **Status:** [ ]  
    - **PR/Issue:** #  
- [ ] Add CI metrics dashboard (badge or report in README)  
    - **DoD:** Dashboard live and reporting, reviewed by Infra lead  
    - **Artifact:** `/README.md`, `/docs/metrics_dashboard.md`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [ ]  
    - **PR/Issue:** #  
    - [ ] Metrics reporting tested  
- [ ] Write test cases for schema evolution and backward compatibility  
    - **DoD:** Test cases merged, reviewed by Foundation team  
    - **Artifact:** `/tests/schema_evolution/`  
    - **Reviewer(s):** Foundation team  
    - **Status:** [ ]  
    - **PR/Issue:** #  
- [ ] Document node lifecycle policy (draft, review, active, deprecated)  
    - **DoD:** Policy published in docs, reviewed by CAIA  
    - **Artifact:** `/docs/lifecycle_policy.md`  
    - **Reviewer(s):** CAIA  
    - **Status:** [ ]  
    - **PR/Issue:** #  
- [ ] Define and enforce canonical error taxonomy for validation failures  
    - **DoD:** Error taxonomy published and used in all tools, reviewed by Infra lead  
    - **Artifact:** `/docs/error_taxonomy.md`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [ ]  
    - **PR/Issue:** #  

### Additional Checks
- [x] Add yamllint to pre-commit hooks for schema validation  
    - **DoD:** yamllint runs on all YAML files before commit  
    - **Status:** [x]  

- [x] All YAML schema/model/test alignment and enforcement  
    - **DoD:** All schemas, models, and tests are in sync and pass CI  
    - **Status:** [x]  

- [ ] Reducer snapshot test (deferred)  
    - **Note:** Deferred until reducer protocol is fully specified in M2. See `tests/protocol/test_reducer_snapshot.py` for stub.  

---

## Optional Enhancements (Stretch Goals or M2 Prep)

*These items are not required for Milestone 1 completion but are recommended for enhanced quality or preparation for future milestones. Mark priority and milestone relevance as appropriate.*

- [ ] Implement plugin validation hook system for custom/org-specific checks  
    - **Priority:** Recommended for M2  
    - **DoD:** Plugin system available and documented  
    - **Artifact:** `/tools/plugin_hooks.py`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [ ]  
    - **PR/Issue:** #  
- [ ] Implement validation report artifact (e.g., `validation_report.json`) for each node  
    - **Priority:** Recommended for M2  
    - **DoD:** Report generated for all nodes, reviewed by CAIA  
    - **Artifact:** `/reports/validation_report.json`  
    - **Reviewer(s):** CAIA  
    - **Status:** [ ]  
    - **PR/Issue:** #  
- [ ] Add historical compliance tracking (weekly trend)  
    - **Priority:** Stretch goal  
    - **DoD:** Tracking system live, reviewed by Infra lead  
    - **Artifact:** `/docs/compliance_history.md`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [ ]  
    - **PR/Issue:** #  
- [ ] Add optional metadata signing for `.onex` files  
    - **Priority:** Stretch goal  
    - **DoD:** Signing logic implemented, reviewed by Foundation team  
    - **Artifact:** `/tools/onex_signer.py`  
    - **Reviewer(s):** Foundation team  
    - **Status:** [ ]  
    - **PR/Issue:** #  

---

> Once all items are checked, Milestone 1 is complete and the project may proceed to Milestone 2: Runtime Loader and Executable Scaffold Node.

> ⚠️ Reminder: The core functional outcome of M2 is a scaffold node that builds other nodes using these M1-defined protocols. This is the heart of the ONEX MVP and should inform your implementation here.

---

*Note: Consider automating checklist status tracking and metrics reporting via project management tools or CI integration.*