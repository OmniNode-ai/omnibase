<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: milestone_1_checklist.md
version: 1.0.0
uuid: aaebac59-42c4-473c-b722-59a99aa98b52
author: OmniNode Team
created_at: 2025-05-22T05:34:29.778060
last_modified_at: 2025-05-22T21:19:13.544067
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 6b6c69629a7354af7f0abaa1535b23817e691a147cb9ed8326a3f3bbffd69e13
entrypoint: python@milestone_1_checklist.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.milestone_1_checklist
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Milestone 1 Implementation Checklist: ONEX Node Protocol, Schema, Metadata, and CI Enforcement

> **Status:** Canonical
> **Last Updated:** 2025-05-16
> **Purpose:** This checklist enumerates all implementation steps required to complete Milestone 1 of the ONEX Execution Architecture. Each item is actionable, testable, and maps directly to the deliverables in [onex_execution_architecture.md](./onex_execution_architecture.md).

## Implementation Flow Overview

The Milestone 1 implementation bootstraps the ONEX system by defining the schemas, metadata contracts, and validation tooling that power future milestones. The high-level flow is:

1. Define `.onex` metadata schema (describes a node)  
2. Define `.onextree` file format (indexes node locations in directory)  
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
    Defines the metadata block for each node; referenced by `.onextree`
    - **DoD:** Schema file merged to main, referenced in docs, reviewed by Infra lead  
    - **Artifact:** `/schemas/onex_node.yaml`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [x] (YAML schema, Pydantic model, and extractor utility are now fully aligned and implemented. All field names, types, and constraints are enforced per the canonical schema.)  
    - **PR/Issue:** #  
    - [x] Unit/integration tests written and passing  
    - [x] Usage example in docs  
- [x] Define canonical `.onextree` directory structure format for node discovery (with explicit required fields)  
    Defines the discoverable directory structure; references `.onex` files for each node  
    - **DoD:** Format documented, sample `.onextree` file in repo, reviewed by CAIA  
    - **Artifact:** `/schemas/tree_format.yaml`  
    - **Reviewer(s):** CAIA  
    - **Status:** [x]  
    - **PR/Issue:** #  
    - [x] Unit/integration tests written and passing  
    - [x] Usage example in docs  
- [x] Add dual-format support for .onextree files (YAML and JSON)  
    - **DoD:** Both .onextree (YAML) and .onextree.json (JSON) formats are supported, validated, and documented  
    - **Artifact:** `/schemas/tree_format.yaml`, `/schemas/tree_format.json`, example .onextree.json file in repo  
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
- [x] Validate `node.onex.yaml` and state contract against canonical schemas
    - [x] Run schema validation in CI and confirm both files pass
    - [x] Add explicit test or CI check for this validation

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
- [x] Node folders follow `name_type/` format (e.g. `stamper_node/`)
- [x] Each node contains `node.py`, `state_contract.yaml`, `.onex` metadata
- [x] Usage of this structure documented in `docs/nodes/structural_conventions.md`

#### Stamper Node Migration and Canonicalization

1. **Directory and Metadata Setup**
    - [x] Create `src/omnibase/nodes/stamper_node/` directory with canonical structure
    - [x] Add `node.onex.yaml` with all required metadata fields for stamper node
    - [x] Add comment or flag in metadata to indicate the file is "self-describing" and exempt from stamping
    - [x] Add `stamper_node_contract.yaml` defining the state contract
    - [x] Validate `node.onex.yaml` and state contract against canonical schemas
        - [x] Run schema validation in CI and confirm both files pass
        - [x] Add explicit test or CI check for this validation
    - [x] Confirm `node.onex.yaml` is explicitly ignored by the stamper via `.onexignore`
    - [x] Validate that the file is treated as a full metadata block and not stamped again
        - [x] Add or confirm test that ensures `.onexignore` is respected at runtime
        - [x] Add or confirm test that ensures no double-stamping occurs

