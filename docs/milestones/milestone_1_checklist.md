<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: milestone_1_checklist.md
version: 1.0.0
uuid: dd263972-9b84-46c1-ae8c-7b642d62c839
author: OmniNode Team
created_at: '2025-05-28T12:40:26.539104'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://milestone_1_checklist
namespace: markdown://milestone_1_checklist
meta_type: tool

<!-- === /OmniNode:Metadata === -->

# Milestone 1 Implementation Checklist: ONEX Node Protocol, Schema, Metadata, and CI Enforcement

## 🔁 RECOMMENDED EXECUTION PLAN (Refactor-Minimizing Order)

The following sequence is optimized to minimize refactor overhead and test breakage, based on the current state of architecture, typing debt, and test coverage (682 tests as of review).

### 1. Phase 0: Fix All Architecture Violations (Blocking)
- Freeze all typing and test changes until these are resolved.
- Address critical violations across `core/`, `shared models/`, `cli/`, and `runtimes/`.
- Validate fix with parity validator and CI.


- [ ] **Event-Driven Node Discovery and Registry Node (CRITICAL)**
    - [x] **Define Node Announcement Protocol**
        - Specify the event schema for `node_announce` messages (required fields: node_id, metadata_block, status, execution_mode, inputs, outputs, graph_binding, etc.).
        - Add protocol documentation and canonical example to core/protocol.
        - **DoD:** Protocol and schema for node_announce event are defined and documented in core.
    - [x] **Refactor Core for Protocol Purity**
        - Remove all runtime/node imports and discovery logic from core (e.g., no `RuntimeHandlerDiscovery` import).
        - Require all handler/node discovery to occur via event-driven registration or plugin mechanisms.
        - **DoD:** Core contains only protocol definitions and abstract interfaces; no runtime/node dependencies.
    - [x] **Implement CollectorNode (Registry Node) in Runtime/Nodes**
        - Scaffold a CollectorNode that subscribes to the event bus and maintains a live registry of all nodes (ephemeral and persistent).
        - CollectorNode must handle node_announce events, maintain node status, and provide lookup for agents/schedulers.
        - **DoD:** CollectorNode is implemented as a runtime/node service, not in core; can receive and track node_announce events.
    - [~] **Document Event-Driven Registration Pattern**
        - Update developer documentation to require all nodes (including ephemeral/function-wrapped) to emit node_announce on startup.
        - Provide migration guidance for moving from static to event-driven registration.
        - **DoD:** Documentation and migration guide are published.

- [ ] **Core Layer Architecture Violations (CRITICAL)**
    - [x] **core_file_type_handler_registry.py** - Remove imports of specific runtime handlers (lines 37-50)
    - [x] **core_structured_logging.py** - Remove import of `omnibase.nodes.logger_node.v1_0_0.models.state` (line ~175)
        - No such import present; file is already protocol-pure.
    - [ ] **Action Required:** 
      - Implement plugin-based discovery pattern for handlers
      - Use dependency injection for logger state access
      - Core layer must only define protocols and abstract base classes
    - **DoD:** Core layer has zero imports from nodes/ or runtimes/
    - **Priority:** BLOCKING - affects all downstream functionality
    - **Estimated Effort:** 2-3 days

- [x] **Shared Model Architecture Violations (CRITICAL)**
    - [x] **model_node_metadata.py** - Remove import of omnibase.nodes.stamper_node.v1_0_0.node_tests.stamper_test_registry_cases (line 888)
    - [x] **Action Required:**
      - Move test registry cases to shared test infrastructure
      - Use dependency injection pattern for test case access
      - Shared models must not import from specific nodes
    - **DoD:** All shared models have zero imports from nodes/
    - **Priority:** BLOCKING - affects metadata handling across ecosystem
    - **Estimated Effort:** 1-2 days

