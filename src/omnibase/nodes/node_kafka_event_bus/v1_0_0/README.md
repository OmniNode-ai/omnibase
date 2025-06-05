# Template Node (ONEX Canonical)

This node implements the canonical ONEX reducer pattern and serves as the reference for all new nodes.

## Key Features
- **Reducer Pattern:** Implements `.run()` and `.bind()` lifecycle. All business logic is delegated to inline handlers or runtime helpers.
- **Introspection:** Standards-compliant introspection via `introspection.py`, exposing node metadata, contract, CLI arguments, capabilities, and scenario registry.
- **Scenario-Driven Validation:** All validation and testing is scenario-driven. Scenarios are defined in `scenarios/index.yaml` and exposed via introspection.
- **Error Codes:** Canonical error codes are defined in `error_codes.py` and exposed via introspection.

## Usage

### CLI Introspection
```bash
python node.py --introspect
```
Prints full node contract, metadata, CLI arguments, and available scenarios as JSON.

### Scenario Discovery
```bash
python node.py --run-scenario <scenario_id>
```
Prints the scenario config for the given scenario ID from the node's scenario registry.

## Usage Modes

### 1. Direct CLI Invocation (Short-lived)

You can invoke the node directly for health checks, scenario runs, or direct input processing. In this mode, the node runs the requested operation and exits.

Example:

```bash
poetry run onex run node_kafka_event_bus --args='{"args": ["--health-check"]}'
```

### 2. Event-Driven (Serve/Daemon) Mode

For event-driven workflows (e.g., using the ONEX CLI to publish events), the node **must be running as a persistent process** that subscribes to the event bus and handles events as they arrive. This is called "serve" or "daemon" mode.

**Important:**
- The event-driven CLI (`poetry run onex run ...`) publishes events to the event bus and expects the node to be running and subscribed.
- If the node is not running in serve mode, CLI commands will hang or time out, as there is no subscriber to handle events.

#### Starting the Node in Serve Mode

```bash
poetry run python -m omnibase.nodes.node_kafka_event_bus.v1_0_0.node --serve
```

Or, if integrated with the ONEX CLI:

```bash
poetry run onex run node_kafka_event_bus --args='["--serve"]'
```

This will start the node as a persistent process, subscribing to the event bus and handling events as they arrive.

## Developer Notes
- Input/output state models are defined in `models/state.py` and must use canonical Pydantic models and Enums.
- All protocol and interface definitions must use the strongest possible typing (see project rules).
- Error codes must be referenced from `error_codes.py` and never hardcoded.
- All scenarios must be registered in `scenarios/index.yaml` and exposed via introspection.

## Naming Standards (Canonical)

All files (except for explicit exceptions below) must be prefixed with the name of their immediate parent directory, using all-lowercase and underscores. This ensures clarity, prevents import collisions, and enables automated enforcement.

**Examples:**
- `tools/input/input_validation_tool.py`
- `tools/output/output_field_tool.py`
- `protocols/input_validation_tool_protocol.py`
- `protocols/output_field_tool_protocol.py`

**Exceptions (do not require prefix):**
- `node.py` (main node entrypoint in versioned node directories)
- `contract.yaml` (canonical contract in versioned node directories)
- `node.onex.yaml` (node metadata in versioned node directories)
- `README.md`, `error_codes.py`, `pytest.ini` (standard project files)
- `state.py` (if always in a `models/` subdir and unambiguous)
- `test_*.py` (test files, by convention)

Any new exceptions must be justified and documented in the standards file.

For authoritative and up-to-date rules, see `.cursor/rules/standards.mdc`.

## References
- See `introspection.py` for the full introspection implementation.
- See `node_kafka_event_bus_milestone1_checklist.md` for milestone requirements.
- See project rules for interface, typing, and testing standards.

## Protocol Compliance and Edge Cases

### Protocol Compliance
- **Event Format & Models:**
  - All events use the canonical `OnexEvent` and `OnexEventMetadataModel` as defined in `model_onex_event.py`.
  - Event bus operations (`publish`, `subscribe`) accept and emit these models only.
- **Protocol Interface:**
  - Implements the `ProtocolEventBus` interface (`publish`, `subscribe`, `unsubscribe`, `clear`, `bus_id`).
  - All public methods and properties are protocol-compliant.
- **State Contract:**
  - Input/output state is defined in `contract.yaml` using canonical models and enums.
  - Required fields: `version`, `status`, `message`, and protocol-compliant output fields.
- **Error Handling:**
  - All errors use project-specific error codes and models.
  - Error events use the `error`, `error_type`, and `error_code` fields in metadata.
- **Event Schema Validation:**
  - All emitted events can be validated using the canonical ONEX event schema validator.

### Edge Cases
- **Degraded Mode:**
  - If the Kafka broker is unavailable, the node falls back to `InMemoryEventBus` for local event delivery.
  - All events remain protocol-compliant, but are not persisted or delivered cross-process.
- **Async/Sync Bridging:**
  - The Kafka event bus currently wraps synchronous Kafka client calls in async methods as a temporary bridge until full async support is implemented.
- **Health Check, Bootstrap, and Introspection:**
  - All emit events/results using canonical models and are protocol-compliant.

### Notes
- All protocol compliance and edge case handling is covered by automated tests and schema validation.
- Any future changes to protocol or event schema should be reflected in this documentation and validated by the test suite.

## Configuration

- Configure the node by providing a `KafkaEventBusConfigModel` via state or contract.
- Required fields: `bootstrap_servers`, `topics`.
- Optional fields: `security_protocol`, `sasl_mechanism`, `sasl_username`, `sasl_password`, `client_id`, `group_id`, `partitions`, `replication_factor`, `acks`, `enable_auto_commit`, `auto_offset_reset`.

## Migration Notes

- This node replaces JetStream/ZMQ event bus implementations.
- All event payloads and types are protocol-agnostic and compatible with existing ONEX event consumers.
