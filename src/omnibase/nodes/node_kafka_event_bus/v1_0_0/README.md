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

## Protocol Compliance

- This node emits and consumes `OnexEvent` objects (see `model_onex_event.py`).
- Implements the canonical `ProtocolEventBus` interface for ONEX event buses.
- All configuration is provided via `KafkaEventBusConfigModel` (see `models/config.py`).

## Configuration

- Configure the node by providing a `KafkaEventBusConfigModel` via state or contract.
- Required fields: `bootstrap_servers`, `topics`.
- Optional fields: `security_protocol`, `sasl_mechanism`, `sasl_username`, `sasl_password`, `client_id`, `group_id`, `partitions`, `replication_factor`, `acks`, `enable_auto_commit`, `auto_offset_reset`.

## Migration Notes

- This node replaces JetStream/ZMQ event bus implementations.
- All event payloads and types are protocol-agnostic and compatible with existing ONEX event consumers.
