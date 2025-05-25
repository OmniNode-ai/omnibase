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

### Fixture & Test Infrastructure
- [x] Stamp all fixture files and test data with canonical `.onex` metadata
    - [x] Apply stamper to YAML/JSON in `src/omnibase/schemas/schemas_tests/testdata/`
    - [x] Apply stamper to YAML/JSON in node-local fixture directories (`src/omnibase/nodes/*/v1_0_0/node_tests/fixtures/`)
    - [x] Apply stamper to YAML/JSON in validation test data (`src/omnibase/validate/validate_tests/directory_tree/test_case/`)
    - [x] Add schema validation to CI for all stamped fixtures and test data
    - [x] Confirm hash/idempotency checks for fixture inputs
    - **Rationale:** Enables reproducibility, version tracking, and compatibility with state contracts. **Note:** Fixture files are appropriately ignored by `.onexignore` patterns to preserve test data integrity.
- [x] Validate that node-local fixture directories are ignored or scoped to local test runs
    - [x] Verify `.onexignore` files exist in fixture directories (already present in `schemas_tests/testdata/` and `stamper_node/fixtures/`)
    - [x] Avoid importing node-local test helpers outside of node scope
- [x] Create centralized test fixture infrastructure
    - [x] Create `tests/fixtures/` directory for shared test fixtures
    - [x] Create `tests/data/` directory for shared test data
    - [x] Ensure each has associated `.onex` metadata and schema validation
- [x] Implement `FixtureLoaderProtocol` in `protocol/` to support fixture discovery
    - [x] Create `src/omnibase/protocol/protocol_fixture_loader.py` with the minimal interface
    - [x] Register support for central and node-scoped fixture directories
    - [x] Include fixture filtering/loading logic for CLI/CI runners
- [x] Ensure `src/omnibase/schemas/schemas_tests/testdata/` remains canonical for contract schema examples
    - [x] Verify all testdata files are properly stamped with ONEX metadata
    - [x] Add comprehensive schema validation tests
- [x] Define optional `.onextree` structure or registry loader for fixture discovery (M2 prep)
    - [x] Update `.onextree` to include fixture directory structure
    - [x] Create fixture discovery mechanism for M2 runtime loader
- [x] Update existing test discovery logic to accommodate both shared and node-local fixtures
    - [x] Enhance `src/omnibase/fixtures/protocol_cli_dir_fixture_registry.py` for centralized fixture management
    - [x] Update node test runners to support both local and shared fixtures
- [x] Add CI task to flag orphaned fixtures and unused data files
    - [x] Create script to scan for unreferenced YAML/JSON files in fixture directories
    - [x] Add CI check to auto-report unreferenced fixture files
    - [x] Implement fixture usage tracking and cleanup recommendations
    - **Rationale:** Prevent drift and bloat from accumulating unused test assets.

### Advanced Node & CLI Features
- [x] **Telemetry Decorator:** Implement and apply a telemetry decorator to all node entrypoints.
    - **DoD:** Decorator standardizes logging context, timing, event emission, and error handling.
    - **Artifact:** `src/omnibase/nodes/stamper_node/telemetry.py`, applied in `main.py`.
- [x] **Correlation/Request ID Propagation:** Add and propagate correlation/request IDs in all state models and ONEX events.
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

### Deferred Items
- [ ] Reducer snapshot test (deferred)
    - **Note:** Deferred until reducer protocol is fully specified in M2. See `tests/protocol/test_reducer_snapshot.py` for stub.

---

## MILESTONE 1 COMPLETION REQUIREMENTS

*These tasks are required to complete Milestone 1 and establish the foundation for Milestone 2 development.*

### Release Infrastructure & Stable Branch Strategy
- [ ] **Establish Stable Branch Strategy**
    - [ ] Create `stable/m1` branch from main for Milestone 1 release
    - [ ] Define branch protection rules for stable branch (require PR reviews, status checks)
    - [ ] Document stable branch workflow in `docs/development/branching_strategy.md`
    - [ ] Update contributor guidelines to reference stable branch process
    - **Artifact:** `stable/m1` branch, branch protection rules, documentation
    - **DoD:** Stable branch created with proper protection rules; workflow documented

- [ ] **CI Release Process Implementation**
    - [ ] Create GitHub Actions workflow for automated weekly releases
    - [ ] Implement semantic versioning strategy (e.g., `v1.0.0-rc.1`, `v1.0.0`)
    - [ ] Add release notes generation from PR descriptions and commit messages
    - [ ] Configure release artifact generation (source code, documentation)
    - [ ] Add release validation checks (all tests pass, documentation builds)
    - **Artifact:** `.github/workflows/release.yml`, release configuration
    - **DoD:** Automated release process creates tagged releases with proper artifacts

- [ ] **Release Candidate Testing**
    - [ ] Create RC testing checklist for manual validation
    - [ ] Implement smoke tests for critical functionality
    - [ ] Add integration test suite for end-to-end workflows
    - [ ] Document release validation procedures
    - **Artifact:** `docs/testing/release_validation.md`, smoke test suite
    - **DoD:** RC testing process validates core functionality before release

- [ ] **Version Management & Tagging**
    - [ ] Implement version bumping strategy in CI
    - [ ] Add version validation in pre-commit hooks
    - [ ] Create changelog generation from conventional commits
    - [ ] Tag Milestone 1 completion with `v1.0.0` release
    - **Artifact:** Version management scripts, changelog automation
    - **DoD:** Consistent versioning across all components; automated changelog

- [ ] **Documentation for Milestone 1 Release**
    - [ ] Create comprehensive release notes for v1.0.0
    - [ ] Update README with installation and usage instructions
    - [ ] Document migration path from development to stable branch
    - [ ] Create getting started guide for new contributors
    - **Artifact:** Release notes, updated documentation, migration guide
    - **DoD:** Complete documentation package for Milestone 1 release

- [ ] **Milestone 1 Completion Validation**
    - [ ] Run full test suite on stable branch (all 243+ tests passing)
    - [ ] Validate all checklist items are completed
    - [ ] Perform end-to-end validation of core ONEX workflows
    - [ ] Generate final Milestone 1 completion report
    - **Artifact:** Completion report, test results, validation checklist
    - **DoD:** All M1 requirements validated; ready for M2 development

### Pre-Milestone 2 Preparation
- [ ] **Milestone 2 Planning & Setup**
    - [ ] Create `