2. **Source Code and Logic Migration**
    - [x] Add `src/main.py` implementing the stamper node logic per contract (stub present)
    - [x] Add `src/helpers/` directory (can be empty or stub)
    - [x] Move and refactor `stamper_engine.py` logic into `stamper_node/helpers/stamper_engine.py` (or submodules)
        - [x] Implement `StamperEngine.stamp_file` and `process_directory` methods (now in helpers/stamper_engine.py)
        - [x] Migrate real stamping logic from legacy code
        - [x] Add/expand tests for new logic
    - [x] Move or adapt all relevant handler registration and utility logic
        - [x] Audit `helpers/handlers/` and ensure all required logic is present and imported
        - [x] Remove any unused or stub code (from main.py)
    - [x] Reference or import all required constants and models
    - [x] Refactor main.py to use canonical engine and keep node root clean

3. **Tests and Fixtures**
    - [x] Add `tests/test_main.py` with unit tests for stamper node
    - [x] Add `tests/fixtures/` directory (currently empty)
    - [x] Move or duplicate all stamper-related tests into `tests/nodes/stamper_node/` (currently under node-local path)
        - [x] Update imports and paths in the moved test file to reference the canonical helpers/stamper_engine.py location
    - [x] Stamp all test fixtures and validate via schema/CI
        - [x] Add actual fixture files to `fixtures/` (none present)
        - [x] Stamp fixtures with `.onex` metadata
        - [x] Add/expand schema validation for fixtures in CI
    - [x] Add minimal end-to-end test: stamp → emit event → validate `.onex` output (present in `test_main.py`)
    - [x] Add test coverage or manual validation to ensure hash is not broken by stamper for full-metadata files
        - [x] Add explicit test for idempotency/hash preservation

4. **Documentation and Developer Support**
    - [x] Add `README.md` with node documentation and usage
    - [x] Update or move documentation from `docs/tools/stamper.md` into `stamper_node/README.md`
        - [x] Audit for missing content and migrate as needed
    - [x] Ensure `README.md` includes schema references and usage example for both CLI and programmatic execution
        - [x] Add CLI usage example
        - [x] Add programmatic usage example

5. **CLI & Event Runtime Integration**
    - [x] Refactor CLI entrypoint to invoke the new node, or provide a wrapper (stub present)
    - [x] Validate runtime execution via CLI with `onex run stamper_node` (even if stubbed)
        - [x] Add/expand test or manual validation for CLI invocation
    - [x] Emit `NODE_START`, `NODE_SUCCESS`, and `NODE_FAILURE` events using `EventBusProtocol`
    - [x] Include debug logging and error reporting consistent with core observability guidelines
        - [x] Audit logging for observability compliance
        - [x] Add/expand tests for error reporting

5.5 **Directory Restructuring and Registry/Tree Structure Alignment**
    - [ ] Restructure node directories to match the canonical, versioned layout
        - [ ] Move all nodes to `nodes/<node_name>/<version>/` structure
        - [ ] Ensure all adapters, contracts, models, helpers, tests, and fixtures are versioned and placed under the correct node version directory
        - [ ] Remove or migrate any legacy or non-versioned node directories
        - [ ] Add `.wip` marker or `node.onex.yaml` to all version directories as appropriate
        - [ ] Update all references, imports, and documentation to match the new structure
    - [ ] Registry and .onextree Alignment
        - [ ] Generate or update `.onextree` manifest to reflect the new directory structure
        - [ ] Ensure all nodes, adapters, contracts, runtimes, CLI tools, and packages are represented in `.onextree` with correct versioning
        - [ ] Add/expand tests to validate `.onextree` against actual directory contents
        - [ ] Update CI to enforce `.onextree` and directory structure compliance
    - [ ] Registry Metadata and Loader Updates
        - [ ] Ensure all artifact metadata files (`node.onex.yaml`, `cli_adapter.yaml`, `contract.yaml`, etc.) are present and correct in each versioned directory
        - [ ] Update loader logic and documentation to clarify `.onextree` usage, `.wip` marker, and metadata file conventions
        - [ ] Add/expand tests for loader/registry behavior with new structure
    - [ ] Documentation
        - [ ] Update all relevant documentation to reference the new structure, `.onextree` format, and registry-centric conventions
        - [ ] Add migration notes and before/after examples for maintainers
    - [ ] Registry-Centric Artifact Versioning
        - [ ] Ensure all artifacts (nodes, adapters, contracts, runtimes, CLI tools, packages) are versioned in their own subdirectories
        - [ ] Add/expand registry index files (`registry.yaml`, `adapters.yaml`, etc.) to track all versions
        - [ ] Add/expand compatibility metadata (semantic version ranges) in all artifact metadata files
    - [ ] .onextree/Registry Validation Tooling
        - [ ] Build or update CLI tool for `.onextree` generation/validation (if not already done)
        - [ ] Integrate tool into CI and pre-commit hooks
    - [ ] Loader/Registry Documentation
        - [ ] Ensure all loader/registry logic is documented in `docs/registry_architecture.md` and cross-linked from other docs

