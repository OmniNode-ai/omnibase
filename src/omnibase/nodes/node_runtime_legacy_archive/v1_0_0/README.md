# node_runtime (ONEX Canonical Runtime Node)

This node implements the canonical ONEX reducer pattern and exposes core runtime helpers via a dispatch table. It serves as the single entry point for all shared runtime logic, making helpers discoverable and invocable by agents, orchestrators, and other nodes.

## Key Features
- **Reducer Pattern:** Implements `.run()` lifecycle. All business logic is dispatched via a table of core helpers.
- **Dispatch Table:** Exposes helpers like `merge_state` and `emit_event` for use by other nodes and agents.
- **Introspection:** Standards-compliant introspection via `--introspect`, exposing available actions, input/output models, and dispatch table.
- **Scenario-Driven Validation:** Designed to be exercised via scenario YAMLs, not traditional test files.

## Usage

### Introspection
```bash
python node.py --introspect
```
Outputs available actions, input/output schemas, and dispatch table.

### Run a Helper Action
```bash
python node.py merge_state '{"foo": 1}'
```

### Dispatch Table
See `dispatch.yaml` for a list of available actions and their parameters.

## Extending
- Add new helpers to the dispatch table in `node.py` and document them in `dispatch.yaml`.
- All helpers should be protocol-compliant and return structured results.

## Directory Structure
```
node_runtime/
  node.py
  dispatch.yaml
  README.md
  models/
  scenarios/
```

## License
Copyright OmniNode Team

## Dispatch Table Structure

The dispatch table is defined in `dispatch.yaml` and validated by the `DispatchTableModel` (see `models/dispatch.py`). Each action includes:
- `id`: Action identifier (e.g., `merge_state`)
- `description`: Human-readable description
- `params`: List of parameters (name, type, description)
- `returns`: Return type and description

Example from `dispatch.yaml`:
```yaml
actions:
  - id: merge_state
    description: Merge two or more state dicts (stub implementation)
    params:
      - name: state
        type: dict
        description: State dictionary to merge
    returns:
      type: dict
      description: Merged state
  - id: emit_event
    description: Emit an event (stub implementation)
    params:
      - name: state
        type: dict
        description: State dictionary for event emission
    returns:
      type: dict
      description: Event emission result
```

## Scenario-Driven Usage

All runtime node helpers are validated via scenario YAMLs, not traditional tests. Scenarios are defined in `scenarios/` and registered in `scenarios/index.yaml`.

Example scenario (`scenarios/runtime_node_smoke.yaml`):
```yaml
steps:
  - id: merge_state_test
    node: node_runtime
    action: merge_state
    params:
      foo: 1
    expected_result:
      merged: true
      foo: 1
  - id: emit_event_test
    node: node_runtime
    action: emit_event
    params:
      bar: 2
    expected_result:
      event_emitted: true
      bar: 2
```

Each step invokes a dispatch action with parameters and checks the result against the expected output. This ensures all helpers are exercised and regression-safe.

## Adding New Actions
- Add the new helper function to `node.py` and register it in the `DISPATCH_TABLE`.
- Document the action in `dispatch.yaml` (with params and return type).
- Add or update scenario YAMLs to cover the new action.
