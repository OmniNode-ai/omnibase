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

## REMAINING TASKS

### Advanced Node & CLI Features
- [x] **Schema Versioning:** Embed version fields in all state models and maintain a schema changelog (`CHANGELOG.stamper.md`).
    - **DoD:** Version field present, changelog updated on every schema change.
    - **Artifact:** State models, `CHANGELOG.stamper.md`.
    - **Note:** ✅ **COMPLETE** - Implemented across all nodes with schema version constants (stamper: 1.1.1, others: 1.0.0), comprehensive changelogs, validation utilities, and 24 test methods for schema versioning functionality. All DoD criteria met: version fields present, changelogs maintained, artifacts created.
- [x] **CLI/Node Output Parity Harness:** Add a test harness to verify CLI and direct node invocations produce identical output.
    - **DoD:** Test module (e.g., `test_canary_equivalence.py`) in `tests/nodes/stamper_node/`.
    - **Note:** ✅ **FULLY COMPLIANT WITH TESTING STANDARDS + CI INTEGRATION** - Implemented as comprehensive test harness in `tests/test_cli_node_parity.py` covering ALL ONEX nodes (stamper, tree_generator, registry_loader, schema_generator, template). Successfully validates CLI/node interface consistency with 12/13 tests passing (1 skipped in mock context). **UPDATED:** Fixed all testing standards violations per docs/testing.md: uses canonical OnexStatus enum throughout, project-specific CLINodeParityError from core/errors.py, proper TODO documentation for manual registry with issue tracking, comprehensive fixture injection with context validation, and robust error handling with canonical status mapping. Establishes canonical patterns for validating CLI/node parity across the entire ecosystem with full protocol-first testing compliance and continuous validation.
- [x] **Error Code to Exit Code Mapping:** Map error codes to CLI exit codes and enforce in CLI adapters.
    - **DoD:** Mapping in shared module, CLI adapters use canonical exit codes.
    - **Note:** ✅ **FULLY IMPLEMENTED ACROSS ALL NODES** - Comprehensive error code system implemented with:
      - **Canonical Exit Code Mapping:** All nodes now use `get_exit_code_for_status(OnexStatus)` from `core/error_codes.py`
      - **Node-Specific Error Codes:** Created comprehensive error code modules for all nodes:
        - `stamper_node/v1_0_0/error_codes.py` - 20 error codes (ONEX_STAMP_*)
        - `tree_generator_node/v1_0_0/error_codes.py` - 16 error codes (ONEX_TREE_*)
        - `registry_loader_node/v1_0_0/error_codes.py` - 20 error codes (ONEX_REGISTRY_*)
        - `schema_generator_node/v1_0_0/error_codes.py` - 16 error codes (ONEX_SCHEMA_*)
        - `template_node/v1_0_0/error_codes.py` - 16 error codes (ONEX_TEMPLATE_*)
      - **CLI Integration:** All node CLIs updated to use canonical exit codes instead of hardcoded 0/1
      - **Error Categories:** Each node has categorized errors (directory, file, validation, configuration, etc.)
      - **Exit Code Conventions:** 0=success, 1=error, 2=warning, 3=partial, 4=skipped, 5=fixed, 6=info
      - **Registry Integration:** All error codes registered with global error code registry
      - **Testing:** CLI/Node parity tests validate consistent exit code behavior across all interfaces
- [x] **Standardized Node Introspection:** Implement `--introspect` command for all ONEX nodes to expose contract, states, dependencies, and error codes.
    - **DoD:** All nodes support `--introspect` command returning standardized JSON response with node metadata, contract, state models, error codes, dependencies, and capabilities.
    - **Artifact:** Base introspection mixin, standardized response format, updated CLI interfaces for all nodes.
    - **Rationale:** Enables auto-discovery and validation of third-party nodes, provides self-documenting capabilities, supports generic tooling and ecosystem development.
    - **Note:** ✅ **FULLY IMPLEMENTED ACROSS ALL NODES** - Comprehensive introspection system implemented with:
      - **Base Infrastructure:** Created `NodeIntrospectionMixin` in `src/omnibase/mixin/introspection_mixin.py` with standardized interface
      - **Response Models:** Defined comprehensive Pydantic models in `src/omnibase/model/model_node_introspection.py` for structured JSON responses
      - **Node Implementations:** All 5 ONEX nodes now support `--introspect` command:
        - `stamper_node` - File metadata stamping with 20 error codes, supports dry-run and batch processing
        - `tree_generator_node` - Directory tree generation with 16 error codes, supports validation
        - `registry_loader_node` - ONEX registry loading with 25 error codes, supports artifact filtering
        - `schema_generator_node` - JSON schema generation with 21 error codes, supports batch processing
        - `template_node` - Template file generation with 20 error codes, supports variable substitution
      - **Comprehensive Metadata:** Each introspection response includes node metadata, contract specification, state models, error codes, dependencies, capabilities, and CLI interface
      - **CLI Integration:** All nodes updated with `--introspect` argument and proper handling logic
      - **Self-Documenting:** Nodes expose their complete contract via standardized JSON format enabling auto-discovery and validation
      - **Third-Party Ready:** Provides foundation for external developers to validate and integrate with ONEX ecosystem
