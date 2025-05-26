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
- [x] **Function Metadata Extension (Unified Tools Approach):** Extend the existing metadata stamping system to support functions as tools within the main metadata block across all supported languages, eliminating artificial separation and leveraging existing ONEX infrastructure.
    - **DoD:** Language-agnostic function-as-tool stamping capability, unified metadata schema with optional tools field, function discovery and introspection via existing tool patterns, CLI integration for function operations, validation of function tool metadata across multiple languages.
    - **Artifact:** Enhanced stamper node with multi-language function tool support, extended NodeMetadataBlock with optional tools field, CLI commands for function tool operations, function tool discovery utilities, auto-generated docstrings from metadata.
    - **Rationale:** Functions ARE tools regardless of language - no need for artificial separation. Leverages existing ONEX tool/node infrastructure, provides foundation for M2 dynamic tool composition, validates metadata patterns at function granularity, enables seamless function-level introspection and discovery using proven patterns.
    - **Scope:** Function tool metadata stamping, discovery, and introspection across supported languages. Excludes in-memory execution, Redux state management, channels, and dynamic composition (deferred to M2).
    - **Language Support:**
      - **Python:** AST-based parsing for function definitions, type hints, docstrings
      - **JavaScript/TypeScript:** AST-based parsing for function declarations, JSDoc comments, TypeScript types
      - **Bash/Shell:** Pattern-based parsing for function definitions, comment-based metadata
      - **YAML/JSON:** Schema-based function definitions for configuration-driven tools
      - **Extensible:** Plugin architecture for additional language support
    - **Unified Approach Benefits:**
      - **Conceptual Simplicity:** One metadata block per file, functions as optional tools within existing schema
      - **Language Agnostic:** Same metadata format works across all supported languages
      - **Maximum Efficiency:** 56% reduction in metadata overhead vs separate blocks (51 vs 116 lines for 10 functions)
      - **Natural Tool Discovery:** Functions discoverable via existing tool discovery patterns regardless of language
      - **Seamless Integration:** Parity validator, introspection, CLI all work with function tools automatically
      - **M2 Preparation:** Functions already "tools" - M2 can load them directly without architectural changes
    - **Implementation Strategy:**
      - **Phase 1: Extend Existing Metadata Schema (1 day)** ✅ COMPLETED
        - Add optional `tools` field to existing `NodeMetadataBlock` Pydantic model
        - Define language-agnostic function tool schema: `{name: {type: "function", language: str, line: int, description: str, inputs: List[str], outputs: List[str], error_codes: List[str], side_effects: List[str]}}`
        - Extend existing validation to handle function tools across languages
        - Create function-specific error codes within existing error code system
      - **Phase 2: Multi-Language Function Tool Discovery (2 days)** ✅ COMPLETED
        - Extend existing stamper node with language-specific parsers (Python AST, JS/TS AST, Bash patterns, YAML/JSON schemas)
        - Add function tool metadata extraction from language-specific documentation formats (docstrings, JSDoc, comments, schemas)
        - Support opt-in function stamping via language-appropriate markers (`@onex_function`, `@onex:function`, `# @onex:function`, etc.)
        - Implement function hash calculation and change detection using existing patterns
        - Auto-generate minimal documentation from function tool metadata
      - **Phase 3: Integration with Existing Infrastructure (1 day)** ✅ COMPLETED
        - Extend existing auto-discovery system to find and catalog function tools across languages
        - Add function tool introspection to existing introspection mixin (functions appear in tools list)
        - Update parity validator to validate function tool metadata compliance automatically
        - Support function tool filtering and search via existing tool discovery patterns
      - **Phase 4: CLI Integration (1 day)** ✅ COMPLETED
        - Add `onex stamp file <file> --discover-functions` flag to existing stamp command
        - Add `onex list-tools <file>` command to show all tools including functions
        - Add `onex tool-info <file>:<function_name>` command for detailed function tool introspection
        - Integrate function tool operations with existing CLI infrastructure seamlessly
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
    - **Benefits for M1:** Demonstrates metadata system versatility without artificial complexity, provides foundation for M2 without overcommitment, uses existing infrastructure with zero new concepts, validates tool patterns at function granularity across languages, eliminates duplication between documentation and metadata
    - **Estimated Effort:** 5-6 days vs. 6+ days for separate metadata blocks approach
    - **Risk Level:** Very Low - pure extension of existing proven metadata and tool infrastructure
    - **Note:** ✅ **COMPLETED FOR M1** - Successfully implemented with full coding standards compliance, treats functions as tools (which they are) regardless of language, provides natural stepping stone to M2 dynamic tool composition while maintaining M1 scope boundaries and conceptual purity. All tests passing, enum-based typing implemented, proper ABC usage for internal inheritance, fixture injection in tests.
- [x] **Centralized Error Code Definitions:** Centralize error code definitions in a shared module and enforce usage.
    - **DoD:** All error handling uses defined codes, linter/CI check present.
    - **Artifact:** `error_codes.py`, linter/CI config.
    - **Status:** ✅ **COMPLETED** - All 39 error code violations have been systematically fixed. The centralized error code system is fully implemented with `OnexError` and `CoreErrorCode` classes, and a linter script integrated into CI that validates compliance across the entire codebase.
