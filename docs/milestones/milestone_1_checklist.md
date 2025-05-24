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
> **Last Updated:** 2025-05-24
> **Purpose:** This checklist enumerates all implementation steps required to complete Milestone 1 of the ONEX Execution Architecture. Each item is actionable, testable, and maps directly to the deliverables in [onex_execution_architecture.md](./onex_execution_architecture.md).

> **Note:** Completed items are summarized for brevity; see git history for full details.

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

### CRITICAL PATH: .onextree and Registry Loader ✅ COMPLETED

> **Summary:** All critical path items for .onextree and registry loader have been completed. The .onextree manifest accurately reflects the directory structure, all artifact metadata files are present with compatibility metadata, registry loader logic is fully documented and tested, and CI validation is enforced. Migration documentation and examples have been provided for maintainers. See git history for full implementation details.

<details>
<summary><strong>✅ Registry Node Conversion</strong> (Click to expand)</summary>

**Registry Node Conversion ✅ COMPLETED:**
- [x] **Design Registry Node Architecture** ✅ COMPLETED
- [x] **Implement Registry Loader Node** ✅ COMPLETED (PR #22)
- [x] **Implement Bootstrap Registry** ✅ COMPLETED
- [x] **Implement Registry Bridge** ✅ COMPLETED
- [x] **Testing and Validation** ✅ COMPLETED
- [x] **Documentation and Migration** ✅ COMPLETED
- [x] **Cleanup and Finalization** ✅ COMPLETED

**Migration Summary:**
- **Complete migration** from legacy registry infrastructure to registry loader node
- **Zero breaking changes** during transition via bridge pattern
- **1,600+ lines of legacy code removed** across cleanup phases
- **Direct usage** of registry loader node state models (RegistryLoaderInputState, RegistryLoaderOutputState)
- **Protocol-driven testing** with fixture injection and model-based assertions
- **Comprehensive test coverage** maintained throughout migration
- **Project structure cleanup** with 7 empty directories removed and configuration updated
</details>

## COMPLETED FOUNDATIONS

<details>
<summary><strong>✅ Schema & Protocol Definition</strong> (Click to expand)</summary>

> **Summary:** All canonical schemas and protocols for `.onex` metadata, `.onextree` directory structure, `execution_result`, and `state_contract` have been defined, versioned, and validated. Dual-format (YAML/JSON) support is implemented and tested. Schema changelogs, versioning, and deprecation policies are documented. All related unit/integration tests are passing, and usage examples are present in the documentation. CI validation for node metadata and state contracts is enforced. See `/schemas/`, `/docs/`, and test modules for details.
</details>

<details>
<summary><strong>✅ Tooling & Automation</strong> (Click to expand)</summary>

> **Summary:** All core tooling and automation for ONEX has been implemented and validated. This includes protocol docstring/Markdown doc generators, Node Author Quickstart guide, metadata stamper and validator CLI tools, structured .onexignore support with YAML models and multi-tool integration, and enhanced metadata stamper with recursive directory traversal and CI/pre-commit integration. All tools support protocol-driven architecture with comprehensive error reporting, modular structure, and extensive test coverage. Stamper restamping issue resolved with comprehensive .onexignore patterns for configuration files. See `/tools/`, `/docs/quickstart.md`, and related test modules for details.
</details>

<details>
<summary><strong>✅ Node Creation Foundation</strong> (Click to expand)</summary>

> **Summary:** Canonical node structure has been established with standardized `name_type/` format, required files (`node.py`, `state_contract.yaml`, `.onex` metadata), and comprehensive documentation in `docs/nodes/structural_conventions.md`. All nodes follow the established patterns for discoverability, validation, and maintainability.
</details>

<details>
<summary><strong>✅ Stamper Node Implementation</strong> (Click to expand)</summary>

> **Summary:** Complete stamper node implementation with canonical directory structure, metadata files, source code migration, comprehensive test suite, documentation, CLI integration, and event emission. All components follow versioned node structure with proper import paths and canonical structure. Directory restructuring completed with all artifacts migrated to registry-centric, versioned directories. See `/nodes/stamper_node/`, related test modules, and documentation for details.
</details>

<details>
<summary><strong>✅ Tree Generator Node Implementation</strong> (Click to expand)</summary>

> **Summary:** Complete tree generator node implementation following stamper node patterns with canonical directory structure, helpers/tree_generator_engine.py containing core logic (274 lines), reduced node.py from 419 to 191 lines (54% reduction), standardized node function with proper event emission, fixed OnexStatus enum usage and import patterns for MyPy compliance. Constants file created with centralized status constants, message templates, and event types to prevent hardcoded string maintenance issues. All tests updated to use status-based assertions instead of fragile string parsing. All 16 tests pass including comprehensive .onextree validation tests. All pre-commit hooks pass and functionality verified. See `/nodes/tree_generator_node/`, related test modules, and documentation for details.
</details>

<details>
<summary><strong>✅ Fixture Strategy and Layout</strong> (Click to expand)</summary>

> **Summary:** Hybrid fixture structure established with central shared and node-local patterns, documented in `docs/testing/fixtures_guidelines.md`. This approach supports both encapsulation and reusability across nodes while enabling scalable test design.
</details>

<details>
<summary><strong>✅ Protocol & Interface Remediation</strong> (Click to expand)</summary>

> **Summary:** All core interfaces refactored to use canonical Protocols: FileTypeHandlerRegistry, SchemaExclusionRegistry, DirectoryTraverser, and hash utilities. All protocols are strongly typed, documented, and tested for conformance. Hash utilities use canonical Enums (NodeMetadataField) and serializers. See `/runtime/protocol/` and related test modules for details.
</details>

<details>
<summary><strong>✅ Runtime Directory Refactor</strong> (Click to expand)</summary>

> **Summary:** Complete runtime directory structure established with canonical subdirectories (`filesystem/`, `io/`, `crypto/`). All shared execution utilities migrated with imports updated across nodes and tools, duplicate copies removed, and comprehensive documentation added.
</details>

<details>
<summary><strong>✅ Runtime & Event Execution Layer</strong> (Click to expand)</summary>

> **Summary:** Complete event-driven runtime architecture implemented with OnexEvent model, EventBusProtocol, in-memory event bus, NodeRunner for node execution with event emissions, MessageBusAdapter for event forwarding, PostgresEventStore for durability, and CLI command `onex run <node>`. All components emit standard events (`NODE_START`, `NODE_SUCCESS`, `NODE_FAILURE`) and integrate with ledger persistence. See `/onex/core/events/`, `/onex/runtime/`, and related modules for details.
</details>

<details>
<summary><strong>✅ Additional Completed Items</strong> (Click to expand)</summary>

> **Summary:** yamllint integrated into pre-commit hooks for schema validation. All YAML schema/model/test alignment and enforcement implemented with comprehensive pre-commit hooks (yamllint, mypy, etc.) passing. Manual line wrapping for canonical schema YAML completed for full yamllint compliance. Stamper node refactor completed with node-local state models moved to `models/` directory, commented stub imports removed, and runtime version injection enforced. Enhanced .onexignore system with comprehensive patterns for configuration files (contract YAML files, CLI tool configs, runtime configs) to prevent stamper restamping issues.
</details>

---

## REMAINING IMPLEMENTATION TASKS

### CI & Enforcement
- [ ] Integrate CI enforcement: all nodes must pass schema validation for metadata, execution result, and state contract
    - [ ] CI blocks non-compliant commits, reviewed by Infra lead
    - [ ] CI test coverage for all enforcement logic
- [x] Integrate CI enforcement: `.onextree` file must match directory contents and reference valid `.onex` files
    - [x] CI blocks drift, reviewed by CAIA
    - [x] CI test coverage for all enforcement logic
- [ ] Integrate CI enforcement: lifecycle field must be valid and hash-stamped
    - [ ] CI blocks invalid lifecycle/hash, reviewed by Infra lead
    - [ ] CI test coverage for all enforcement logic
- [x] Add pre-commit hooks for schema validation and `.onextree` sync
    - [x] Hooks block non-compliant commits locally, reviewed by Foundation team
- [ ] Add CI metrics dashboard (badge or report in README)
    - [ ] Dashboard live and reporting, reviewed by Infra lead
    - [ ] Metrics reporting tested
- [ ] Write test cases for schema evolution and backward compatibility
    - [ ] Test cases merged, reviewed by Foundation team
- [ ] Document node lifecycle policy (draft, review, active, deprecated)
    - [ ] Policy published in docs, reviewed by CAIA
- [ ] Define and enforce canonical error taxonomy for validation failures
    - [ ] Error taxonomy published and used in all tools, reviewed by Infra lead

### Protocols & Models (Shared Core)
- [ ] Ensure all protocols are defined in `src/omnibase/protocol/` and are not duplicated in node directories
- [ ] Ensure all models/enums are defined in `src/omnibase/model/` and are not duplicated in node directories
- [ ] Update documentation to clarify the separation and reference pattern for protocols and models
- [ ] Add/expand tests for protocol/model contract compliance in `tests/protocol/` and `tests/model/`
- [ ] Refactor any node, tool, or CLI code to import protocols/models from the shared location
- [ ] Review and document versioning and changelog policies for protocols and models

### Handler & Plugin System
- [ ] Canonicalize handler and registry logic in core/runtime
    - All official handlers and the file type handler registry are defined and maintained in `omnibase.runtime.handlers` and `omnibase.core.core_file_type_handler_registry`.
    - Node-local handler/registry logic is removed or migrated.
    - All node/CLI imports reference only canonical modules.
    - **Artifact:** `/src/omnibase/runtime/handlers/`, `/src/omnibase/core/core_file_type_handler_registry.py`
    - **DoD:** No node-local handler/registry logic remains; all tests pass.
- [ ] Implement plugin/override API for node-local handler extensions
    - Expose a minimal, versioned `register_handler(name, HandlerClass)` API.
    - Document plugin/override mechanism in code and developer docs.
    - Provide canonical example in node entrypoint/helpers.
    - **Artifact:** `/src/omnibase/runtime/handlers/`, `/docs/nodes/structural_conventions.md`
    - **DoD:** Node-local handler registration works and is documented.
- [ ] Handler/plugin metadata and introspection
    - Require all handlers/plugins to declare metadata (supported file types, version, author, etc.).
    - Enforce via code review and CI.
    - **Artifact:** `/src/omnibase/runtime/handlers/`
    - **DoD:** All handlers/plugins have metadata; CI enforces.
- [ ] Document and version handler/registry API
    - Publish Handler/Registry API doc and CHANGELOG.
    - Tag releases with semver.
    - Provide migration guides.
    - **Artifact:** `/docs/handlers_registry_api.md`, `/CHANGELOG.md`
    - **DoD:** Docs and changelog published; migration guide available.
- [ ] Governance and review process for plugins
    - Define review process for new plugins/handlers.
    - Add PR template checklist or architectural review step.
    - **Artifact:** `.github/PULL_REQUEST_TEMPLATE.md`
    - **DoD:** All plugin/handler PRs follow review process.
- [ ] Define plugin discovery entry-point patterns and document in developer guide
    - **Artifact:** `/docs/plugins/entry_points.md`
    - **DoD:** Developers can load handlers via entry-points; example documented.
- [ ] Establish plugin priority and conflict-resolution rules
    - **Artifact:** `/docs/plugins/conflict_resolution.md`
    - **DoD:** Core vs node-local handlers have defined load order; documented and enforced.
- [ ] Add CLI command to list all registered handlers and plugins
    - **Artifact:** `onex/cli/commands/list_handlers.py`
    - **DoD:** `onex handlers list` outputs handler name, source (core/plugin), and version.
- [ ] Write tests for plugin override resolution order and failure cases
    - **Artifact:** `tests/runtime/test_plugin_resolution.py`
    - **DoD:** Unit tests cover core-only, plugin-only, and override scenarios.

### Fixture & Test Infrastructure
- [ ] Stamp all fixture files and test data with canonical `.onex` metadata
    - [ ] Apply stamper to YAML/JSON in `tests/fixtures/` and `tests/data/`
    - [ ] Apply stamper to YAML/JSON in all node-local fixture and `data/` folders
    - [ ] Add schema validation to CI for all stamped fixtures and test data
    - [ ] Confirm hash/idempotency checks for fixture inputs
    - **Rationale:** Enables reproducibility, version tracking, and compatibility with state contracts.
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

### Advanced Node & CLI Features
- [ ] **Telemetry Decorator:** Implement and apply a telemetry decorator to all node entrypoints.
    - **DoD:** Decorator standardizes logging context, timing, event emission, and error handling.
    - **Artifact:** `src/omnibase/nodes/stamper_node/telemetry.py`, applied in `main.py`.
- [ ] **Correlation/Request ID Propagation:** Add and propagate correlation/request IDs in all state models and ONEX events.
    - **DoD:** ID generated at CLI layer if not provided, present in all logs/events.
    - **Artifact:** `StamperInputState`, `StamperOutputState`, event models.
- [ ] **Telemetry/Log Subscriber Utility:** Implement a utility to subscribe to telemetry decorator events/logs and print/process them in real time.
    - **DoD:** Utility subscribes to event bus or log stream, prints or processes logs for local/CI use.
    - **Artifact:** `src/omnibase/nodes/stamper_node/telemetry_subscriber.py` (or runtime/events/).
- [ ] **ONEX Event Schema Standardization:** Define and document the canonical ONEX event schema.
    - **DoD:** Schema documented in `docs/protocol/onex_event_schema.md`, all emitters conform.
    - **Artifact:** Event emitter modules, schema doc.
- [ ] **Event Emission Tests:** Add tests to validate event emission and telemetry subscriber output.
    - **DoD:** Tests in `tests/nodes/stamper_node/` or `tests/runtime/events/`.
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
- [ ] **Update Documentation:** Update `README.md` and developer docs to cover all new requirements, including telemetry, event schema, plugin loading, error code mapping, redaction, and correlation/tracing.
    - **DoD:** Docs updated, usage and rationale for each new feature explained.
    - **Artifact:** `README.md`, `docs/nodes/canary_node_cli_alignment.md`, developer guides.

### Test Canonicalization and Protocol-Driven Refactor
- [ ] **Handler/Fixture/Integration Test Separation and Coverage**
    - [ ] All test cases (node-local, handler, integration, fixture) must be generated or injected via protocol-driven registries or handler serialization methods.
    - [ ] Assertions must be model-based or handler-driven, never string-based for domain fields.
    - [ ] All test parameterization must use protocol-driven registries or fixtures.
    - [ ] All test files must be reviewed for: no hardcoded domain values, no string-based assertions for domain fields, no parallel or ad-hoc logic for metadata block construction or parsing, full round-trip and idempotency coverage using handler logic.
    - [ ] Refactor node-local tests to use only in-memory, protocol-driven, handler-rendered test cases (no file-based fixtures for canonical/positive cases)
    - [ ] Add/expand handler-level tests in `tests/handlers/` to cover: file-based fixture parsing, edge cases and malformed files, delimiter/comment handling and legacy file support
    - [ ] Add/expand integration tests in `tests/tools/` or `tests/fixtures/` to cover: CLI and disk-backed stamping flows, end-to-end stamping and validation with real files, negative/malformed file scenarios
    - [ ] Ensure all handler/fixture/integration tests are separated from node-local protocol tests
    - [ ] Document the separation and rationale in `docs/testing/node_testing_guidelines.md` and `docs/testing/fixtures_guidelines.md`
- [ ] **Protocol-Driven File I/O in Tests**
    - [ ] Audit all test files for direct use of `open`, `Path`, `write_text`, `yaml.safe_load`, `json.load`, and similar.
    - [ ] Refactor all file I/O in tests to use protocol-driven adapters (e.g., `InMemoryFileIO`, `ProtocolFileIO`).
    - [ ] Ensure all test data loading and writing is abstracted and testable via protocol.
- [ ] **Canonical Models and Enums for Test Data**
    - [ ] Identify all test case definitions using `dict`, `str`, or lists of tuples.
    - [ ] Replace with canonical Pydantic models and imported Enums for all test case structures.
    - [ ] Refactor test case IDs, types, and expected results to use Enums, not string literals.
- [ ] **Test Case Injection via Registry**
    - [ ] Implement or update a protocol-driven test case registry (e.g., `ProtocolCLIDirFixtureRegistry`).
    - [ ] Refactor all test modules to use injectable, registry-driven test cases.
    - [ ] Remove all hardcoded test data from test modules; import or inject from the registry.
- [ ] **Handler-Driven Parsing and Serialization**
    - [ ] Audit all test code for direct calls to `yaml.safe_load`, `json.load`, or similar.
    - [ ] Refactor all parsing/serialization to use the canonical handler registry.
    - [ ] Ensure all edge cases, delimiters, and legacy file support are covered by handler logic.
- [ ] **Assertions and Output Validation**
    - [ ] Identify all string-based asserts (e.g., `assert "foo" in result`).
    - [ ] Replace with model-based or Enum-based assertions using canonical result models.
    - [ ] Ensure all output validation is standards-compliant and robust to model changes.
- [ ] **Separation of Test Types**
    - [ ] Node-local tests: Refactor to use only in-memory, protocol-driven, handler-rendered test cases.
    - [ ] Handler-level tests: Move or expand file-based fixture parsing, edge case, and delimiter tests to `tests/handlers/`.
    - [ ] Integration tests: Move or expand CLI/disk-backed, end-to-end, and negative/malformed file tests to `tests/tools/` or `tests/fixtures/`.
    - [ ] Document and enforce the separation in `docs/testing/node_testing_guidelines.md` and `docs/testing/fixtures_guidelines.md`.
- [ ] **Documentation and Rationale**
    - [ ] Update or create documentation for: the rationale and structure for each test type, the protocol-driven approach to test data and I/O, the registry-driven test case injection pattern.
    - [ ] Reference all canonical models, Enums, and handler registries in documentation.
    - [ ] Add migration notes and before/after examples for maintainers.
- [ ] **CI and Enforcement**
    - [ ] Add or update CI checks to enforce: no direct file I/O or serialization in tests (except via protocol), no hardcoded string literals for test case IDs, types, or results, all test cases are registry-injectable and model-driven.
    - [ ] Add linter or static analysis rules to flag non-canonical patterns.
    - [ ] Ensure all new and refactored tests pass and are covered by CI.
- [ ] **Review and Finalization**
    - [ ] Review all refactored test modules for compliance with project standards and naming conventions.
    - [ ] Cross-reference checklist items with milestone and documentation artifacts.
    - [ ] Solicit review from maintainers and update checklist status accordingly.

### Event Bus Protocol: Dedicated Test Coverage
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

### Deferred Items
- [ ] Reducer snapshot test (deferred)
    - **Note:** Deferred until reducer protocol is fully specified in M2. See `tests/protocol/test_reducer_snapshot.py` for stub.

---

## OPTIONAL ENHANCEMENTS (M2 PREP)

*These items are not required for Milestone 1 completion but are recommended for enhanced quality or preparation for future milestones.*

- [ ] Implement plugin validation hook system for custom/org-specific checks
    - **Priority:** Recommended for M2
- [ ] Implement validation report artifact (e.g., `validation_report.json`) for each node
    - **Priority:** Recommended for M2
- [ ] Add historical compliance tracking (weekly trend)
    - **Priority:** Stretch goal
- [ ] Add optional metadata signing for `.onex` files
    - **Priority:** Stretch goal
- [ ] Propose reorganization: move all runnable nodes into `src/omnibase/nodes/`
    - **Priority:** High
- [ ] Flatten and document node helper structure
    - Move all node-local helpers to a single `helpers/` directory at node root.
- [ ] Provide node bootstrap/scaffold utility
    - Implement/maintain CLI tool to generate standardized node skeletons.
- [ ] Enforce handler/registry import and plugin usage via linting/CI
    - Add/update CI rules to block disallowed imports and enforce plugin API usage.

---

> **NOTE:** This checklist is dynamically ordered for solo, sequential implementation. The critical path (.onextree manifest and loader) must be completed before most other tasks can proceed.

> Once all items are checked, Milestone 1 is complete and the project may proceed to Milestone 2: Runtime Loader and Executable Scaffold Node.

> ⚠️ **Reminder:** The core functional outcome of M2 is a scaffold node that builds other nodes using these M1-defined protocols. This is the heart of the ONEX MVP and should inform your implementation here.
