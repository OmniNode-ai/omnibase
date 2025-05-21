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

**Recommendation:**
Define a shared module (e.g., `error_codes.py`) containing all error codes as constants or enums.

```python
class ErrorCode(str, Enum):
    NODE_EXEC_ERROR = "NODE_EXEC_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    ENGINE_FAILURE = "ENGINE_FAILURE"
```

**Rationale:**
Improves consistency and simplifies CI validation of node responses.

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

**Recommendation:**
- Define a minimal required schema for ONEX lifecycle events:

```json
{
  "event_type": "NODE_START",
  "node_id": "stamper_node",
  "timestamp": "ISO-8601",
  "input_id": "UUID",
  "metadata": { "request_id": "..." }
}
```
- Document in `docs/protocol/onex_event_schema.md`.
- Reference this in all emitter implementations.

---

## 3. Plugin Discovery Strategy

**Recommendation:**
- Define a plugin loading convention to ensure runtime discovery.
- Options:
  - **Entry Points:** Python's setuptools-based `entry_points` for plugin registration.
  - **Registry File:** Centralized `plugin_registry.yaml` listing hook implementations.
  - **Environment Hooks:** Plugins loaded via paths/env vars in deployment.
- Suggest supporting all three, with priority ordering.

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

**Recommendation:**
- Create a decorator that wraps node entrypoints and standardizes:
  - Logging context binding
  - Timing capture
  - ONEX event emission (start/success/failure)
  - Error wrapping

```python
@telemetry("stamper_node")
def run_stamper_node(...):
    ...
```
- Optional params: `emit_events=True`, `log_exceptions=True`, etc.

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

**Recommendation:**
- Implement `redact()` method on state models or mark redacted fields with metadata.

```python
class StamperInputState(BaseModel):
    api_key: Optional[str] = Field(default=None, metadata={"sensitive": True})
```
- Redaction applied automatically during `.model_dump()` or logging.
- Prevents accidental leak of credentials or PII in logs/events.

---

## 8. Correlation ID and Distributed Tracing

**Recommendation:**
- Inject and propagate a `request_id` or `correlation_id` across all log entries and events.
  - Can be generated at CLI layer and passed via `StamperInputState`.
  - Bind to all loggers and emitters.

---

These refinements ensure the ONEX platform remains robust under version pressure, scalable in distributed systems, and secure by default. They are suitable for immediate adoption in the Stamper node and eventual enforcement across all nodes and tools. 