6. **Cleanup and Finalization**
    - [ ] Pass all CI, lint, and schema validation checks for the new node
        - [ ] Confirm all checks pass in CI
    - [ ] Remove or deprecate old stamper files after migration is validated
        - [ ] Audit repo for legacy files and remove/deprecate as needed

#### Fixture Strategy and Layout
- [x] Adopt hybrid fixture structure (central shared + node-local)
    - [x] Document this structure in `docs/testing/fixtures_guidelines.md`
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

- [ ] Define optional `.onextree` structure or registry loader for fixture discovery (M2 prep)

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

- [ ] [NEW: 2025-05-21] Canonicalize handler and registry logic in core/runtime
    - All official handlers and the file type handler registry are defined and maintained in `omnibase.runtime.handlers` and `omnibase.core.core_file_type_handler_registry`.
    - Node-local handler/registry logic is removed or migrated.
    - All node/CLI imports reference only canonical modules.
    - **Artifact:** `/src/omnibase/runtime/handlers/`, `/src/omnibase/core/core_file_type_handler_registry.py`
    - **DoD:** No node-local handler/registry logic remains; all tests pass.
    - **Reviewer(s):** Infra lead, CAIA

- [ ] [NEW: 2025-05-21] Implement plugin/override API for node-local handler extensions
    - Expose a minimal, versioned `register_handler(name, HandlerClass)` API.
    - Document plugin/override mechanism in code and developer docs.
    - Provide canonical example in node entrypoint/helpers.
    - **Artifact:** `/src/omnibase/runtime/handlers/`, `/docs/nodes/structural_conventions.md`
    - **DoD:** Node-local handler registration works and is documented.
    - **Reviewer(s):** Infra lead, CAIA

- [ ] [NEW: 2025-05-21] Handler/plugin metadata and introspection
    - Require all handlers/plugins to declare metadata (supported file types, version, author, etc.).
    - Enforce via code review and CI.
    - **Artifact:** `/src/omnibase/runtime/handlers/`
    - **DoD:** All handlers/plugins have metadata; CI enforces.
    - **Reviewer(s):** Infra lead, CAIA

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
- [x] (Optional) Reflect runtime/ structure in `.onextree` for CI/discovery

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
- [ ] Build CLI tool for automated `.onextree` generation and validation  
    - **DoD:** Tool generates/validates `.onextree`, integrated in CI, reviewed by CAIA  
    - **Artifact:** `/tools/tree_generator.py`  
    - **Reviewer(s):** CAIA  
    - **Status:** [ ]  
    - **PR/Issue:** #  
    - [ ] Unit/integration tests written and passing  
    - [ ] Usage example in docs  
4. **Tree, Registry, and Runtime Integration**
    - [ ] Ensure node is referenced in `.onextree` (if required by discovery mechanism)
    - [ ] Add node to `.onextree` file with correct path and metadata reference
    - [ ] Register node in `registry.yaml` or other applicable index if registry integration is enabled
- [ ] Integrate CI enforcement: all nodes must pass schema validation for metadata, execution result, and state contract  
    - **DoD:** CI blocks non-compliant commits, reviewed by Infra lead  
    - **Artifact:** `.github/workflows/ci.yml`  
    - **Reviewer(s):** Infra lead  
    - **Status:** [ ]  
    - **PR/Issue:** #  
    - [ ] CI test coverage for all enforcement logic  
- [ ] Integrate CI enforcement: `.onextree` file must match directory contents and reference valid `.onex` files  
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
- [ ] Add pre-commit hooks for schema validation and `.onextree` sync  
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

- [ ] [NEW: 2025-05-21] Flatten and document node helper structure
    - Move all node-local helpers to a single `helpers/` directory at node root.
    - Document guidelines for subdirectories within helpers.
    - Audit all nodes for compliance.
    - **Artifact:** `/src/omnibase/nodes/<node>/helpers/`
    - **DoD:** Only node-specific logic remains in helpers.
    - **Reviewer(s):** CAIA, Infra lead

