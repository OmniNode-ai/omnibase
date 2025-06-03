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
