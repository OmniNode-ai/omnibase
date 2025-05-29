<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode.ai
created_at: '2025-05-28T12:40:26.616377'
description: Stamped by ONEX
entrypoint: python://canary_node_cli_alignment.md
hash: b96a1d8b22e220e0825ec82b9817e7eda7ca31f980032ed7bf429052087806dc
last_modified_at: '2025-05-29T11:50:15.069601+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: canary_node_cli_alignment.md
namespace: omnibase.canary_node_cli_alignment
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: 668de083-4374-44c7-b2c3-fd70bf89ad7d
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# Canary Node & CLI Alignment Strategy

## Purpose and Scope

This document defines the architectural approach for unifying the ONEX Stamper node (the "canary" node) and its CLI interface. It establishes patterns and rationale for future node/CLI tool development, ensuring maintainability, extensibility, and testability across the ONEX platform.

---

## Background: CLI vs. Node Patterns

- **CLI (Typer-based):**
  - Parses arguments and subcommands (file, directory, etc.).
  - Passes options to the engine (`StamperEngine`) for stamping/processing.
  - Handles output formatting, argument validation, and error handling.
- **Node Entrypoint (main.py):**
  - Accepts minimal arguments (e.g., file_path, author).
  - Constructs a stub input state and invokes `run_stamper_node`.
  - Lacks support for full CLI feature set (templates, batch, patterns, etc.).

---

## Discrepancies and Motivation for Unification

- CLI supports a rich feature set and full engine API surface.
- Node supports only a stub interface, with minimal options and limited invocation modes.
- CLI and node do not share a common input schema or output model.
- This divergence hinders testability, automation, and future extensibility.

---

## Canonical Approach for Node/CLI Alignment

### 1. Unified Input/Output State
- Define `StamperInputState` and `StamperOutputState` (Pydantic models) to cover all CLI options and engine parameters.
- Use these models for both CLI and programmatic node invocation.
- Document all fields and their mapping to CLI arguments.
- **Version Management:**
  - All state models must include an explicit `version` field.
  - Maintain migration utilities and a changelog for schema evolution.

### 2. Node Entrypoint Logic
- `run_stamper_node` detects mode (file vs. directory) from input state.
- Dispatches to the correct engine method, passing all options.
- Structures output in `StamperOutputState`.
- Emits ONEX lifecycle events (NODE_START, NODE_SUCCESS, NODE_FAILURE).
- Never emits CLI-formatted or colorized output.

### 3. CLI Adapter
- Provide a drop-in CLI adapter (e.g., `cli_stamp_node_adapter.py`) that maps CLI args to `StamperInputState` and invokes the node.
- Ensures test parity and interop between CLI and node.

### 4. Extensibility and Observability
- Design for future options (dry-run, custom event sinks, advanced filters).
- Make event sinks pluggable (stdout, file, remote, etc.).
- Support batch/streaming workflows and schema versioning.
- Normalize error handling and reporting in output state.
- **Structured Logging:**
  - All nodes and CLI tools must use structured logging (e.g., JSON via `structlog`).
  - Log context (node_id, request_id, etc.) must be propagated for traceability.
- **Centralized Configuration:**
  - Use a versioned config file (YAML/TOML/JSON) for logging, plugin paths, event sinks, etc.
  - Support environment variable overrides for 12-factor compatibility.
- **Error Handling:**
  - All errors must be mapped to unique error codes in output state.
  - Maintain a canonical error code registry.
- **Security:**
  - Sensitive fields in input/output state must be redacted or omitted from logs and outputs.
  - Document and enforce sensitive field handling.
- **Performance Metrics:**
  - Output state must include `processing_duration_ms` and `processed_items_count`.
  - Optionally include resource usage metrics.

### 5. Event Emission (ONEX Lifecycle Events)
- Define a formal interface/module for event emission (e.g., `onex_event_emitter`).
- Events should be pluggable: can be logged, sent to a message queue, or handled by a future event node.
- **Note:** The event emitter will be broken out into its own node/module in the future, enabling event-driven workflows and observability across ONEX.