- [ ] [NEW: 2025-05-21] Provide node bootstrap/scaffold utility
    - Implement/maintain CLI tool to generate standardized node skeletons.
    - **Artifact:** `/scripts/omnibase-cli`, `/docs/quickstart.md`
    - **DoD:** New nodes can be scaffolded with best-practice structure.
    - **Reviewer(s):** CAIA, Foundation team

- [ ] [NEW: 2025-05-21] Enforce handler/registry import and plugin usage via linting/CI
    - Add/update CI rules to block disallowed imports and enforce plugin API usage.
    - Document linting/CI rules.
    - **Artifact:** `.github/workflows/`, `/docs/`
    - **DoD:** CI blocks non-compliant imports or plugin usage.
    - **Reviewer(s):** Infra lead

- [ ] [NEW: 2025-05-21] Document and version handler/registry API
    - Publish Handler/Registry API doc and CHANGELOG.
    - Tag releases with semver.
    - Provide migration guides.
    - **Artifact:** `/docs/handlers_registry_api.md`, `/CHANGELOG.md`
    - **DoD:** Docs and changelog published; migration guide available.
    - **Reviewer(s):** Infra lead, CAIA


- [ ] [NEW: 2025-05-21] Governance and review process for plugins
    - Define review process for new plugins/handlers.
    - Add PR template checklist or architectural review step.
    - **Artifact:** `.github/PULL_REQUEST_TEMPLATE.md`
    - **DoD:** All plugin/handler PRs follow review process.
    - **Reviewer(s):** CAIA, Infra lead

    - [ ] Define plugin discovery entry-point patterns (e.g., setuptools `entry_points`) and document in developer guide  
        - **Artifact:** `/docs/plugins/entry_points.md`  
        - **DoD:** Developers can load handlers via entry-points; example documented.  
        - **Reviewer(s):** CAIA, Infra lead  

    - [ ] Establish plugin priority and conflict-resolution rules  
        - **Artifact:** `/docs/plugins/conflict_resolution.md`  
        - **DoD:** Core vs node-local handlers have defined load order; documented and enforced.  
        - **Reviewer(s):** Infra lead  

    - [ ] Add CLI command to list all registered handlers and plugins  
        - **Artifact:** `onex/cli/commands/list_handlers.py`  
        - **DoD:** `onex handlers list` outputs handler name, source (core/plugin), and version.  
        - **Reviewer(s):** Foundation team  

    - [ ] Write tests for plugin override resolution order and failure cases  
        - **Artifact:** `tests/runtime/test_plugin_resolution.py`  
        - **DoD:** Unit tests cover core-only, plugin-only, and override scenarios.  
        - **Reviewer(s):** Infra lead, CAIA  

---

> Once all items are checked, Milestone 1 is complete and the project may proceed to Milestone 2: Runtime Loader and Executable Scaffold Node.
> ⚠️ Reminder: The core functional outcome of M2 is a scaffold node that builds other nodes using these M1-defined protocols. This is the heart of the ONEX MVP and should inform your implementation here.

---

*Note: Consider automating checklist status tracking and metrics reporting via project management tools or CI integration.*

---

*Each item above should be tracked as a distinct, testable checklist entry with a clear Definition of Done (DoD) and artifact location. This ensures all advanced requirements from the Canary Node & CLI Alignment document are implemented, enforced, and documented for Milestone 1 and beyond.*

### Stamper Node Refactor and Hygiene (2025-06-10)
- [x] Move node-local state models to a `models/` directory in the node source
- [x] Remove commented stub imports from `main.py`
- [x] Enforce runtime version injection for state models (no hardcoded version)

