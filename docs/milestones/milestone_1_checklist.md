<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:40:26.539104'
description: Stamped by ONEX
entrypoint: python://milestone_1_checklist.md
hash: 5b306bf423cb50bdfb3f123f7d684d17542b2859ea127793a4ab42dff24685df
last_modified_at: '2025-05-29T11:50:15.026166+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: milestone_1_checklist.md
namespace: omnibase.milestone_1_checklist
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: dd263972-9b84-46c1-ae8c-7b642d62c839
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# Milestone 1 Implementation Checklist: ONEX Node Protocol, Schema, Metadata, and CI Enforcement

## REMAINING TASKS

    - **Example Unified Metadata (Language-Agnostic):**
      ```yaml
      # === OmniNode:Metadata ===
      # ... standard 21-line file metadata ...
      # tools:
      #   validate_schema:
      #     type: function
      #     language: python
      #     line: 45
      #     description: "Validates JSON schema format and structure"
      #     inputs: ["schema: Dict[str, Any]", "correlation_id: Optional[str]"]
      #     outputs: ["ValidationResult"]
      #     error_codes: ["SCHEMA_INVALID", "SCHEMA_MALFORMED"]
      #     side_effects: ["logs validation events"]
      #   processData:
      #     type: function
      #     language: javascript
      #     line: 78
      #     description: "Process and transform input data"
      #     inputs: ["data: any", "transformRules: string[]"]
      #     outputs: ["ProcessedData"]
      #     error_codes: ["DATA_INVALID", "TRANSFORM_FAILED"]
      #     side_effects: ["logs processing events", "may cache results"]
      #   backup_files:
      #     type: function
      #     language: bash
      #     line: 15
      #     description: "Backup files to specified directory"
      #     inputs: ["source_dir: string", "backup_dir: string"]
      #     outputs: ["exit_code: number"]
      #     error_codes: ["BACKUP_FAILED", "PERMISSION_DENIED"]
      #     side_effects: ["creates backup files", "logs backup operations"]
      # === /OmniNode:Metadata ===
      ```
 
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
    - [ ] 80% test coverage minimum for all files
    - [ ] No hardcoded dependencies or singletons
- [x] **Node audit. Make sure all nodes match. Several are missing contracts. That should fail the parity node test. we should consider .onextrees for all nodes which could also be emitted during introspection and use that to test node homogeniaty**
    - **DoD:** All nodes have required manifests and pass parity validation
    - **Artifact:** Complete node.onex.yaml manifests for all 7 nodes
    - **Status:** ✅ **COMPLETED** - Added missing node.onex.yaml manifest for schema_generator_node. All 7 nodes now have required manifests. Parity validator shows 35 passed validations with SUCCESS status.
- [ ] **Naming convention audit for all files**
    - **DoD:** All files follow canonical naming conventions with proper prefixes
    - **Artifact:** Renamed files and updated imports
    - **Status:** 🔄 **IN PROGRESS** - ✅ Phase 1 Complete: Moved 2 misplaced protocol files from fixtures/ to protocol/. Next: Fix missing prefixes in core/ and tools/ directories.
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
- [ ] **Add/Update CI checks for naming and file size**
    - **DoD:** CI fails on non-canonical names or oversized files.
    - **Artifact:** CI config, linter rules.
- [ ] **[Optional Stretch Goal] Prototype f2n (Function-to-Node) and node_announce event schema**
    - **DoD:** Minimal f2n utility and event schema defined; see docs/future_enhancements.md for spec.
    - **Artifact:** Prototype code, event schema, and documentation.

### Deferred Items
- [ ] Reducer snapshot test (deferred)
    - **Note:** Deferred until reducer protocol is fully specified in M2. See `tests/protocol/test_reducer_snapshot.py` for stub.

---
### 🔍 Additional Audit Checklist (Final Pass Before Milestone 1 Completion)

- [ ] Conduct full audit of ONEX coding standards:
  - Naming conventions
  - ABC inheritance usage
  - Required type annotations
  - Enum usage instead of literals
- [ ] Verify all file-level metadata (`OmniNode:Metadata`) includes:
  - Valid `uuid`, `hash`, and `namespace`
  - Accurate `entrypoint`, `meta_type`, and `description`
  - Lifecycle set correctly (`active`, `archived`, etc.)
- [ ] Confirm all `node.onex.yaml` manifests include:
  - Full runtime configuration (`dependencies`, `environment`, `state_contract`)
  - Canonical metadata and tags
  - Complete node schema alignment
- [ ] Run CI parity validator and verify:
  - Metadata hashes match stamped content
  - CLI parity and validation tests pass across nodes
- [ ] Validate directory layout:
  - All runnable nodes live in `src/omnibase/nodes/`
  - Helper files reside in clearly scoped `helpers/` directories
- [ ] Run final linter/type checks:
  - `ruff`, `mypy`, `yamllint`, `black` if applicable
  - No warnings or untyped public methods
- [ ] Confirm final commit includes updated `README.md` or docs if directory changes were made
- [ ] Replace all hardcoded strings with enums, constants or modelproperty.value 

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
