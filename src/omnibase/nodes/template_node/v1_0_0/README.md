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

## References
- See `introspection.py` for the full introspection implementation.
- See `template_node_milestone1_checklist.md` for milestone requirements.
- See project rules for interface, typing, and testing standards.
