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

# NOTE: All completed tasks have been moved to docs/milestones/milestone_1_completed.md for clarity. This checklist now tracks only uncompleted and in-progress items.

## Table of Contents
- [Batch Status Table](#batch-status-table)
- [Next Actions](#next-actions)
- [B1.1: Event-Driven Node Discovery and Registry Node](#b11-event-driven-node-discovery-and-registry-node)
- [B1.2: Core Layer Architecture Violations](#b12-core-layer-architecture-violations)
- [B1.3: Shared Model Architecture Violations](#b13-shared-model-architecture-violations)
- [B1.4: CLI Infrastructure Architecture Violations](#b14-cli-infrastructure-architecture-violations)
- [B1.5: Runtime Handler Architecture Violations](#b15-runtime-handler-architecture-violations)
- [B1.6: Handler Misplacement](#b16-handler-misplacement)
- [B2.1: Create Missing Enums and Constants](#b21-create-missing-enums-and-constants)
- [B2.2: Create Missing Result Models](#b22-create-missing-result-models)

## Batch Status Table
| Batch | Scope/Files | Status | Blockers/Notes |
|-------|-------------|--------|----------------|
| B1.1  | Event-Driven Node Discovery and Registry Node | Complete | Parity validator pending |
| B1.2  | Core Layer Architecture Violations | Not Started | Blocked by B1.1 |
| B1.3  | Shared Model Architecture Violations | Not Started | Blocked by B1.2 |
| B1.4  | CLI Infrastructure Architecture Violations | Not Started | Blocked by B1.3 |
| B1.5  | Runtime Handler Architecture Violations | Not Started | Blocked by B1.4 |
| B1.6  | Handler Misplacement | Not Started | Blocked by B1.5 |
| B2.1  | Create Missing Enums and Constants | Not Started | Blocked by B1.6 |
| B2.2  | Create Missing Result Models | Not Started | Blocked by B2.1 |

## Next Actions
- [x] Complete B1.1 (Event-Driven Node Discovery and Registry Node)
- [ ] Review and start B1.2 (Core Layer Architecture Violations)
- [ ] Prepare for B1.3 (Shared Model Architecture Violations)

---

# === PROTOCOL-PURE IPC EVENT BUS IMPLEMENTATION (BLOCKING) ===

## IPC Event Bus for Cross-Process Event-Driven Architecture
**Status:** [ ] Not Started   [ ] In Progress   [ ] Ready for Review   [ ] Complete
**Depends on:** OnexEvent schema stability, core serialization guarantees
**Unblocks:** Parity validator, distributed node orchestration, protocol-pure event-driven workflows
**DoD:** IPC event bus enables event-driven communication between ONEX nodes, validators, and tools across process boundaries. All protocol-pure event emission and subscription is supported for multi-process and distributed scenarios.
**Validation Checklist:**
- [x] Design minimal IPC event bus (Unix domain socket or file-based)
- [x] Implement IpcEventBus class in src/omnibase/runtimes/onex_runtime/v1_0_0/events/event_bus_ipc.py
- [x] Define `IpcEvent` wrapper model for transport consistency and schema enforcement
- [x] Support publish/subscribe for OnexEvent using consistent JSON schema and optional binary transport framing
- [x] Add event bus selection logic (env var/CLI arg)
- [x] Integrate with all node/validator CLI entrypoints
- [x] Document usage and configuration (including env vars, socket path conventions, error handling, reconnection behavior)
- [ ] Add protocol-pure tests for IPC event bus (cross-process)
- [ ] Validate with parity validator and multi-process introspection

**Implementation Notes:**
- The IPC event bus must serialize all messages using the same schema as the rest of the event system (OnexEvent). Consider defining an explicit `IpcEvent` wrapper model to support framing, type-tagging, and optional compression.
- Ensure the event bus gracefully handles message boundaries, malformed inputs, and reconnects (especially for file-based or socket implementations).
- Use context manager support for connection lifecycle.
- Prefer non-blocking I/O or threading to prevent deadlocks on slow consumers.

---

# === ROBUST ZMQ IPC EVENT BUS (BLOCKING) ===

## Robust ZMQ Event Bus for Cross-Process Event-Driven Architecture
**Status:** [ ] Not Started   [ ] In Progress   [ ] Ready for Review   [ ] Complete
**Depends on:** Protocol-pure event bus abstraction, OnexEvent schema stability
**Unblocks:** Reliable local orchestration, CI, and developer workflows
**DoD:** ZMQ event bus is robust, reliable, and protocol-pure, with all checklist items below complete.

**Validation Checklist:**
- [ ] Socket lifecycle & resource management
    - [ ] Ensure publisher (PUB) socket is always bound before any subscriber (SUB) connects.
    - [ ] Add explicit socket file cleanup before/after tests and on shutdown.
    - [ ] Implement context and socket shutdown/close logic in both publisher and subscriber.
    - [ ] Add process exit hooks to clean up ZMQ resources and socket files.
- [ ] Publisher/subscriber readiness & handshake
    - [ ] Implement a readiness handshake: subscriber signals "ready" before publisher sends events.
    - [ ] Add a "ready/ack" event or use a synchronization primitive (e.g., file, event, or ZMQ REQ/REP).
    - [ ] Publisher waits for at least one subscriber to be ready before sending events (configurable timeout).
- [ ] Delivery guarantees & diagnostics
    - [ ] Add event delivery confirmation (at least for test/dev mode): publisher logs if no subscriber is ready.
    - [ ] Add retry logic for publisher if send fails (with exponential backoff and max attempts).
    - [ ] Add health check endpoints/events for both publisher and subscriber (e.g., "ping", "pong").
    - [ ] Emit protocol-pure log/telemetry events for all connection, delivery, and error events.
- [ ] Backpressure, buffering, and flow control
    - [ ] Configure ZMQ high-water mark (HWM) for PUB/SUB sockets to prevent silent message drops.
    - [ ] Add warning or error log if buffer is full or events are dropped.
    - [ ] Document and expose HWM and buffer size as config/env options.
- [ ] Test harness & CI reliability
    - [ ] Add pre-test and post-test cleanup of ZMQ socket files.
    - [ ] Add publisher/subscriber liveness checks before running event delivery tests.
    - [ ] Add generous timeouts and retries for slow CI environments.
    - [ ] Ensure all test failures are logged with protocol-pure error events (not just exceptions).
- [ ] Error handling & recovery
    - [ ] Add robust error handling for all ZMQ socket operations (bind, connect, send, recv).
    - [ ] Implement automatic reconnection logic for both publisher and subscriber on failure.
    - [ ] Add exponential backoff and jitter for reconnection attempts.
    - [ ] Emit protocol-pure error events for all recoverable and fatal errors.
- [ ] Observability & telemetry
    - [ ] Emit protocol-pure log events for all major lifecycle events (bind, connect, ready, send, receive, error, shutdown).
    - [ ] Add metrics: event count, error count, last event timestamp, subscriber count.
    - [ ] Add health check endpoint/event for external monitoring.
- [ ] Documentation & configuration
    - [ ] Document all ZMQ event bus configuration options (socket path, HWM, timeouts, etc.).
    - [ ] Document developer workflow for running and debugging ZMQ event bus locally.
    - [ ] Add troubleshooting guide for common ZMQ issues (connection refused, message loss, etc.).
    - [ ] Ensure all configuration is available via environment variables and/or config files.
- [ ] Protocol-pure interface & future-proofing
    - [ ] Ensure all event bus usage is via the protocol-pure event bus interface (no direct ZMQ usage outside the bus).
    - [ ] Add a "backend" field to event bus diagnostics/logs to indicate ZMQ vs. future JetStream/NATS.
    - [ ] Document the process for swapping in JetStream/NATS in the future (interface, config, and test requirements).

*See detailed engineering checklist for sub-items and implementation notes.*

---

# === JetStream/NATS Event Bus Readiness (Milestone 1) ===

**Status:** [ ] Not Started   [ ] In Progress   [ ] Ready for Review   [ ] Complete
**Depends on:** Protocol-pure event bus abstraction, IPC event bus implementation
**Unblocks:** Future distributed and cloud-native ONEX deployments
**DoD:** Codebase is JetStream/NATS-ready with no architectural blockers for future integration. All event bus usage is protocol-pure and abstracted.
**Validation Checklist:**
- [x] All event emission and subscription use protocol-pure event bus interface (no direct in-memory/IPC usage)
- [x] All events are schema-validated models with unique event_id and correlation_id
- [ ] Subject naming convention for events is defined and documented
- [ ] Event bus implementation, NATS URL, and subject prefix are configurable (env/config)
- [ ] All event handlers are idempotent; event bus interface allows for future ack/nack
- [x] Only subscribe(handler) pattern is used for event consumption
- [x] Event bus interface accepts credentials/tokens/certs (for future use)
- [x] All event bus operations emit protocol-pure log/telemetry events
- [x] All tests use protocol event bus interface; in-memory/IPC buses are swappable
- [ ] Update all necessary schema

**Implementation Notes:**
- This section ensures the codebase is ready for JetStream/NATS integration in future milestones, with no protocol or architectural blockers.
- Actual JetStream implementation and deployment is deferred to a future milestone.

---

# === BATCH 1: PHASE 0 - ARCHITECTURE VIOLATIONS (BLOCKING) ===

## <a name="b11-event-driven-node-discovery-and-registry-node"></a>B1.1: Event-Driven Node Discovery and Registry Node
**Status:** [ ] Not Started   [ ] In Progress   [ ] Ready for Review   [ ] Complete
**Depends on:** None
**Unblocks:** B1.2
**DoD:** Protocol and schema for node_announce event are defined and documented in core; CollectorNode implemented; event-driven registration pattern documented.
**Validation Checklist:**
- [x] Protocol and schema for node_announce event defined and documented
- [x] Core refactored for protocol purity
- [x] CollectorNode implemented in runtime/nodes
- [x] Event-driven registration pattern documented
- [x] All tests pass
- [ ] Parity validator passes

- [x] **Event-Driven Node Discovery and Registry Node (CRITICAL)**
    - [x] **Define Node Announcement Protocol**
        - Protocol and schema for node_announce event are defined and documented in core. Protocol-pure, strongly typed, and validated as of 2025-06-01 (batch refactor).
        - Canonical Pydantic model, enums, and event handler logic updated and tested.
    - [x] **Refactor Core for Protocol Purity**
        - Remove all runtime/node imports and discovery logic from core (e.g., no `RuntimeHandlerDiscovery` import).
        - Require all handler/node discovery to occur via event-driven registration or plugin mechanisms.
        - **DoD:** Core contains only protocol definitions and abstract interfaces; no runtime/node dependencies.
    - [x] **Implement CollectorNode (Registry Node) in Runtime/Nodes**
        - Scaffold a CollectorNode that subscribes to the event bus and maintains a live registry of all nodes (ephemeral and persistent).
        - CollectorNode must handle node_announce events, maintain node status, and provide lookup for agents/schedulers.
        - **DoD:** CollectorNode is implemented as a runtime/node service, not in core; can receive and track node_announce events.
    - [x] **Document Event-Driven Registration Pattern**
        - Update developer documentation to require all nodes (including ephemeral/function-wrapped) to emit node_announce on startup.
        - Provide migration guidance for moving from static to event-driven registration.
        - **DoD:** Documentation and migration guide are published.

---

## <a name="b12-core-layer-architecture-violations"></a>B1.2: Core Layer Architecture Violations
**Status:** [ ] Not Started   [ ] In Progress   [ ] Ready for Review   [ ] Complete
**Depends on:** B1.1
**Unblocks:** B1.3
**DoD:** Core layer has zero imports from nodes/ or runtimes/; plugin-based discovery pattern for handlers implemented; Logger state access uses dependency injection.
**Validation Checklist:**
- [ ] All runtime/node imports removed from core
- [ ] Plugin-based discovery pattern for handlers implemented
- [ ] Logger state access uses dependency injection
- [ ] Core layer only defines protocols and abstract base classes
- [ ] All tests pass
- [ ] Parity validator passes

- [ ] **Core Layer Architecture Violations (CRITICAL)**
    - [ ] **core_file_type_handler_registry.py** - Remove imports of specific runtime handlers (lines 37-50)
    - [ ] **core_structured_logging.py** - Remove import of `omnibase.nodes.logger_node.v1_0_0.models.state` (line ~175)
        - No such import present; file is already protocol-pure.
    - [ ] **Action Completed:**
      - Plugin-based discovery pattern for handlers implemented
      - Logger state access now uses dependency injection
      - Core layer now only defines protocols and abstract base classes
    - **DoD:** Core layer has zero imports from nodes/ or runtimes/
    - **Priority:** BLOCKING - affects all downstream functionality
    - **Estimated Effort:** 2-3 days

---

## <a name="b13-shared-model-architecture-violations"></a>B1.3: Shared Model Architecture Violations
**Status:** [ ] Not Started   [ ] In Progress   [ ] Ready for Review   [ ] Complete
**Depends on:** B1.2
**Unblocks:** B1.4
**DoD:** All shared models have zero imports from nodes/; test registry cases moved to shared test infrastructure; dependency injection pattern for test case access used.
**Validation Checklist:**
- [ ] All node imports removed from shared models
- [ ] Test registry cases moved to shared test infrastructure
- [ ] Dependency injection pattern for test case access used
- [ ] All tests pass
- [ ] Parity validator passes

- [ ] **Shared Model Architecture Violations (CRITICAL)**
    - [ ] **model_node_metadata.py** - Remove import of omnibase.nodes.stamper_node.v1_0_0.node_tests.stamper_test_registry_cases (line 888)
    - [ ] **Action Completed:**
      - Test registry cases moved to shared test infrastructure
      - Dependency injection pattern for test case access used
      - Shared models have zero imports from nodes/
    - **DoD:** All shared models have zero imports from nodes/
    - **Priority:** BLOCKING - affects metadata handling across ecosystem
    - **Estimated Effort:** 1-2 days

---

## <a name="b14-cli-infrastructure-architecture-violations"></a>B1.4: CLI Infrastructure Architecture Violations
**Status:** [ ] Not Started   [ ] In Progress   [ ] Ready for Review   [ ] Complete
**Depends on:** B1.3
**Unblocks:** B1.5
**DoD:** CLI infrastructure has zero hardcoded node references; dynamic node discovery via registry pattern implemented; all hardcoded node references removed from CLI infrastructure.
**Validation Checklist:**
- [ ] All hardcoded node references removed from CLI infrastructure
- [ ] Dynamic node discovery via registry pattern implemented
- [ ] CLI only defines interfaces and discovery mechanisms
- [ ] All tests pass
- [ ] Parity validator passes

- [ ] **CLI Infrastructure Architecture Violations (CRITICAL)**
    - [ ] **cli_main.py** - Remove hardcoded `stamper_node@v1_0_0` registry entry
    - [ ] **cli_main_new.py** - Remove imports of `omnibase.nodes.cli_node.v1_0_0.*`
    - [ ] **commands/run_node.py** - Remove hardcoded NODE_REGISTRY with specific node paths
    - [ ] **commands/fix_node_health.py** - Remove import of `omnibase.nodes.node_manager_node.v1_0_0.helpers.helpers_maintenance`
    - [ ] **Action Completed:**
      - Dynamic node discovery via registry pattern implemented
      - All hardcoded node references removed from CLI infrastructure
      - CLI now only defines interfaces and discovery mechanisms
    - **DoD:** CLI infrastructure has zero hardcoded node references
    - **Priority:** BLOCKING - affects all CLI functionality and user experience
    - **Estimated Effort:** 3-4 days

---

## <a name="b15-runtime-handler-architecture-violations"></a>B1.5: Runtime Handler Architecture Violations
**Status:** [ ] Not Started   [ ] In Progress   [ ] Ready for Review   [ ] Complete
**Depends on:** B1.4
**Unblocks:** B1.6
**DoD:** Runtime handlers have zero imports from nodes/; shared functionality moved to runtime or core; shared utility registry for metadata block operations implemented.
**Validation Checklist:**
- [ ] All imports from nodes/ removed from runtime handlers
- [ ] Shared functionality moved to runtime or core
- [ ] Shared utility registry for metadata block operations implemented
- [ ] Runtime layer does not depend on specific node implementations
- [ ] All tests pass
- [ ] Parity validator passes

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

---

## <a name="b16-handler-misplacement"></a>B1.6: Handler Misplacement
**Status:** [ ] Not Started   [ ] In Progress   [ ] Ready for Review   [ ] Complete
**Depends on:** B1.5
**Unblocks:** B2.1
**DoD:** handlers/ contains only shared abstractions; all handler implementations are in the correct runtime directory.
**Validation Checklist:**
- [ ] All handler implementations are in the correct runtime directory
- [ ] handlers/ contains only base classes, protocols, and mixins
- [ ] All tests pass
- [ ] Parity validator passes

- [ ] **Handler Misplacement (MAJOR)**
    - [ ] **handlers/handler_ignore.py** - File deleted; no misplaced handlers remain. Directory now contains only shared abstractions, protocols, and mixins.
    - [ ] **Action Completed:**
      - All handler implementations are now in the correct runtime directory.
      - handlers/ contains only base classes, protocols, and mixins.
    - **DoD:** handlers/ contains only shared abstractions
    - **Priority:** HIGH - affects handler architecture consistency
    - **Estimated Effort:** 0.5 days

---

# === BATCH 2: PHASE 1 - ENUMS AND CORE RESULT MODELS ===

## <a name="b21-create-missing-enums-and-constants"></a>B2.1: Create Missing Enums and Constants
**Status:** [ ] Not Started   [ ] In Progress   [ ] Ready for Review   [ ] Complete
**Depends on:** B1.6
**Unblocks:** B2.2
**DoD:** All required enums (HandlerSourceEnum, HandlerTypeEnum, HandlerPriorityEnum, OnexStatus) are present and implemented under canonical names.
**Validation Checklist:**
- [ ] All required enums present and implemented under canonical names
- [ ] All fixed sets are covered by enums
- [ ] No missing constants module required
- [ ] All tests pass
- [ ] Parity validator passes

- [ ] **Create Missing Enums and Constants**
  - All required enums (HandlerSourceEnum, HandlerTypeEnum, HandlerPriorityEnum, OnexStatus) are present and implemented under canonical names. All fixed sets are covered by enums; no missing constants module required.

---

## <a name="b22-create-missing-result-models"></a>B2.2: Create Missing Result Models
**Status:** [ ] Not Started   [ ] In Progress   [ ] Ready for Review   [ ] Complete
**Depends on:** B2.1
**Unblocks:** B3.1
**DoD:** All required result models (HandlerMetadataModel, ExtractedBlockModel, SerializedBlockModel, CanHandleResultModel) are present and implemented under canonical names.
**Validation Checklist:**
- [ ] All required result models present and implemented under canonical names
- [ ] No missing protocol result models remain
- [ ] All tests pass
- [ ] Parity validator passes

- [ ] **Create Missing Result Models**
  - All required result models (HandlerMetadataModel, ExtractedBlockModel, SerializedBlockModel, CanHandleResultModel) are present and implemented under canonical names. No missing protocol result models remain.

---

# === BATCH 3: PHASE 2 - TYPING REFACTOR BY SUBSYSTEM ===

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
      - [ ] **model_node_metadata.py** - Replace Dict usage with typed models (combine with file size refactoring)
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
      - [ ] **directory_traverser.py** - Refactor DirectoryTraverser and related models to use typed models for all configuration and result fields (no Dict, Any, or magic numbers).
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
        - [ ] **Top-level files** (3/3) - ✅ __init__.py compliant, ❌ conftest.py has violations, ✅ exceptions.py compliant
        - [ ] **metadata/** (1/1) - ✅ metadata_constants.py reviewed (compliant - uses proper constants)
        - [ ] **core/** (5/6) - ❌ core_error_codes.py, ❌ core_function_discovery.py, ❌ core_plugin_loader.py, ❌ core_structured_logging.py reviewed, 1 more file needs review
        - [ ] **enums/** (9 files) - All files define only canonical Enums. No typing violations or protocol-breaking issues are present.
        - [ ] **handlers/** (3 files) - All files are compliant, use only strongly typed models, and no typing violations or protocol-breaking issues are present.
        - [ ] **model/** (33 files) - All protocol-facing fields and return types use the strongest possible typing. Any use of Any/Dict/List is for extensibility or protocol-allowed cases. No protocol-breaking violations remain.
        - [ ] **fixtures/** (7 files) - All files use strongly typed models. Any use of Any is for protocol/test extensibility only; no protocol-breaking violations remain.
        - [ ] **mixin/** (8 files) - All files use strongly typed models for protocol-facing data. Any use of Dict/Any/List is for serialization, redaction, or introspection flexibility only; no protocol-breaking violations remain.
        - [ ] **protocol/** (4/30+) - Most protocol files are compliant and use only strongly typed models and enums. The following files require refactoring to eliminate Any, Dict, and legacy return types: protocol_file_type_handler.py, protocol_validate.py, protocol_directory_traverser.py, protocol_schema_loader.py. 4 files need refactor; 26+ more are already compliant.
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

# === BATCH 4: PHASE 3 - CANARY FILE LOCK-IN AND METADATA ENFORCEMENT ===

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

# === BATCH 5: PHASE 4 - TEST SUITE CANONICALIZATION ===

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

# === BATCH 6: PHASE 5 - CI AND ENFORCEMENT HARDENING ===

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

# === BATCH 7: PHASE 6 - RELEASE INFRASTRUCTURE AND FINAL M1 TAGGING ===

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

## Batch Execution Tracking (Revised)

| Batch | Scope/Files | Status | Blockers/Notes |
|-------|-------------|--------|----------------|
| 1     | protocol/ (remaining uncompleted files) | Complete | - |
| 2     | handlers/ (uncompleted items) | Not Started | - |
| 3     | core/ (uncompleted items) | Not Started | - |
| 4     | mixin/, utils/, fixtures/ (uncompleted items) | Not Started | - |
| 5     | templates/, schemas/ (uncompleted items) | Not Started | - |
| 6     | CI, docs, release infra | Not Started | - |

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

- [ ] **model_node_metadata.py** - Refactor IOContract, SignatureContract, StateContractBlock, and NodeMetadataBlock to use typed models instead of Dict[str, str] and Dict[str, Any].
- [ ] **model_onex_message_result.py** - Refactor OnexResultModel and OnexMessageModel to use typed models for metadata/context fields instead of Dict[str, Any].
- [ ] **model_onex_event.py** - Refactor OnexEvent to use a strongly typed model for metadata instead of Dict[str, Any].
- [ ] **model_validate_error.py** - Refactor ValidateMessageModel and ValidateResultModel to use typed models for context fields instead of Dict[str, Any].
- [ ] **model_node_introspection.py** - Refactor NodeMetadataModel, ContractModel, and NodeIntrospectionResponse to use typed models for version_status, performance_profile, and other Dict fields.
- [ ] **fixtures/cli_stamp_fixtures.py** - Refactor CLIDirFixtureCase and CLIStampDirFixtureRegistry to use typed models for files/subdirs instead of Tuple[str, str] and List[Tuple[str, str]].
- [ ] **fixtures/fixture_loader.py** - Refactor CentralizedFixtureLoader to use typed models for fixture data instead of Any/Dict.
- [ ] **fixtures/centralized_fixture_registry.py** - Refactor CentralizedFixtureRegistry to use typed models for fixture cases and data instead of mocks and Any/Dict.
- [ ] **fixtures/registry_adapter.py** - Refactor RegistryAdapter and MockRegistryAdapter to use strongly typed models for all registry data and artifact fields (no Dict[str, Any]).
- [ ] **fixtures/mocks/dummy_schema_loader.py** - Refactor DummySchemaLoader to use strongly typed models for all return values (no dict[str, Any]).
- [ ] **fixtures/mocks/dummy_handlers.py** - Refactor all dummy handler classes to use strongly typed models for all handler methods (no Any, Tuple, or Dict returns).
- [ ] **protocol_file_type_handler.py** - Refactor ProtocolFileTypeHandler to require/return strongly typed models for all handler methods (no Any, Dict, or tuple returns).
- [ ] **protocol_cli.py** - Refactor ProtocolCLI to use typed models for describe_flags and logger fields.
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
- [ ] **protocol/protocol_schema_loader.py** - Protocol-pure and strongly typed as of 2025-06-01 (batch refactor)
- [ ] **protocol/protocol_testable_registry.py** - Refactor get_node to return a strongly typed model instead of Dict[str, Any].
- [ ] **protocol/protocol_tool.py** - Refactor execute to accept and return strongly typed models instead of Dict[str, Any] and Any.
- [ ] **model/model_state_contract.py** - Refactor StateContractModel, StateSchemaModel, and ErrorStateModel to use strongly typed models for all properties and metadata fields (no Dict[str, Any]).
- [ ] **model/model_project_metadata.py** - Refactor ProjectMetadataBlock to use strongly typed models for tools and any Dict fields.
- [ ] **model/model_schema.py** - Refactor SchemaModel to use strongly typed models for properties and required fields (no Dict[str, Any]).

- [ ] **Structured Logging Protocol-Pure Refactor**
    - [ ] **core_structured_logging.py** - All emit_log_event calls now require LogContextModel, and all call sites have been updated to use the canonical, strongly typed model.
    - [ ] **All CLI, utility, node, and handler files** - All emit_log_event calls now use LogContextModel for the context argument, with all required fields populated.
    - [ ] **All event emission and telemetry decorator tests** - All event emission and handler protocol-purity tests now pass.
    - [ ] **Handler and protocol interfaces** - All handler, protocol, and CLI interfaces are strictly typed and protocol-pure, with no legacy or dict-based context or metadata.
    - [ ] **Test suite** - All tests pass (696 passed, 32 skipped, 3 warnings for deprecated Pydantic .dict() usage).
    - [ ] **Batch status**: Protocol-pure logging, event emission, and handler typing batch is now complete. All protocol, handler, and CLI logging is type-safe and protocol-pure.

# === REGISTRY NODE: DYNAMIC EVENT BUS PORT ALLOCATION, INTROSPECTION, AND TOOL DISCOVERY (BLOCKING) ===

**See also:** [docs/onex/registry_node_introspection.md](../onex/registry_node_introspection.md) for the full introspection/query schema and milestone table.

## Registry Node for Dynamic Event Bus Port Allocation and Tool Discovery
**Status:** [ ] Not Started   [ ] In Progress   [ ] Ready for Review   [ ] Complete
**Depends on:** Protocol-pure event bus abstraction, node introspection
**Unblocks:** Robust test/CI isolation, distributed orchestration, dynamic tool discovery
**DoD:** All event bus port allocation and tool discovery is registry-driven, introspection is comprehensive, and all tests pass.

**Summary:**
All actionable engineering tasks for registry-driven event bus port allocation, introspection, and tool discovery are now tracked in [implementation_checklist_registry_node_port_allocation.md](./implementation_checklist_registry_node_port_allocation.md). Refer to that document for the current checklist and progress.

**Note:** PortRequestModel now requires UUID for requester_id, enforcing protocol-pure typing.
