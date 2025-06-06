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

### ⚠️ Business Logic Delegation (Canonical Pattern)

**All business logic must be delegated to protocol-typed helpers/tools.**

- The reducer class (`node.py`) is strictly an orchestrator: it wires together protocol-compliant tools, event bus, and scenario runner.
- No business logic, validation, or output computation should be implemented inline in the reducer.
- If you find business logic in the reducer, refactor it into a protocol-typed helper/tool.

This pattern ensures:
- Maximum testability and swappability
- Protocol-pure compliance
- Future compatibility with dependency injection/registry frameworks

**Maintainers:** Always review new code for violations of this pattern.

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
- See `template_node_milestone1_checklist.md` for milestone requirements.
- See project rules for interface, typing, and testing standards.