### 6. Test and Documentation Strategy
- Use golden file testing to ensure CLI/node output parity.
- Automate documentation of CLI-to-node feature mapping.
- Maintain a changelog and deprecation path for schema changes.

### 7. Extensibility and Plugins
- Design for plugin hooks (pre/post-processing, custom handlers, event sinks).
- Use entry points or a plugin registry for dynamic discovery and loading.

---

## The Stamper Node as Canary

- Serves as the reference implementation for all future ONEX nodes and CLI tools.
- Patterns and lessons learned here will be applied to subsequent nodes (validators, reducers, etc.).
- All new nodes/tools should:
  - Use unified input/output state models
  - Support structured, machine-readable output
  - Be testable and automatable via both CLI and programmatic entrypoints
  - Emit structured logs and ONEX lifecycle events
  - Use centralized configuration and error code registry

---

## Future Directions

- Extend this approach to additional nodes (e.g., validators, orchestrators).
- Break out the event emitter into its own node/module for event-driven workflows.
- Add plugin/extension points for custom handlers and event sinks.
- Support internationalization/localization and performance metrics in output state.
- Harden input validation and security for multi-tenant/SaaS use cases.
- Continue to automate documentation and test harnesses for all new nodes/tools.

---

## Open Questions & Areas for Innovation

- How should plugin discovery and registration be handled across CLI and node?
- What is the best pattern for event sink injection/configuration?
- How can we best support streaming/batch output for very large directory operations?
- What additional observability hooks are needed for production/CI/CD use?
- What is the best architecture for the event emitter/event node, and how should it integrate with the rest of ONEX?

---

# Refinement Suggestions

This section captures minor but impactful refinements to the Stamper Node and CLI alignment strategy, focusing on implementation clarity, future-proofing, and maintainability.

## 1. Logger Context Binding

**Recommendation:**
Bind shared execution context early in `run_stamper_node()` and reuse the logger.

```python
node_logger = structlog.get_logger(__name__).bind(node_id=node_id, mode="file" if input_state.file_path else "directory")
```

**Rationale:**
Avoid repetitive binding calls. Ensures all logs share a common context (e.g., node_id, execution mode).

---

## 2. Abstract Event Emitter Interface

**Recommendation:**
Refactor `OnexEventEmitter` to support interchangeable backends (e.g., message queue, file, stdout).

```python
class BaseEventEmitter(Protocol):
    def emit_node_start(...): ...
    def emit_node_success(...): ...
    def emit_node_failure(...): ...

# Implementations:
#   - StructlogEventEmitter
#   - JetStreamEventEmitter
```

**Rationale:**
Decouples logging/event transport. Enables future event routing without code changes.

---

## 3. Centralized Error Code Definitions

**Status:** ✅ **IMPLEMENTED**
All error handling now uses centralized error codes defined in `src/omnibase/core/error_codes.py`.

```python
from omnibase.core.error_codes import OnexError, CoreErrorCode

# All errors use defined codes
raise OnexError("Invalid input provided", CoreErrorCode.INVALID_PARAMETER)
```

**Implementation Details:**
- `OnexError` class provides structured error handling
- `CoreErrorCode` enum defines all canonical error codes
- CI linter enforces error code compliance across the codebase
- All 39+ error code violations have been systematically fixed

**Rationale:**
Improves consistency and simplifies CI validation of node responses. Provides structured error handling for better debugging and monitoring.

---

## 4. CLI/Node Output Parity Test Harness

**Recommendation:**
Add a test module (e.g., `test_canary_equivalence.py`) to verify CLI and direct node invocations produce identical output.

**Rationale:**
Guarantees interface-level compatibility, prevents CLI/node schema drift.

---

## 5. Schema Diff and Drift CI