- [ ] **CLI Infrastructure Architecture Violations (CRITICAL)**
    - [ ] **cli_main.py** - Remove hardcoded `stamper_node@v1_0_0` registry entry
    - [ ] **cli_main_new.py** - Remove imports of `omnibase.nodes.cli_node.v1_0_0.*`
    - [ ] **commands/run_node.py** - Remove hardcoded NODE_REGISTRY with specific node paths
    - [ ] **commands/fix_node_health.py** - Remove import of `omnibase.nodes.node_manager_node.v1_0_0.helpers.helpers_maintenance`
    - [ ] **Action Required:**
      - Implement dynamic node discovery via registry pattern
      - Remove all hardcoded node references from CLI infrastructure
      - CLI should only define interfaces and discovery mechanisms
    - **DoD:** CLI infrastructure has zero hardcoded node references
    - **Priority:** BLOCKING - affects all CLI functionality and user experience
    - **Estimated Effort:** 3-4 days

- [ ] **Runtime Handler Architecture Violations (CRITICAL)**
    - [ ] **handlers/handler_metadata_yaml.py** - Remove import of `omnibase.nodes.stamper_node.v1_0_0.helpers.metadata_block_normalizer`
    - [ ] **handlers/handler_python.py** - Remove import of `omnibase.nodes.stamper_node.v1_0_0.helpers.metadata_block_normalizer`
    - [ ] **handlers/handler_markdown.py** - Remove import of `omnibase.nodes.stamper_node.v1_0_0.helpers.metadata_block_normalizer`
    - [ ] **mixins/mixin_metadata_block.py** - Remove import of `omnibase.nodes.stamper_node.v1_0_0.helpers.hash_utils`
    - [ ] **Action Required:**
      - Move shared functionality from stamper_node helpers to runtime or core
      - Implement shared utility registry for metadata block operations
      - Runtime layer must not depend on specific node implementations
    - **DoD:** Runtime handlers have zero imports from nodes/
    - **Priority:** BLOCKING - affects all file processing and metadata operations
    - **Estimated Effort:** 2-3 days

- [ ] **Handler Misplacement (MAJOR)**
    - [ ] **handlers/handler_ignore.py** - Move to runtimes/onex_runtime/v1_0_0/handlers/ and refactor to use strongly typed models for all handler methods (no Any, tuple returns, or untyped context).
    - [ ] **Action Required:**
      - Move specific implementation to runtime directory
      - Update imports and registry references
      - handlers/ should contain only base classes, protocols, and mixins
    - **DoD:** handlers/ contains only shared abstractions
    - **Priority:** HIGH - affects handler architecture consistency
    - **Estimated Effort:** 0.5 days

- [ ] **handlers/block_placement_mixin.py** - Refactor to use strongly typed models for policy parameter and remove Any usage.

### 2. Phase 1: Enums and Core Result Models
- Implement missing Enums and Result Models before touching broader typing.
- This enables consistent replacement of `Dict[str, Any]` and magic literals in protocol and infrastructure layers.

- [ ] **Create Missing Enums and Constants**
  - [ ] **HandlerSourceEnum** for `"core"`, `"runtime"`, `"node-local"`, `"plugin"` string literals
  - [ ] **HandlerTypeEnum** for `"extension"`, `"special"`, `"named"` string literals  
  - [ ] **HandlerPriorityEnum** for magic numbers (0, 10, 50, 75, 100)
  - [ ] **StatusEnum** for various status fields using string literals
  - [ ] **Constants module** for remaining magic numbers and strings
  - **DoD:** All string literals for fixed option sets use enums
  - **Priority:** BLOCKING - required for all other typing fixes
  - **Estimated Effort:** 2-3 days

- [ ] **Create Missing Result Models**
  - [ ] **HandlerInfoModel** to replace `Dict[str, Any]` in registry
  - [ ] **ExtractBlockResult** for handler extract operations (replace tuple returns)
  - [ ] **SerializeBlockResult** for handler serialize operations (replace string returns)
  - [ ] **CapabilityResult** for can_handle operations (replace bool returns)
  - [ ] **HandlerMetadata** for typed metadata instead of `Dict[str, Any]`
  - **DoD:** All protocol methods return typed models instead of primitives
  - **Priority:** BLOCKING - required for protocol compliance
  - **Estimated Effort:** 2-3 days

### 3. Phase 2: Typing Refactor by Subsystem (With Tests)
Execute the following in order, ensuring each subsystem has 80%+ coverage and all tests passing:
- Core infrastructure
- CLI infrastructure
- Runtime handlers
- Models
- Mixins and utilities