- [ ] **Handler/Fixture/Integration Test Separation and Coverage**
    - [ ] All test cases (node-local, handler, integration, fixture) must be generated or injected via protocol-driven registries or handler serialization methods.
        - No hand-written or hardcoded metadata blocks, UUIDs, timestamps, or domain fields.
        - All dynamic values must be provided by fixtures, mocks, or protocol registries.
        - All test data must be round-trip safe and idempotent with the handler logic.
        - **DoD:** All test data is handler-generated or registry-injected; no hardcoded domain values remain.
        - **Rationale:** Ensures test/production parity, maintainability, and extensibility.
    - [ ] Assertions must be model-based or handler-driven, never string-based for domain fields.
        - Assert on model structure, field presence, or handler output, not on literal strings.
        - For idempotency, always compare handler output to itself, not to a static string.
        - **DoD:** No string-based assertions for domain fields; all assertions are model- or handler-based.
        - **Rationale:** Prevents test fragility and drift from canonical logic.
    - [ ] All test parameterization must use protocol-driven registries or fixtures.
        - No ad-hoc or in-test parameter lists for domain cases.
        - All test cases must be injectable and extensible for future plugin/handler scenarios.
        - **DoD:** All test parameterization is registry- or fixture-driven; no ad-hoc lists remain.
        - **Rationale:** Enables extensibility and plugin support.
    - [ ] All test files must be reviewed for:
        - No hardcoded domain values.
        - No string-based assertions for domain fields.
        - No parallel or ad-hoc logic for metadata block construction or parsing.
        - Full round-trip and idempotency coverage using handler logic.
        - **DoD:** All test files pass review for these criteria; deviations are flagged and remediated.
        - **Rationale:** Ensures long-term maintainability and standards compliance.
    - [ ] All test reviews must explicitly check for:
        - Protocol/handler-driven test case construction.
        - Model-based assertions.
        - Registry-injectable test cases.
        - No drift from production handler logic.
        - **DoD:** All reviews document compliance with these checks.
        - **Rationale:** Prevents regression and enforces standards.
    - [ ] Refactor node-local tests to use only in-memory, protocol-driven, handler-rendered test cases (no file-based fixtures for canonical/positive cases)
    - [ ] Add/expand handler-level tests in `tests/handlers/` to cover:
        - [ ] File-based fixture parsing (YAML, Markdown, Python, etc.)
        - [ ] Edge cases and malformed files
        - [ ] Delimiter/comment handling and legacy file support
    - [ ] Add/expand integration tests in `tests/tools/` or `tests/fixtures/` to cover:
        - [ ] CLI and disk-backed stamping flows
        - [ ] End-to-end stamping and validation with real files
        - [ ] Negative/malformed file scenarios
    - [ ] Ensure all handler/fixture/integration tests are separated from node-local protocol tests
    - [ ] Document the separation and rationale in `docs/testing/node_testing_guidelines.md` and `docs/testing/fixtures_guidelines.md`

### Test Canonicalization and Protocol-Driven Refactor (2025-06-11)
- [ ] **Protocol-Driven File I/O in Tests**
    - [ ] Audit all test files for direct use of `open`, `Path`, `write_text`, `yaml.safe_load`, `json.load`, and similar.
    - [ ] Refactor all file I/O in tests to use protocol-driven adapters (e.g., `InMemoryFileIO`, `ProtocolFileIO`).
    - [ ] Ensure all test data loading and writing is abstracted and testable via protocol.
    - **DoD:** No direct file I/O or serialization in tests except via protocol. All test I/O is mockable and standards-compliant.
    - **Artifact:** All test modules, protocol adapters, CI config.
    - **Rationale:** Enables test isolation, extensibility, and future backend swaps.

- [ ] **Canonical Models and Enums for Test Data**
    - [ ] Identify all test case definitions using `dict`, `str`, or lists of tuples.
    - [ ] Replace with canonical Pydantic models and imported Enums for all test case structures.
    - [ ] Refactor test case IDs, types, and expected results to use Enums, not string literals.
    - **DoD:** All test cases use canonical models and Enums; no string-literal IDs or types remain.
    - **Artifact:** All test modules, model/enum definitions.
    - **Rationale:** Ensures type safety, discoverability, and future evolution.

- [ ] **Test Case Injection via Registry**
    - [ ] Implement or update a protocol-driven test case registry (e.g., `ProtocolCLIDirFixtureRegistry`).
    - [ ] Refactor all test modules to use injectable, registry-driven test cases.
    - [ ] Remove all hardcoded test data from test modules; import or inject from the registry.
    - **DoD:** All test cases are registry-injectable and model-driven.
    - **Artifact:** Registry modules, test modules.
    - **Rationale:** Enables plugin/test extension and centralizes test case management.