**Recommendation:**
Emit and commit the Pydantic-generated JSON schema for input and output states as versioned artifacts.

```python
with open("schemas/stamper_input.schema.json", "w") as f:
    f.write(StamperInputState.model_json_schema())
```

**Rationale:**
Provides CI-level monitoring for schema changes and downstream integration safety.

---

## Optional Enhancements
- Map `error_code` to numeric exit codes for CI.
- Use a telemetry decorator to abstract timing/event/logging around node entrypoints.

---

These refinements increase reliability, reduce duplication, and future-proof the node architecture for more advanced ONEX deployments.

This document is a living reference. All future ONEX node/CLI tool designs should be reviewed for alignment with these principles and updated as the platform evolves.

---

# Refinement Additions for Canary Node & CLI Alignment Strategy

This section supplements the core Canary Node alignment plan with precision refinements and implementation augmentations. It aims to close any remaining gaps in schema enforcement, event discipline, observability, and long-term extensibility.

---

## 1. Schema Versioning and Changelog Enforcement

**Recommendation:**
- Embed `version: Literal["1.x"]` in each Pydantic schema.
- Maintain a `CHANGELOG.stamper.md` with each change explicitly mapped to a schema version.
- Enforce via CI: any diff in `model_json_schema()` must require a version bump and changelog update.

---

## 2. ONEX Event Schema Standardization

**Status:** ✅ **IMPLEMENTED**
ONEX Event Schema has been standardized with comprehensive documentation and implementation.

**Implementation Details:**
- Standardized `OnexEvent` model with required fields (event_type, node_id, timestamp, correlation_id)
- Complete event type enumeration in `OnexEventTypeEnum`
- Event emission infrastructure with telemetry decorators
- Real-time event processing capabilities
- Comprehensive test coverage with 11+ test methods

**Event Schema:**
```json
{
  "event_type": "NODE_START",
  "node_id": "stamper_node",
  "timestamp": "ISO-8601",
  "correlation_id": "UUID",
  "metadata": { "request_id": "..." }
}
```

**Documentation:** Complete event schema documentation available in the codebase.

---

## 3. Plugin Discovery Strategy

**Status:** ✅ **IMPLEMENTED**
Comprehensive plugin discovery system supporting all three recommended mechanisms.

**Implementation Details:**
- **Entry Points:** Python setuptools-based `entry_points` for plugin registration (Priority 0)
- **Registry File:** Centralized `plugin_registry.yaml` listing hook implementations (Priority 5)
- **Environment Hooks:** Plugins loaded via environment variables (Priority 10 - highest)
- Priority-based loading with higher priority plugins replacing lower priority ones
- Support for 5 plugin types: handlers, validators, tools, fixtures, nodes

**Documentation:** Complete plugin discovery guide at `docs/plugins/plugin_discovery.md`

---

## 4. Schema Drift Detection

**Recommendation:**
- Add a schema drift test that validates the current model output against a committed reference.

```python
with open("schemas/expected_input.schema.json") as f:
    expected = json.load(f)
    assert StamperInputState.model_json_schema() == expected
```
- Fails CI on unintended model change.
- Provides alerting and review gate for compatibility updates.

---

## 5. Telemetry Decorator for Entrypoints

**Status:** ✅ **IMPLEMENTED**
Telemetry decorators have been implemented and applied to all node entrypoints.

**Implementation Details:**
- Telemetry decorator abstracts timing, event emission, and logging
- Applied to all node entrypoints for consistent observability
- Automatic correlation ID propagation
- Standardized event emission (NODE_START, NODE_SUCCESS, NODE_FAILURE)
- Performance metrics capture

**Usage:**
```python
@telemetry("stamper_node")
def run_stamper_node(...):
    ...
```

---

## 6. CLI Exit Code Mapping

**Recommendation:**
- Map known `error_code` values to numeric CLI exit codes.