For each:
- Refactor types
- Update all dependent tests
- Achieve minimum 80% coverage
- Confirm parity validator passes

- [ ] **SYSTEMATIC TYPING VIOLATIONS REVIEW AND REMEDIATION (COMPREHENSIVE)**
    - [ ] **Phase 1: Review ALL Files from Standards Inventory (Week 1)**
      - [ ] **Top-level files** (3 files) - Review for Dict[str, Any], string literals, magic numbers
      - [ ] **metadata/** (1 file) - Review metadata_constants.py for enum usage
      - [ ] **core/** (6 files) - Review all core files for typing violations
      - [ ] **enums/** (9 files) - Verify all enums are properly used throughout codebase
      - [ ] **handlers/** (3 files) - Review for typing compliance
      - [ ] **model/** (33 files) - Comprehensive review of all model files for Dict usage
      - [ ] **fixtures/** (7 files) - Review fixture files for typing violations
      - [ ] **mixin/** (8 files) - Review all mixin files for typing compliance
      - [ ] **protocol/** (30+ files) - Review all protocol files for primitive returns
      - [ ] **templates/** (11 files) - Review template files for typing patterns
      - [ ] **schemas/** (23+ files) - Review schema files for typing compliance
      - [ ] **cli_tools/** (15+ files) - Review all CLI files for string literals and Dict usage
      - [ ] **runtimes/** (50+ files) - Review runtime files for typing violations
      - [ ] **utils/** (9 files) - Review utility files for typing compliance
      - **DoD:** Every file in standards inventory reviewed and violations documented
      - **Priority:** CRITICAL - establishes complete scope of typing work
      - **Estimated Effort:** 5-7 days for comprehensive review

    - [ ] **Phase 2: Fix Critical Infrastructure Typing (Week 2)**
      - [ ] **core_file_type_handler_registry.py** - Replace string literals with enums, Dict[str, Any] with models
        - Replace `source: str` parameters with `HandlerSourceEnum`
        - Replace `list_handlers()` return type with `List[HandlerInfoModel]`
        - Replace magic priority numbers with `HandlerPriorityEnum`
        - Replace handler type strings with `HandlerTypeEnum`
      - [ ] **core_structured_logging.py** - Replace Dict[str, Any] with typed event models
        - Replace event metadata dictionaries with typed models
        - Use `LogLevelEnum` consistently throughout
        - Replace magic strings with named constants
      - [ ] **protocol_file_type_handler.py** - Update protocol to return models instead of primitives
        - Replace `extract_block() -> tuple` with `-> ExtractBlockResult`
        - Replace `serialize_block() -> str` with `-> SerializeBlockResult`
        - Replace `can_handle() -> bool` with `-> CapabilityResult`
      - [ ] **protocol_handler_discovery.py** - Use typed models for metadata and enums for source
        - Replace `Dict[str, Any]` metadata with `HandlerMetadata` model
        - Replace string source with `HandlerSourceEnum`
        - Replace magic priority numbers with `HandlerPriorityEnum`
      - **DoD:** Core infrastructure has zero Dict[str, Any] usage and zero string literals for enums
      - **Priority:** CRITICAL - affects all downstream code
      - **Estimated Effort:** 3-4 days

    - [ ] **Phase 3: Fix CLI Infrastructure Typing (Week 3)**
      - [ ] **cli_main.py** - Replace hardcoded registry access with enum-based keys
        - Create `KnownNodeEnum` for node references
        - Replace `NODE_CLI_REGISTRY["stamper_node@v1_0_0"]` with enum-based access
        - Replace string literals for log levels with `LogLevelEnum`
        - Replace magic strings for command names with constants
      - [ ] **commands/list_handlers.py** - Replace Dict[str, Any] with HandlerInfoModel
        - Replace handler info dictionaries with `HandlerInfoModel`
        - Use `OutputFormatEnum` for format types ("table", "json", "summary")
        - Use `HandlerSourceEnum` for source filters
        - Use `HandlerTypeEnum` for type filters
      - [ ] **All CLI command files** - Update to use proper enums and models
        - Replace string literals with appropriate enums
        - Use typed models for command results
        - Replace magic strings with named constants
      - **DoD:** CLI infrastructure uses enums for all fixed option sets
      - **Priority:** HIGH - affects user experience and maintainability
      - **Estimated Effort:** 2-3 days

    - [ ] **Phase 4: Fix Runtime Handler Typing (Week 4)**
      - [ ] **runtime_handler_discovery.py** - Use enums and models instead of literals
        - Replace `source="runtime"` with `HandlerSourceEnum.RUNTIME`
        - Replace magic priority numbers with `HandlerPriorityEnum`
        - Replace `Dict[str, str]` metadata with `HandlerMetadata` model
      - [ ] **All handler implementations** - Update to use new protocol return types
        - Update all handlers to return `ExtractBlockResult` instead of tuples
        - Update all handlers to return `SerializeBlockResult` instead of strings
        - Update all handlers to return `CapabilityResult` instead of bools
      - [ ] **Handler mixins** - Update to use typed models
        - Replace Dict[str, Any] usage with specific typed models
        - Use enums for string literals in mixins
      - **DoD:** Runtime handlers comply with typed protocol interfaces
      - **Priority:** HIGH - affects all file processing operations
      - **Estimated Effort:** 3-4 days

    - [ ] **Phase 5: Fix Model File Typing (Week 5)**
      - [x] **model_node_metadata.py** - Replace Dict usage with typed models (combine with file size refactoring)
        - Replace `IOContract.inputs: Dict[str, str]` with `List[IOParameter]`
        - Replace `IOContract.outputs: Dict[str, str]` with `List[IOParameter]`
        - Replace `SignatureContract.parameters: Dict[str, str]` with typed model
        - Replace string literals for status/type fields with enums
      - [ ] **model_file_filter.py** - Fix remaining Dict usage
        - Replace `skipped_file_reasons: Dict[Path, str]` with typed model
        - Use enums for reason codes
      - [ ] **All other model files** - Audit and fix remaining Dict[str, Any] usage
        - Replace generic dictionaries with specific typed models
        - Ensure all enum fields use proper enum types
        - Fix any remaining string literals that should be enums
      - **DoD:** All model files use strongest possible typing with no Dict[str, Any] for domain data
      - **Priority:** MEDIUM - can be combined with file size refactoring
      - **Estimated Effort:** 2-3 days (combined with refactoring)

    - [ ] **Phase 6: Fix Utility and Mixin Typing (Week 6)**
      - [ ] **directory_traverser.py** - Replace Dict usage and magic numbers (combine with file size refactoring)
        - Replace configuration dictionaries with typed models
        - Use constants for magic numbers (file sizes, buffer sizes)
        - Use enums for status values and traversal modes
      - [ ] **mixin_introspection.py** - Replace Dict[str, Any] with typed models
        - Replace field extraction dictionaries with typed models
        - Use enums for field types and status values
        - Replace magic strings with constants
      - [ ] **centralized_fixture_registry.py** - Fix Dict usage in fixture handling
        - Replace `fixture_data: dict` with typed fixture models
        - Replace `case_data: dict` with typed case models
        - Use enums for fixture types and formats
      - [ ] **All utility files** - Complete typing compliance review
        - Replace any remaining Dict[str, Any] usage
        - Use enums for string literals
        - Use constants for magic numbers
      - **DoD:** All utility and mixin files use strongest possible typing
      - **Priority:** MEDIUM - can be done in parallel with other work
      - **Estimated Effort:** 2-3 days

    - [ ] **Phase 7: Validation and Testing (Week 7)**
      - [ ] **Run mypy with strict typing** to verify all changes
        - Enable strict mode: `mypy --strict src/`
        - Fix all type errors revealed by strict checking
        - Ensure 100% mypy compliance across codebase
      - [ ] **Update all tests** to use new models and enums
        - Replace Dict[str, Any] usage in test assertions
        - Use new typed models in test fixtures
        - Update test data to use enums instead of string literals
      - [ ] **Validate with parity_validator_node** for ecosystem compliance
        - Run comprehensive validation after typing changes
        - Ensure all nodes still pass validation
        - Fix any typing-related validation failures
      - [ ] **Create comprehensive typing standards documentation**
        - Create typing standards guide with examples and patterns
        - Document migration patterns for common violations
        - Create best practices guide for new code
      - [ ] **Add CI checks** to enforce typing standards for new code
        - Add mypy strict checking to CI pipeline
        - Add linting rules to catch typing violations
        - Add pre-commit hooks for typing compliance
      - **DoD:** 100% mypy compliance with strict typing enabled, comprehensive documentation
      - **Priority:** FINAL - validates all typing improvements
      - **Estimated Effort:** 2-3 days

    - [ ] **TYPING VIOLATIONS SUMMARY (Based on Systematic Review - IN PROGRESS)**
      - [ ] **CONFIRMED VIOLATIONS FOUND:**
        - [ ] **conftest.py** - Uses `Any` type annotations, magic constants (MOCK_CONTEXT = 1, INTEGRATION_CONTEXT = 2)
        - [ ] **core_error_codes.py** - Uses `Dict[OnexStatus, CLIExitCode]` mapping, could use typed registry
        - [ ] **core_function_discovery.py** - Returns `Dict[str, FunctionTool]` (should be typed model), uses string literals for language matching
        - [ ] **core_plugin_loader.py** - Uses `Dict[str, PluginMetadata]` and `Dict[str, Any]` for plugin storage, magic strings for plugin keys
        - [ ] **core_structured_logging.py** - Uses `Dict[str, Any]` for metadata and context, string literals for log levels and event types
        - [ ] **directory_traverser.py** - Uses magic numbers (5 * 1024 * 1024), `Dict` usage in configuration, string literals for traversal modes
        - [ ] **centralized_fixture_registry.py** - Uses `dict` type annotations for `fixture_data` and `case_data` parameters
        - [ ] **mixin_introspection.py** - Uses `Dict[str, List]` and `Any` type annotations, string literals for field types
        - [ ] **block_placement_mixin.py** - Uses `Any` type annotation for policy parameter, no type safety
        - [ ] **model_file_filter.py** - Uses `Dict[Path, str]` for `skipped_file_reasons` (should be typed model)
        - [ ] **list_handlers.py** - Uses `Dict[str, Dict[str, Any]]` for handler storage, string literals for format types
        - [ ] **handler_markdown.py** - Returns `tuple[Optional[NodeMetadataBlock], Optional[str]]` (violates protocol), uses `Any` for default parameters
        - [ ] **mixin_metadata_block.py** - Uses `dict[str, Any]` extensively, `Any` type annotations, imports from stamper_node (architecture violation)
        - [ ] **protocol_validate.py** - Uses `Any` type annotation for logger and config parameters
        - [ ] **model_context.py** - Uses `Dict[str, str]` for data field (should be typed model for domain-specific data)
        - [ ] **model_handler_config.py** - Uses string literals for `processing_category` field (should be enum)
        - [ ] **run_node.py** - Hardcoded `NODE_REGISTRY: Dict[str, tuple[str, str, Any]]` with magic strings
        - [ ] **handler_python.py** - Returns `tuple[Optional[Any], str]` from `extract_block()` (violates protocol)
        - [ ] **protocol_directory_traverser.py** - Returns `Union[OnexResultModel, List[T]]` (inconsistent return types)
      - [ ] **SYSTEMATIC REVIEW STATUS:**
        - [x] **Top-level files** (3/3) - ✅ __init__.py compliant, ❌ conftest.py has violations, ✅ exceptions.py compliant
        - [x] **metadata/** (1/1) - ✅ metadata_constants.py reviewed (compliant - uses proper constants)
        - [ ] **core/** (5/6) - ❌ core_error_codes.py, ❌ core_function_discovery.py, ❌ core_plugin_loader.py, ❌ core_structured_logging.py reviewed, 1 more file needs review
        - [x] **enums/** (1/9) - ✅ metadata.py reviewed (compliant - proper enum definitions), 8 more files need review
        - [ ] **handlers/** (1/3) - ❌ block_placement_mixin.py reviewed, 2 more files need review
        - [ ] **model/** (5/33) - ❌ model_handler_config.py, ❌ model_file_filter.py, ❌ model_context.py, ✅ model_base_error.py, ✅ model_log_entry.py reviewed, 28 more need review
        - [ ] **fixtures/** (1/7) - ❌ centralized_fixture_registry.py reviewed, 6 more files need review
        - [ ] **mixin/** (1/8) - ❌ mixin_introspection.py reviewed, 7 more files need review
        - [ ] **protocol/** (4/30+) - ❌ protocol_directory_traverser.py, ❌ protocol_validate.py, ✅ protocol_event_bus.py, ✅ protocol_stamper.py reviewed, 26+ more need review
        - [ ] **templates/** (0/11) - All template files need review
        - [ ] **schemas/** (0/23+) - All schema files need review
        - [ ] **cli_tools/** (2/15+) - ❌ run_node.py, ❌ list_handlers.py reviewed, 13+ more files need review
        - [ ] **runtimes/** (3/50+) - ❌ handler_python.py, ❌ handler_markdown.py, ❌ mixin_metadata_block.py reviewed, 47+ more files need review
        - [ ] **utils/** (1/9) - ❌ directory_traverser.py reviewed, 8 more files need review
      - [ ] **REVIEW COMPLETION:** 24/200+ files reviewed (12% complete)
      - [ ] **VIOLATIONS FOUND:** 18/24 files reviewed have typing violations (75% violation rate)
      - [ ] **PATTERN ANALYSIS:**
        - [ ] **Dict[str, Any] violations:** Found in 12+ files (most common violation)
        - [ ] **String literal violations:** Found in 10+ files (should use enums)
        - [ ] **Magic number violations:** Found in 5+ files (should use constants)
        - [ ] **Protocol return type violations:** Found in 4+ files (primitive returns instead of models)
        - [ ] **Any type annotation violations:** Found in 8+ files (should use specific types)
      - [ ] **ESTIMATED SCOPE BASED ON SAMPLE:**
        - [ ] **Total files with violations:** ~150 files (75% of 200+ files)
        - [ ] **Dict[str, Any] replacements needed:** ~100 files
        - [ ] **String literal to enum conversions:** ~80 files
        - [ ] **Protocol signature updates:** ~20 files
        - [ ] **New enums required:** ~25 enum types
        - [ ] **New models required:** ~15 model types
      - [ ] **ESTIMATED REMAINING WORK:** 176+ files still need systematic review
      - [ ] **CRITICAL PATH:** Complete systematic review before implementing fixes
      - [ ] **NEXT ACTIONS:** Continue systematic review of all remaining files in inventory

### 4. Phase 3: Canary File Lock-In and Metadata Enforcement
- Nominate and validate Canary files for all supported extensions.
- Run Canary validation before any batch stamping.
- Re-stamp metadata only after type system and architecture are locked.

- [ ] **Outdated Metadata Format**
    - [ ] **metadata_constants.py** - Re-stamp with current stamper to fix missing protocol_version, owner, copyright fields
    - [ ] **Action Required:** Run stamper on file to update to current metadata format
    - **DoD:** All metadata follows current format standards
    - **Priority:** MEDIUM - affects metadata consistency
    - **Estimated Effort:** 0.5 days

- [ ] **Canary File Safeguard for Stamping Operations**
    - [ ] Select and nominate one real, protocol-compliant file for each handled extension (Markdown, Python, YAML) as Canary files.
    - [ ] Before any batch stamping run, run the stamper on all Canary files and immediately validate them using the parity validator node (protocol-first, --verbose or --format json).
    - [ ] If any Canary file fails validation, abort the batch operation and emit a protocol-compliant error with diagnostic output. Do not proceed to batch stamping.
    - [ ] Update Canary file set as new filetypes are added (automate via handler registry if possible).
    - [ ] Log and document all Canary check results for auditability and include rationale in developer documentation.
    - **Rationale:** Prevents catastrophic batch corruption by surfacing protocol/handler/serialization errors early, before they can affect the entire codebase. Ensures protocol compliance and safety for all supported filetypes.

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

- [ ] **Node audit. Make sure all nodes match. Several are missing contracts. That should fail the parity node test. we should consider .onextrees for all nodes which could also be emitted during introspection and use that to test node homogeniaty**
    - **DoD:** All nodes have required manifests and pass parity validation
    - **Artifact:** Complete node.onex.yaml manifests for all 7 nodes
    - **Status:** ✅ **COMPLETED** - Added missing node.onex.yaml manifest for schema_generator_node. All 7 nodes now have required manifests. Parity validator shows 35 passed validations with SUCCESS status.
- [ ] **Naming convention audit for all files**
    - **DoD:** All files follow canonical naming conventions with proper prefixes
    - **Artifact:** Renamed files and updated imports
    - **Remaining Actions:**
      - Fix architecture violations first (affects imports and dependencies)
      - Address file size violations (may affect naming during splits)
      - Verify nodes/ directory contains only node-specific code
      - Update any remaining files with missing prefixes after refactoring
    - **Priority:** MEDIUM - address after architecture violations resolved
    - **Estimated Effort:** 1-2 days

### 5. Phase 4: Test Suite Canonicalization (All Layers)
- Split test types: node-local, handler, integration.
- Remove all hardcoded domain values, replace with model-driven fixtures and registries.
- Ensure all serialization/parsing uses handler registry.
- Validate edge cases and malformed inputs with protocol logic.

- [ ] **Test Case Requirements and Expected Results in Fixtures**
    - [ ] All test case/fixture definitions must include not only scenario setup but also the expected result(s) or requirements for each case.
    - [ ] Test logic must be generic and data-driven: it must load the scenario, run the code under test, and compare the actual result to the expected result from the fixture.
    - [ ] No expected results or requirements may be hardcoded in test logic; all must be defined in the test case data.
    - [ ] CI should validate that all test cases have expected results defined.
    - **Rationale:** Centralizes requirements, improves traceability, enables easier auditing and extension of test coverage, and ensures all test logic is requirements-driven.

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

### 6. Phase 5: CI and Enforcement Hardening
- Add CI checks for import violations, file size, metadata format, handler placement.
- Enforce strict mypy and canonical architecture boundaries.

- [ ] **Add/Update CI checks for naming and file size**
    - **DoD:** CI fails on non-canonical names or oversized files.
    - **Artifact:** CI config, linter rules.
    - **Enhanced Requirements Based on Standards Review:**
      - [ ] Add CI check to prevent imports from nodes/ in shared directories (core/, model/, handlers/, cli_tools/, runtimes/)
      - [ ] Add CI check to prevent hardcoded node references in CLI infrastructure
      - [ ] Add CI check to enforce 500-line file size limit with specific exceptions
      - [ ] Add CI check to validate metadata format compliance
      - [ ] Add CI check to prevent specific implementations in shared handlers/ directory
      - [ ] Add linter rules to flag architecture violations automatically
    - **Priority:** HIGH - prevents regression of architecture violations
    - **Estimated Effort:** 2-3 days (implement after architecture fixes)

### 7. Phase 6: Release Infrastructure and Final M1 Tagging
- Create stable branch, automate version tagging, changelog, RC testing.
- Final pass with parity validator, linting, and README/doc updates.
- Tag `v1.0.0` and begin M2 planning.

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

## Batch Execution Tracking

| Batch | Scope/Files | Status | Blockers/Notes |
|-------|-------------|--------|----------------|
| 1     | (list files) | Not Started |  |
| 2     | ...         |          |                |

---

### Regression/Compatibility Test After Each Batch
- [ ] After each batch:
    - [ ] Run full test suite
    - [ ] Run parity validator node
    - [ ] Record and triage any regressions or failures

---

### Architecture/Standards Review Signoff
- [ ] Final architecture and standards review signoff (see docs/milestones/milestone_standards_review.md)

---

### File Size Exception Documentation
- [ ] Document and justify any shared file >500 lines as required by standards (see docs/standards.md)

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

## NEW REWORK ITEMS FROM BATCH REVIEW:

- [x] **model_node_metadata.py** - Refactor IOContract, SignatureContract, StateContractBlock, and NodeMetadataBlock to use typed models instead of Dict[str, str] and Dict[str, Any].
- [x] **model_onex_message_result.py** - Refactor OnexResultModel and OnexMessageModel to use typed models for metadata/context fields instead of Dict[str, Any].
- [x] **model_onex_event.py** - Refactor OnexEvent to use a strongly typed model for metadata instead of Dict[str, Any].
- [x] **model_validate_error.py** - Refactor ValidateMessageModel and ValidateResultModel to use typed models for context fields instead of Dict[str, Any].
- [x] **model_node_introspection.py** - Refactor NodeMetadataModel, ContractModel, and NodeIntrospectionResponse to use typed models for version_status, performance_profile, and other Dict fields.
- [x] **fixtures/cli_stamp_fixtures.py** - Refactor CLIDirFixtureCase and CLIStampDirFixtureRegistry to use typed models for files/subdirs instead of Tuple[str, str] and List[Tuple[str, str]].
- [x] **fixtures/fixture_loader.py** - Refactor CentralizedFixtureLoader to use typed models for fixture data instead of Any/Dict.
- [x] **fixtures/centralized_fixture_registry.py** - Refactor CentralizedFixtureRegistry to use typed models for fixture cases and data instead of mocks and Any/Dict.
- [x] **fixtures/registry_adapter.py** - Refactor RegistryAdapter and MockRegistryAdapter to use strongly typed models for all registry data and artifact fields (no Dict[str, Any]).
- [x] **fixtures/mocks/dummy_schema_loader.py** - Refactor DummySchemaLoader to use strongly typed models for all return values (no dict[str, Any]).
- [x] **fixtures/mocks/dummy_handlers.py** - Refactor all dummy handler classes to use strongly typed models for all handler methods (no Any, Tuple, or Dict returns).
- [x] **protocol_file_type_handler.py** - Refactor ProtocolFileTypeHandler to require/return strongly typed models for all handler methods (no Any, Dict, or tuple returns).
- [x] **protocol_cli.py** - Refactor ProtocolCLI to use typed models for describe_flags and logger fields.
- [ ] **directory_traverser.py** - Refactor DirectoryTraverser and related models to use typed models for all configuration and result fields (no Dict, Any, or magic numbers).
- [ ] **All protocol and model files** - Audit for Any, Dict, and string literal usage and refactor to use enums and models as appropriate.
- [ ] **All fixtures and test infrastructure** - Refactor to use typed models for all test case and fixture data (no Dict, Any, or Tuple-based structures).
- [ ] **All CLI command files** - Refactor to use enums and models for all command arguments, results, and registry entries (no Dict, Any, or string literals for fixed sets).
- [ ] **All handler implementations** - Refactor to use new protocol return types and models (no tuple or primitive returns).
- [ ] **All mixins and utilities** - Refactor to use typed models and enums for all configuration and result fields.
- [ ] **mixin/event_driven_node_mixin.py** - Refactor all Dict[str, Any] and untyped event payloads to use strongly typed models for event and introspection data.
- [ ] **protocol/protocol_fixture_loader.py** - Refactor to use strongly typed models for fixture objects instead of Any in load_fixture return type.
- [ ] **protocol/protocol_node_cli_adapter.py** - Refactor to return a strongly typed model for node input state instead of Any in parse_cli_args.
- [ ] **protocol/protocol_node_runner.py** - Refactor to use a strongly typed model for node execution result instead of Any in run return type.
- [ ] **protocol/protocol_registry.py** - Refactor RegistryArtifactInfo and RegistryStatus to use Pydantic models instead of plain classes with Dict[str, Any] for metadata.
- [ ] **protocol/protocol_schema_loader.py** - Refactor load_schema_for_node to return a strongly typed model instead of dict[str, Any].
- [ ] **protocol/protocol_testable_registry.py** - Refactor get_node to return a strongly typed model instead of Dict[str, Any].
- [ ] **protocol/protocol_tool.py** - Refactor execute to accept and return strongly typed models instead of Dict[str, Any] and Any.
- [ ] **model/model_state_contract.py** - Refactor StateContractModel, StateSchemaModel, and ErrorStateModel to use strongly typed models for all properties and metadata fields (no Dict[str, Any]).
- [ ] **model/model_project_metadata.py** - Refactor ProjectMetadataBlock to use strongly typed models for tools and any Dict fields.
- [x] **model/model_schema.py** - Refactor SchemaModel to use strongly typed models for properties and required fields (no Dict[str, Any]).
