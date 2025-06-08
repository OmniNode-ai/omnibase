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

## CLI Usage

### Dry Run Mode

> **Note:**
> The `--dry-run` flag is **not applicable** for this node, as it has no side effects to prevent. Invoking `--dry-run` will print a message and exit immediately. This is the canonical ONEX pattern for pure/event bus nodes.

### Validation

If you wish to validate scenario or config files, use the `--validate` flag (if implemented) or run the scenario regression tests via `pytest`.

### Serve Mode

To run the node in event-driven (serve) mode:

```bash
poetry run python -m omnibase.nodes.node_kafka_event_bus.v1_0_0.node --serve
```

Or, with the ONEX CLI:

```bash
poetry run onex run node_kafka_event_bus --args='["--serve"]'
```

## Async CLI Stub

The Kafka node CLI now includes a `--serve-async` flag as a **stub/placeholder** for future async event loop support:

```bash
poetry run python -m omnibase.nodes.node_kafka_event_bus.v1_0_0.node --serve-async
```

- This flag currently logs a warning and prints a message that async CLI support is not yet implemented.
- No blocking or coupling to other CLI logic; this is a forward-compatible placeholder.
- See the migration plan and milestone checklist for details on future async CLI work.

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
- Required fields: `