- [x] **Parity Validator Node:** Replace hardcoded CLI/Node parity tests with a dedicated `parity_validator_node` that auto-discovers and validates all ONEX nodes.
    - **DoD:** Complete `parity_validator_node` implementation with auto-discovery via introspection, comprehensive validation (CLI/node parity, schema conformance, error code usage, contract compliance), structured reporting, and integration into pre-commit/CI replacing current hardcoded tests.
    - **Artifact:** `src/omnibase/nodes/parity_validator_node/v1_0_0/`, updated `.pre-commit-config.yaml`, updated CI workflows, third-party developer documentation.
    - **Rationale:** Provides public validation tool for third-party developers, eliminates manual test maintenance, enables comprehensive ecosystem quality assurance, follows ONEX "everything is a node" philosophy.
    - **Note:** ✅ **FULLY IMPLEMENTED** - Complete parity validator node with comprehensive validation capabilities:
      - **Auto-Discovery:** Automatically discovers all ONEX nodes in specified directory (discovered 6 nodes: template, schema_generator, registry_loader, stamper, tree_generator, parity_validator)
      - **CLI/Node Parity Validation:** Validates consistent behavior between CLI and direct node execution (25/25 passed)
      - **Schema Conformance Validation:** Validates proper state model implementation and structure (all nodes passed)
      - **Error Code Usage Validation:** Validates proper error code definitions and usage patterns (all nodes passed)
      - **Contract Compliance Validation:** Validates adherence to ONEX node protocol requirements (all nodes passed)
      - **Introspection Validity Validation:** Validates proper introspection implementation and output (5 skipped for nodes without introspection)
      - **Comprehensive State Models:** Full input/output state models with validation and factory functions
      - **Error Code System:** 28 comprehensive error codes covering all validation scenarios
      - **CLI Interface:** Complete argparse-based CLI with all validation options (--nodes-directory, --validation-types, --node-filter, --fail-fast, --format, etc.)
      - **Introspection Support:** Full introspection capability with detailed node metadata
      - **Performance Metrics:** Optional execution timing for all validation operations
      - **Flexible Output Formats:** Support for JSON, summary, and detailed output formats
      - **Schema Version:** 1.0.0 with comprehensive validation models registered in global schema validator
      - **Testing Results:** All 30 validations completed successfully (25 passed, 0 failed, 5 skipped, 0 errors)
      - **Self-Validation:** The parity validator node successfully validates itself, demonstrating proper implementation
      - **CI/CD Integration:** ✅ **COMPLETE** - Fully integrated into CI and pre-commit workflows:
        - **Pre-commit Hook:** Replaced old pytest-based parity tests with `poetry run python -m omnibase.nodes.parity_validator_node.v1_0_0.node --format summary --fail-fast`
        - **CI Workflow:** Updated `.github/workflows/ci.yml` with comprehensive validation jobs:
          - **Basic Parity Job:** Fast summary validation with correlation ID tracking
          - **Comprehensive Validation Job:** Full JSON output with individual validation type testing and node filtering validation
        - **Automated Validation:** All 5 validation types (CLI/Node parity, schema conformance, error code usage, contract compliance, introspection validity) run automatically in CI
        - **Performance:** Pre-commit hook runs in ~1-2 seconds, CI validation completes in ~10-15 seconds
        - **Coverage:** Validates all 6 discovered ONEX nodes across all validation dimensions
        - **Correlation Tracking:** CI runs include GitHub run ID for request correlation and telemetry