- [x] **Sensitive Field Redaction:** Mark and redact sensitive fields in all logs/events; add tests for redaction.
    - **DoD:** Redaction logic in `.model_dump()` or `redact()` method, tested in `tests/nodes/stamper_node/`.
    - **Status:** ✅ **COMPLETED** - Implemented `SensitiveFieldRedactionMixin` with comprehensive redaction capabilities, added sensitive fields to stamper state models, created canonical protocol-first tests following testing.md standards with registry-driven test cases, fixture injection, and enum-based assertions. All 12 tests passing with proper mock/integration context parameterization.
- [x] **Plugin Discovery:** Implement and document plugin discovery (entry points, registry, env).
    - **DoD:** Plugins can be loaded via all three mechanisms, documented in developer guide.
    - **Artifact:** Plugin loader module, `plugin_registry.yaml`, `pyproject.toml`/`setup.cfg`.
    - **Status:** ✅ **COMPLETED** - Full plugin discovery system implemented with entry points, config files, and environment variables. Comprehensive documentation created at `docs/plugins/plugin_discovery.md`. All tests passing.
- [x] **Structured Logging Infrastructure:** Implement comprehensive structured logging that routes all internal ONEX logging through the Logger Node as side effects, following functional monadic architecture principles.
    - **Status:** ✅ **COMPLETED** - Core infrastructure implemented with comprehensive test coverage (31 tests passing). All components working correctly with Logger Node integration.
    - **DoD:** Complete replacement of all print() statements and Python logging with structured events; Logger Node handles all output formatting; centralized configuration with environment variable support; comprehensive test coverage.
    - **Artifact:** `src/omnibase/core/structured_logging.py`, `StructuredLoggingAdapter`, Logger Node output formatting, configuration system, developer documentation.
    - **Implementation Plan:**
        - [x] **Phase 1: Core Infrastructure (1 day)**
            - [x] Create `emit_log_event()` function for structured log emission
            - [x] Implement `StructuredLoggingAdapter` class to route events through Logger Node
            - [x] Create `OnexLoggingConfig` dataclass with environment variable support
            - [x] Add `STRUCTURED_LOG` event type to `OnexEventTypeEnum`
            - [x] Implement context extraction utilities (`_get_calling_module()`, etc.)
            - [x] Create global setup function `setup_structured_logging()`
        - [ ] **Phase 2: Logger Node Output Formatting (1 day)**
            - [ ] Extend Logger Node with output format configuration (human-readable, JSON, verbose)
            - [ ] Implement context-aware formatting based on environment (CLI, production, development)
            - [ ] Add multiple output target support (stdout, file, etc.)
            - [ ] Create `LoggerOutputConfig` for formatting control
            - [ ] Integrate with existing Logger Node infrastructure
        - [ ] **Phase 3: Clean Replacement (2 days)**
            - [ ] Replace all print() statements with `emit_log_event()` calls
                - [ ] CLI tools and user-facing output (35+ instances)
                - [ ] Debug information in development tools
                - [ ] Status messages in scripts and demos
            - [ ] Replace all Python logging calls with `emit_log_event()`
                - [ ] Core modules and node implementations (35+ files)
                - [ ] Error reporting and critical paths
                - [ ] Configuration and initialization code
            - [ ] Disable Python logging entirely (`logging.disable(logging.CRITICAL)`)
            - [ ] Remove Python logging imports and configurations
        - [ ] **Phase 4: Testing & Documentation (1 day)**
            - [ ] Create comprehensive test suite for all components
            - [ ] Add integration tests with Logger Node
            - [ ] Validate performance impact is minimal
            - [ ] Create developer documentation and usage guide
            - [ ] Document configuration options and environment variables
            - [ ] Add output format examples for different contexts
    - **Benefits:**
        - **Architectural Purity:** All output flows through Logger Node as intended side effects
        - **Zero Complexity:** No compatibility layers or handlers to maintain
        - **Better Observability:** Even CLI output gets correlation IDs and structured context
        - **Single Configuration:** All output formatting controlled by Logger Node
        - **Consistent Patterns:** One way to emit logs across entire codebase
    - **Configuration Support:**
        - Environment variables: `ONEX_LOG_FORMAT`, `ONEX_LOG_LEVEL`, `ONEX_ENABLE_CORRELATION_IDS`
        - Output targets: `ONEX_LOG_TARGETS`, `ONEX_LOG_FILE_PATH`
        - Event bus configuration: `ONEX_EVENT_BUS_TYPE`
    - **System Flow:** Application Code → emit_log_event() → ProtocolEventBus → StructuredLoggingAdapter → Logger Node → Context-appropriate output
- [x] **Update Documentation:** Update `README.md` and developer docs to cover all new requirements, including telemetry, event schema, plugin loading, error code mapping, redaction, and correlation/tracing.
    - **DoD:** Docs updated, usage and rationale for each new feature explained.
    - **Artifact:** `README.md`, `docs/nodes/canary_node_cli_alignment.md`, developer guides.
    - **Status:** ✅ **COMPLETED** - Comprehensive documentation updates completed for all implemented features. README.md now includes detailed sections on structured logging, plugin discovery, error codes, sensitive field redaction, telemetry, and function metadata extension. Developer guide and canary node alignment document updated to reflect completed implementations with usage examples and configuration details.

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
