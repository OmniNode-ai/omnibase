<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: milestone_1_checklist.md -->
<!-- version: 1.0.0 -->
<!-- uuid: c75debe0-1263-488b-8af8-53a900ffa84b -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.159283 -->
<!-- last_modified_at: 2025-05-21T16:42:46.056683 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: deeb2b1d99f954975afdbec99b6523ac6fd4756f8030c62098aec5ceef8e6a27 -->
<!-- entrypoint: {'type': 'python', 'target': 'milestone_1_checklist.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.milestone_1_checklist -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

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

-### Schema & Protocol Definition
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
- [x] Write Node Author Quickstart guide (README)  
    - **DoD:** Guide published, tested by new contributor, reviewed by Foundation team  
    - **Artifact:** `/docs/quickstart.md`  
    - **Reviewer(s):** Foundation team  
    - **Status:** [x]  
    - [x] Usage example in docs  
    - [x] Quickstart tested by new contributor  
    - **Note:** [2024-06-09] Full audit completed: guide, usage example, and checklist are present and committed. See `docs/quickstart.md` for details.
- [x] Build metadata stamper and `.onex` validator CLI tool  
    - **DoD:** Tool validates `.onex` files, integrated in CI, reviewed by Infra lead  
    - **Artifact:** `/tools/onex_validator.py`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [x]  
    - **PR/Issue:** #  
    - [x] Unit/integration tests written and passing  
    - [x] Usage example in docs  
    - **Note:** [2024-06-09] CLI validator and stamper implemented as separate tools, with canonical result models (`OnexResultModel`, `OnexMessageModel`). All code, tests, and docs updated for protocol and naming alignment. Model rename from `UnifiedMessageModel` to `OnexMessageModel` completed and verified.
- [x] Implement structured .onexignore support (YAML, multi-tool)
    - [x] Create Pydantic model for .onexignore (model_onex_ignore.py)
    - [x] Implement loader and validator for .onexignore in stamper tool
    - [x] Update stamper tool to respect .onexignore (tool-specific and global patterns)
    - [x] Fallback to .stamperignore if .onexignore is missing
    - [x] Update documentation with canonical .onexignore examples and migration guidance
        - See new section 'Ignore File Stamping and Ingestion Protocol' in docs/registry.md
    - [x] Usage example in docs
        - See canonical before/after and CLI example in docs/registry.md
    - [x] Add/expand tests for .onexignore (YAML, tool-specific, global, invalid cases)
- [x] Enhance metadata stamper tool for recursive directory traversal and CI/pre-commit integration  
    - [x] Confirm ProtocolDirectoryTraverser protocol is fully implemented and documented
    - [x] Confirm model_enum_ignore_pattern_source.py and other enums are fully used (no string literals remain)
    - [x] Confirm model_file_filter.py is used for structured filtering configuration
    - [x] Confirm DirectoryTraverser class is fully generic and documented
    - [x] Confirm CLIStamper is refactored to use the directory traverser
    - [x] Confirm error reporting is robust for unsupported/malformed files
    - [x] Confirm CI/pre-commit hook integration blocks or auto-fixes unstamped files
    - [x] Confirm tests are updated for new modular structure
    - [x] Confirm comprehensive usage examples and documentation are present
    
### Node Creation Foundation
- [ ] Define canonical node layout and runtime directory structure  
    - **DoD:** `src/omnibase/nodes/` established with scaffold template, tests moved to `tests/nodes/`  
    - **Artifact:** `/src/omnibase/nodes/`, `/tests/nodes/`  
    - **Reviewer(s):** CAIA, Infra lead  
    - **Status:** [ ]  
    - [ ] Node folders follow `name_type/` format (e.g. `stamper_node/`)  
    - [ ] Each node contains `node.py`, `state_contract.yaml`, `.onex` metadata  
    - [ ] Usage of this structure documented in `docs/nodes/structural_conventions.md`  
    

#### Stamper Node Migration and Canonicalization

1. **Directory and Metadata Setup**
    - [x] Create `src/omnibase/nodes/stamper_node/` directory with canonical structure
    - [x] Add `node.onex.yaml` with all required metadata fields for stamper node
    - [ ] Add `stamper_node_contract.yaml` defining the state contract
    - [ ] Validate `node.onex.yaml` and state contract against canonical schemas
    - [ ] Confirm `node.onex.yaml` is explicitly ignored by the stamper via `.onexignore`
    - [ ] Validate that the file is treated as a full metadata block and not stamped again
    - [ ] Add comment or flag in metadata to indicate the file is "self-describing" and exempt from stamping

2. **Source Code and Logic Migration**
    - [x] Add `src/main.py` implementing the stamper node logic per contract
    - [x] Add `src/helpers/` directory (can be empty or stub)
    - [x] Move and refactor `stamper_engine.py` logic into `stamper_node/src/main.py` (or submodules)
    - [x] Move or adapt all relevant handler registration and utility logic
    - [x] Reference or import all required constants and models

3. **Tests and Fixtures**
    - [x] Add `tests/test_main.py` with unit tests for stamper node
    - [x] Add `tests/fixtures/` directory (can be empty or stub)
    - [x] Move or duplicate all stamper-related tests into `tests/nodes/stamper_node/`
    - [x] Stamp all test fixtures and validate via schema/CI
    - [x] Add minimal end-to-end test: stamp → emit event → validate `.onex` output
    - [x] Add test coverage or manual validation to ensure hash is not broken by stamper for full-metadata files

4. **Tree, Registry, and Runtime Integration**
    - [ ] Ensure node is referenced in `.tree` (if required by discovery mechanism)
    - [ ] Add node to `.tree` file with correct path and metadata reference
    - [ ] Register node in `registry.yaml` or other applicable index if registry integration is enabled

5. **Documentation and Developer Support**
    - [ ] Add `README.md` with node documentation and usage
    - [ ] Update or move documentation from `docs/tools/stamper.md` into `stamper_node/README.md`
    - [ ] Ensure `README.md` includes schema references and usage example for both CLI and programmatic execution

6. **CLI & Event Runtime Integration**
    - [ ] Refactor CLI entrypoint to invoke the new node, or provide a wrapper
    - [ ] Validate runtime execution via CLI with `onex run stamper_node` (even if stubbed)
    - [ ] Emit `NODE_START`, `NODE_SUCCESS`, and `NODE_FAILURE` events using `EventBusProtocol`
    - [ ] Include debug logging and error reporting consistent with core observability guidelines

7. **Cleanup and Finalization**
    - [ ] Pass all CI, lint, and schema validation checks for the new node
    - [ ] Remove or deprecate old stamper files after migration is validated

#### Fixture Strategy and Layout
- [ ] Adopt hybrid fixture structure (central shared + node-local)
    - Central: `tests/fixtures/`, `tests/conftest.py` for shared protocol/model fixtures
    - Node-local: `src/omnibase/nodes/<node>/tests/fixtures/` for custom or node-specific cases
    - [ ] Document this structure in `docs/testing/fixtures_guidelines.md`
    - **Rationale:** Supports both encapsulation and reusability across nodes while enabling scalable test design.

- [ ] Stamp all fixture files and test data with canonical `.onex` metadata
    - [ ] Apply stamper to YAML/JSON in `tests/fixtures/` and `tests/data/`
    - [ ] Apply stamper to YAML/JSON in all node-local fixture and `data/` folders
    - [ ] Add schema validation to CI for all stamped fixtures and test data
    - [ ] Confirm hash/idempotency checks for fixture inputs
    - **Rationale:** Enables reproducibility, version tracking, and compatibility with state contracts. Ensures fixture provenance and enables regeneration of nodes with full context.

- [ ] Validate that node-local fixture directories are ignored or scoped to local test runs
    - [ ] Avoid importing node-local test helpers outside of node scope

- [ ] Support YAML/JSON test data in `tests/data/` or `tests/fixtures/<node>/data/`
    - [ ] Ensure each has associated `.onex` metadata and schema validation

- [ ] Implement or stub a `FixtureLoaderProtocol` in `protocol/` to support fixture discovery
    - [ ] Register support for central and node-scoped fixture directories
    - [ ] Include fixture filtering/loading logic for CLI/CI runners

- [ ] Ensure `tests/schema/testdata/` remains canonical for contract schema examples

- [ ] Define optional `.tree` structure or registry loader for fixture discovery (M2 prep)

- [ ] Update existing test discovery logic to accommodate both shared and node-local fixtures

- [ ] Add CI task to flag orphaned fixtures and unused data files
    - [ ] Auto-report unreferenced YAML/JSON files
    - **Rationale:** Prevent drift and bloat from accumulating unused test assets.

### Protocols & Models (Shared Core)
- [ ] Ensure all protocols are defined in `src/omnibase/protocol/` and are not duplicated in node directories
- [ ] Ensure all models/enums are defined in `src/omnibase/model/` and are not duplicated in node directories
- [ ] Update documentation to clarify the separation and reference pattern for protocols and models
- [ ] Add/expand tests for protocol/model contract compliance in `tests/protocol/` and `tests/model/`
- [ ] Refactor any node, tool, or CLI code to import protocols/models from the shared location
- [ ] Review and document versioning and changelog policies for protocols and models

### Protocol & Interface Remediation for Standards Compliance
- [x] Refactor FileTypeHandlerRegistry as a Protocol (node-local or runtime/ if reused)
    - [x] Define ProtocolFileTypeHandlerRegistry in `runtime/protocol/` if used by multiple nodes, else node-local
    - [x] Ensure all handler registration and lookup methods are typed and documented
    - [x] Update all usages to depend on the protocol, not a concrete class
    - [x] Add/expand tests for protocol conformance
- [x] Refactor SchemaExclusionRegistry as a Protocol or ABC (runtime/ if reused)
    - [x] Define ProtocolSchemaExclusionRegistry in `runtime/protocol/` if used by multiple nodes, else node-local
    - [x] Ensure all exclusion logic is typed and documented
    - [x] Update all usages to depend on the protocol, not a concrete class
    - [x] Add/expand tests for protocol conformance
- [x] Refactor DirectoryTraverser as a Protocol (runtime/ if reused)
    - [x] Define ProtocolDirectoryTraverser in `runtime/protocol/` if used by multiple nodes, else node-local
    - [x] Ensure all traversal and processor signatures are strongly typed
    - [x] Update all usages to depend on the protocol, not a concrete class
    - [x] Add/expand tests for protocol conformance
- [x] Refactor hash utilities to use canonical Enum and Protocol
    - [x] Define ProtocolCanonicalHash in `runtime/protocol/` if reused, else node-local
    - [x] Ensure all field references use canonical Enum (NodeMetadataField)
    - [x] Use canonical serializer for all hash computation
    - [x] Add/expand tests for protocol-compliant hash computation
- [x] Add/expand docstrings and metadata for all new/refactored protocols
    - [x] Reference the canonical rule for runtime/ vs node-local protocol placement
    - [x] Document rationale for each protocol's location and interface type

### Runtime Directory Refactor for Shared Execution Logic
- [x] Create `src/omnibase/runtime/` with subdirectories: `filesystem/`, `io/`, `crypto/`
- [x] Move `directory_traverser.py` to `runtime/filesystem/` (rename to `explorer.py` if refactored)
- [x] Move `in_memory_file_io.py` to `runtime/io/`
- [x] Move `hash_utils.py` to `runtime/crypto/`
- [x] Update all imports in nodes and tools to reference the new runtime locations
- [x] Remove any duplicate or node-local copies of these utilities
- [x] Document the runtime/ structure and rationale in developer and node documentation
- [x] (Optional) Reflect runtime/ structure in `.tree` for CI/discovery

### Runtime & Event Execution Layer
- [x] Implement `OnexEvent` model (standard event format)  
    - **DoD:** UUID, timestamp, node ID, type, metadata  
    - **Artifact:** `onex/core/models/onex_event.py`  
    - **Reviewer(s):** Runtime owner  
    - **Status:** [x]  
- [x] Implement `EventBusProtocol` and in-memory event bus  
    - **DoD:** `publish()` and `subscribe()` defined, with tests  
    - **Artifact:** `onex/core/events/event_bus.py`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [x]  
- [x] Implement `NodeRunner` (executes node with event emissions)  
    - **DoD:** Handles success/failure events, integrates with EventBus  
    - **Artifact:** `onex/runtime/node_runner.py`  
    - **Reviewer(s):** Runtime owner  
    - **Status:** [x]  
- [x] Implement `MessageBusAdapter` for event forwarding (stub)  
    - **DoD:** Adapter implements `EventBusProtocol`, routes to MessageBusProtocol  
    - **Artifact:** `onex/events/adapters/messagebus_event_adapter.py`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [x]  
- [x] Add `PostgresEventStore` for event durability  
    - **DoD:** All events and DLQ failures persisted to Postgres container  
    - **Artifact:** `onex/store/event_store_postgres.py`, `schema/onex_events.sql`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [x]  
- [x] Emit events from canary node execution (e.g., StamperNode)  
    - **DoD:** Execution of nodes emits `NODE_START`, `NODE_SUCCESS`, or `NODE_FAILURE`  
    - **Artifact:** `nodes/stamper/stamper_node.py`  
    - **Reviewer(s):** Foundation team  
    - **Status:** [x]  
- [x] Create CLI command: `onex run <node>`  
    - **DoD:** CLI executes node, outputs result, emits events, writes to ledger  
    - **Artifact:** `onex/cli/commands/run_node.py`  
    - **Reviewer(s):** Foundation team  
    - **Status:** [x]  
## Canary Node & CLI Alignment: Advanced Implementation Checklist

### Node Creation Foundation / Runtime & Event Execution Layer
- [ ] **Telemetry Decorator:** Implement and apply a telemetry decorator to all node entrypoints.
    - **DoD:** Decorator standardizes logging context, timing, event emission, and error handling.
    - **Artifact:** `src/omnibase/nodes/stamper_node/telemetry.py`, applied in `main.py`.
- [ ] **Correlation/Request ID Propagation:** Add and propagate correlation/request IDs in all state models and ONEX events.
    - **DoD:** ID generated at CLI layer if not provided, present in all logs/events.
    - **Artifact:** `StamperInputState`, `StamperOutputState`, event models.
- [ ] **Telemetry/Log Subscriber Utility:** Implement a utility to subscribe to telemetry decorator events/logs and print/process them in real time.
    - **DoD:** Utility subscribes to event bus or log stream, prints or processes logs for local/CI use.
    - **Artifact:** `src/omnibase/nodes/stamper_node/telemetry_subscriber.py` (or runtime/events/).
    - **Docs:** Usage documented in developer guide and CI instructions.
- [ ] **ONEX Event Schema Standardization:** Define and document the canonical ONEX event schema.
    - **DoD:** Schema documented in `docs/protocol/onex_event_schema.md`, all emitters conform.
    - **Artifact:** Event emitter modules, schema doc.
- [ ] **Event Emission Tests:** Add tests to validate event emission and telemetry subscriber output.
    - **DoD:** Tests in `tests/nodes/stamper_node/` or `tests/runtime/events/`.

### Tooling & Automation / CI & Enforcement
- [ ] **Schema Versioning:** Embed version fields in all state models and maintain a schema changelog (`CHANGELOG.stamper.md`).
    - **DoD:** Version field present, changelog updated on every schema change.
    - **Artifact:** State models, `CHANGELOG.stamper.md`.
- [ ] **JSON Schema Commit & Validation:** Commit and validate JSON schemas for all state models.
    - **DoD:** Schemas in `schemas/`, validated in CI.
    - **Artifact:** `schemas/stamper_input.schema.json`, `schemas/stamper_output.schema.json`.
- [ ] **Schema Drift Detection:** Add schema drift detection: fail CI if model schema changes without version bump/changelog update.
    - **DoD:** CI test in `tests/schema/` or `.github/workflows/ci.yml`.
- [ ] **CLI/Node Output Parity Harness:** Add a test harness to verify CLI and direct node invocations produce identical output.
    - **DoD:** Test module (e.g., `test_canary_equivalence.py`) in `tests/nodes/stamper_node/`.
- [ ] **Error Code to Exit Code Mapping:** Map error codes to CLI exit codes and enforce in CLI adapters.
    - **DoD:** Mapping in shared module, CLI uses correct exit codes.
    - **Artifact:** `src/omnibase/nodes/stamper_node/error_codes.py`, CLI adapter.
- [ ] **Centralized Error Code Definitions:** Centralize error code definitions in a shared module and enforce usage.
    - **DoD:** All error handling uses defined codes, linter/CI check present.
    - **Artifact:** `error_codes.py`, linter/CI config.
- [ ] **Sensitive Field Redaction:** Mark and redact sensitive fields in all logs/events; add tests for redaction.
    - **DoD:** Redaction logic in `.model_dump()` or `redact()` method, tested in `tests/nodes/stamper_node/`.
- [ ] **Plugin Discovery:** Implement and document plugin discovery (entry points, registry, env).
    - **DoD:** Plugins can be loaded via all three mechanisms, documented in developer guide.
    - **Artifact:** Plugin loader module, `plugin_registry.yaml`, `pyproject.toml`/`setup.cfg`.
- [ ] **Structured Logging & Centralized Config:** Ensure all logging is structured and context-bound; centralize config for logging, plugins, and event sinks; support env var overrides.
    - **DoD:** Logging and config modules, config file, env var support.
    - **Artifact:** `logging_config.py`, `config.yaml`, developer docs.

### Documentation & Developer Support
- [ ] **Update Documentation:** Update `README.md` and developer docs to cover all new requirements, including telemetry, event schema, plugin loading, error code mapping, redaction, and correlation/tracing.
    - **DoD:** Docs updated, usage and rationale for each new feature explained.
    - **Artifact:** `README.md`, `docs/nodes/canary_node_cli_alignment.md`, developer guides.

### CI & Enforcement
- [ ] Build CLI tool for automated `.tree` generation and validation  
    - **DoD:** Tool generates/validates `.tree`, integrated in CI, reviewed by CAIA  
    - **Artifact:** `/tools/tree_generator.py`  
    - **Reviewer(s):** CAIA  
    - **Status:** [ ]  
    - **PR/Issue:** #  
    - [ ] Unit/integration tests written and passing  
    - [ ] Usage example in docs  
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
    - **Note:** [2024-06-09] All schema_ref standardization, model/test alignment, and pre-commit hooks (yamllint, mypy, etc.) are passing. Manual line wrapping for canonical schema YAML is in progress for full yamllint compliance.

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

- [ ] Propose reorganization: move all runnable nodes into `src/omnibase/nodes/`  
    - **Priority:** High  
    - **DoD:** Folder exists, current prototype nodes moved, documented  
    - **Artifact:** `src/omnibase/nodes/`, `docs/nodes/index.md`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [ ]  

---

> Once all items are checked, Milestone 1 is complete and the project may proceed to Milestone 2: Runtime Loader and Executable Scaffold Node.
> ⚠️ Reminder: The core functional outcome of M2 is a scaffold node that builds other nodes using these M1-defined protocols. This is the heart of the ONEX MVP and should inform your implementation here.

---

*Note: Consider automating checklist status tracking and metrics reporting via project management tools or CI integration.*

---

*Each item above should be tracked as a distinct, testable checklist entry with a clear Definition of Done (DoD) and artifact location. This ensures all advanced requirements from the Canary Node & CLI Alignment document are implemented, enforced, and documented for Milestone 1 and beyond.*