- [ ] **Handler-Driven Parsing and Serialization**
    - [ ] Audit all test code for direct calls to `yaml.safe_load`, `json.load`, or similar.
    - [ ] Refactor all parsing/serialization to use the canonical handler registry.
    - [ ] Ensure all edge cases, delimiters, and legacy file support are covered by handler logic.
    - **DoD:** All parsing/serialization in tests uses handler registry; no direct calls remain.
    - **Artifact:** Handler registry, test modules.
    - **Rationale:** Ensures test/production logic parity and robust edge case coverage.

- [ ] **Assertions and Output Validation**
    - [ ] Identify all string-based asserts (e.g., `assert "foo" in result`).
    - [ ] Replace with model-based or Enum-based assertions using canonical result models.
    - [ ] Ensure all output validation is standards-compliant and robust to model changes.
    - **DoD:** All asserts use models/Enums; no string-based asserts for IDs, types, or results.
    - **Artifact:** Test modules, result models.
    - **Rationale:** Reduces test fragility and improves maintainability.

- [ ] **Separation of Test Types**
    - [ ] Node-local tests: Refactor to use only in-memory, protocol-driven, handler-rendered test cases.
    - [ ] Handler-level tests: Move or expand file-based fixture parsing, edge case, and delimiter tests to `tests/handlers/`.
    - [ ] Integration tests: Move or expand CLI/disk-backed, end-to-end, and negative/malformed file tests to `tests/tools/` or `tests/fixtures/`.
    - [ ] Document and enforce the separation in `docs/testing/node_testing_guidelines.md` and `docs/testing/fixtures_guidelines.md`.
    - **DoD:** All test types are separated and documented; no cross-contamination.
    - **Artifact:** Test directories, documentation.
    - **Rationale:** Supports maintainable, scalable, and reviewable test architecture.

- [ ] **Documentation and Rationale**
    - [ ] Update or create documentation for:
        - The rationale and structure for each test type.
        - The protocol-driven approach to test data and I/O.
        - The registry-driven test case injection pattern.
    - [ ] Reference all canonical models, Enums, and handler registries in documentation.
    - [ ] Add migration notes and before/after examples for maintainers.
    - **DoD:** Docs updated; migration path and rationale are clear.
    - **Artifact:** `docs/testing/node_testing_guidelines.md`, `docs/testing/fixtures_guidelines.md`, migration notes.
    - **Rationale:** Ensures future maintainers understand and can extend the system.

- [ ] **CI and Enforcement**
    - [ ] Add or update CI checks to enforce:
        - No direct file I/O or serialization in tests (except via protocol).
        - No hardcoded string literals for test case IDs, types, or results.
        - All test cases are registry-injectable and model-driven.
    - [ ] Add linter or static analysis rules to flag non-canonical patterns.
    - [ ] Ensure all new and refactored tests pass and are covered by CI.
    - **DoD:** CI/linter blocks non-canonical test patterns; all tests pass.
    - **Artifact:** CI config, linter rules, test modules.
    - **Rationale:** Prevents regression and enforces standards.

- [ ] **Review and Finalization**
    - [ ] Review all refactored test modules for compliance with project standards and naming conventions.
    - [ ] Cross-reference checklist items with milestone and documentation artifacts.
    - [ ] Solicit review from maintainers and update checklist status accordingly.
    - **DoD:** All items reviewed, cross-referenced, and approved.
    - **Artifact:** PR review, checklist updates.
    - **Rationale:** Ensures completeness and standards compliance.

5.6 **Event Bus Protocol: Dedicated Test Coverage**
    - [ ] Create a new test file: `tests/runtime/test_event_bus.py`
    - [ ] Test that a single subscriber receives published events
    - [ ] Test that multiple subscribers all receive the same event
    - [ ] Test that events are received in the order they are published
    - [ ] Test that event data (type, metadata) is preserved
    - [ ] Test that unsubscribed callbacks do not receive further events (if supported)
    - [ ] Test that exceptions in one subscriber do not prevent others from receiving events
    - [ ] Test that errors are logged or handled as per implementation
    - [ ] Test publishing with no subscribers (should not error)
    - [ ] Test subscribing/unsubscribing during event emission (if supported)
    - [ ] (Optional) Test thread safety if required by implementation
    - [ ] Add docstrings and rationale for each test
    - [ ] Ensure the new test file is included in CI runs and passes
    - [ ] Reference the new test suite in developer documentation