```python
ERROR_EXIT_CODES = {
  "NODE_EXEC_ERROR": 1,
  "INVALID_INPUT": 2,
  "ENGINE_FAILURE": 3,
}
# CLI should sys.exit(ERROR_EXIT_CODES.get(output.error_code, 99))
```
- Ensures CI/CD systems receive structured feedback.

---

## 7. Redaction Strategy for Sensitive Fields

**Status:** ✅ **IMPLEMENTED**
Comprehensive sensitive field redaction system has been implemented.

**Implementation Details:**
- `SensitiveFieldRedactionMixin` provides automatic redaction capabilities
- Sensitive fields marked with metadata in Pydantic models
- Automatic redaction during `.model_dump()` and logging operations
- Protocol-first testing with redaction validation
- Prevents accidental leak of credentials or PII in logs/events

**Usage:**
```python
class StamperInputState(SensitiveFieldRedactionMixin, BaseModel):
    api_key: Optional[str] = Field(default=None, metadata={"sensitive": True})
```

---

## 8. Correlation ID and Distributed Tracing

**Status:** ✅ **IMPLEMENTED**
Comprehensive correlation ID and distributed tracing system has been implemented.

**Implementation Details:**
- Correlation/Request ID propagation across all state models and ONEX events
- Automatic correlation ID generation and injection
- Structured logging with correlation ID binding
- Event-driven architecture with correlation tracking
- Real-time event processing with tracing capabilities

**Features:**
- Correlation ID propagation across all operations
- Distributed tracing support for complex workflows
- Structured logging with correlation context
- Event correlation for debugging and monitoring

---

## 9. Structured Logging Infrastructure

**Status:** ✅ **IMPLEMENTED**
Comprehensive structured logging infrastructure routing all output through the Logger Node.

**Implementation Details:**
- Complete replacement of print() statements and Python logging
- Event-driven architecture via ProtocolEventBus
- Logger Node handles all output formatting as side effects
- Centralized configuration with environment variable support
- Auto-initialization with fallback mechanisms
- Context extraction and correlation ID support

**System Flow:**
```
Application Code → emit_log_event() → ProtocolEventBus → StructuredLoggingAdapter → Logger Node → Context-appropriate output
```

**Configuration:**
- Environment variables: `ONEX_LOG_FORMAT`, `ONEX_LOG_LEVEL`, `ONEX_ENABLE_CORRELATION_IDS`
- Output targets: `ONEX_LOG_TARGETS`, `ONEX_LOG_FILE_PATH`
- Event bus configuration: `ONEX_EVENT_BUS_TYPE`

---

These refinements ensure the ONEX platform remains robust under version pressure, scalable in distributed systems, and secure by default. The implemented features provide a solid foundation for Milestone 1 completion and preparation for Milestone 2 development.

---

## 2025-06 Update: Adapter and Contract Conventions

- **Adapters:** All adapters (CLI, web, etc.) must be placed in an `adapters/` directory under each node version. Adapters are referenced in `node.onex.yaml` by explicit module/class.
- **Contract:** The state contract file must be named `contract.yaml` for consistency and CI/tooling compatibility.
- **Metadata:** Each version must have exactly one `node.onex.yaml` file as the canonical metadata block, referencing the entrypoint, adapter, and contract.
- **Loader Behavior:** Loader ignores version directories unless `node.onex.yaml` is present or a `WIP` marker is set.
- **See Also:** [structural_conventions.md](structural_conventions.md), [canonical_file_types.md](../standards/canonical_file_types.md) for rationale and canonical examples.

**Canonical node.onex.yaml snippet:**
```yaml
node_id: "stamper_node"
name: "Stamper Node"
version: "1.0.0"
entrypoint:
  module: "nodes.stamper_node.v1_0_0.node"
  function: "run_stamper_node"
adapter:
  module: "nodes.stamper_node.v1_0_0.adapters.cli_adapter"
  class: "StamperNodeCliAdapter"
contract: "contract.yaml"
```