- [ ] **Function Metadata Extension:** Extend the existing metadata stamping system to support Python functions with comprehensive metadata, discovery, and introspection capabilities.
    - **DoD:** Function stamping capability, function discovery and introspection, CLI integration for function operations, validation of function metadata schemas.
    - **Artifact:** Enhanced stamper node with function support, function metadata models, CLI commands for function operations, function discovery utilities.
    - **Rationale:** Natural extension of existing metadata infrastructure, provides foundation for M2 dynamic tool composition, validates metadata patterns at function granularity, enables function-level introspection and discovery.
    - **Scope:** Function metadata stamping, discovery, and introspection only. Excludes in-memory execution, Redux state management, channels, and dynamic composition (deferred to M2).
    - **Implementation Strategy:**
      - **Phase 1: Function Metadata Schema (1-2 days)**
        - Define `FunctionMetadataBlock` Pydantic model with fields: id, name, description, inputs, outputs, side_effects, state_dependencies, hash, parent_file, node_type, created_at
        - Add function metadata validation and schema versioning
        - Create function-specific error codes and validation rules
      - **Phase 2: Function Stamper (2-3 days)**
        - Extend existing stamper node to parse Python AST and identify functions
        - Add function metadata extraction from docstrings, type hints, and signatures
        - Support docstring-based metadata blocks with ONEX function metadata format
        - Implement function hash calculation and change detection
      - **Phase 3: Function Discovery & Introspection (1-2 days)**
        - Extend auto-discovery system to find and catalog stamped functions
        - Add function introspection to existing introspection mixin
        - Update parity validator to validate function metadata compliance
        - Support function filtering and search capabilities
      - **Phase 4: CLI Integration (1 day)**
        - Add `onex stamp function <file_or_directory>` command
        - Add `onex list-functions [--filter]` command for function discovery
        - Add `onex function-info <function_id>` command for detailed function introspection
        - Integrate function operations with existing CLI infrastructure
    - **Benefits for M1:** Demonstrates metadata system versatility, provides foundation for M2 without overcommitting, uses existing infrastructure with minimal new complexity, validates introspection patterns at function granularity
    - **Estimated Effort:** 4-6 days vs. 3-4 weeks for full in-memory nodes system
    - **Risk Level:** Low - natural extension of proven metadata stamping system
    - **Note:** ⏳ **PLANNED FOR M1** - Approved as natural extension of existing metadata infrastructure, provides stepping stone to M2 dynamic tool composition while maintaining M1 scope boundaries
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
    - [ ] Run full test suite on stable branch (all 258+ tests passing)
    - [ ] Validate all checklist items are completed
    - [ ] Perform end-to-end validation of core ONEX workflows
    - [ ] Generate final Milestone 1 completion report
    - **Artifact:** Completion report, test results, validation checklist
    - **DoD:** All M1 requirements validated; ready for M2 development

### Pre-Milestone 2 Preparation
- [ ] **Milestone 2 Planning & Setup**
    - [ ] Create `feature/m2-runtime-loader` branch from stable/m1
    - [ ] Draft Milestone 2 implementation checklist
    - [ ] Set up M2 development environment and dependencies
    - [ ] Plan M2 development timeline and resource allocation
    - **Artifact:** M2 branch, M2 checklist, development plan
    - **DoD:** M2 development environment ready; clear implementation plan

- [ ] **Handoff Documentation**
    - [ ] Document M1 architecture decisions and rationale
    - [ ] Create M2 development guide referencing M1 foundations
    - [ ] Update project roadmap with M1 completion and M2 goals
    - [ ] Prepare M1 retrospective and lessons learned
    - **Artifact:** Architecture documentation, M2 guide, roadmap update
    - **DoD:** Clear handoff documentation for M2 development team

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

## COMPLETED FOUNDATIONS

*These sections have been completed and form the foundation for remaining work.*

### ✅ Fixture & Test Infrastructure (COMPLETE)
- All fixture files stamped with canonical `.onex` metadata
- Centralized test fixture infrastructure with `tests/fixtures/` and `tests/data/`
- `FixtureLoaderProtocol` implemented for fixture discovery
- CI tasks for orphaned fixture detection

### ✅ Telemetry & Event Infrastructure (COMPLETE)
- Telemetry decorator implemented and applied to all node entrypoints
- Correlation/Request ID propagation in all state models and ONEX events
- Telemetry/Log subscriber utility for real-time event processing
- ONEX Event Schema standardization with comprehensive documentation
- Event emission tests with 11 test methods validating complete event flow

### ✅ Schema Infrastructure (COMPLETE)
- JSON Schema generation implemented as `
