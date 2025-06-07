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
poetry run onex run node_template --introspect
```
Prints full node contract, metadata, CLI arguments, and available scenarios as JSON.

### Scenario Discovery
```bash
poetry run onex run node_template --args='["--run-scenario", "smoke"]'
```
Prints the scenario config for the given scenario ID from the node's scenario registry.

## Usage Modes

### 1. Direct CLI Invocation (Short-lived)

You can invoke the node directly for health checks, scenario runs, or direct input processing. In this mode, the node runs the requested operation and exits.

Example:

```bash
poetry run onex run node_template --args='["--health-check"]'
```

### 2. Event-Driven (Serve/Daemon) Mode

For event-driven workflows (e.g., using the ONEX CLI to publish events), the node **can be run as a persistent process** that subscribes to the event bus and handles events as they arrive. In the template node, the backend is always in-memory (see Backend Selection Logic below). For real backend logic, see the Kafka node.

#### Starting the Node in Serve Mode

```bash
poetry run python -m omnibase.nodes.node_template.v1_0_0.node --serve
```

Or, if integrated with the ONEX CLI:

```bash
poetry run onex run node_template --args='["--serve"]'
```

This will start the node as a persistent process, subscribing to the event bus and handling events as they arrive.

## Developer Notes
- Input/output state models are defined in `models/state.py` and must use canonical Pydantic models and Enums.
- All protocol and interface definitions must use the strongest possible typing (see project rules).
- Error codes must be referenced from `error_codes.py` and never hardcoded.
- All scenarios must be registered in `scenarios/index.yaml` and exposed via introspection.

## Scenario Runner (Canonical)

All validation and regression testing is performed by the scenario runner (`scenarios/test_scenarios.py`).

- Loads all scenarios registered in `scenarios/index.yaml`.
- For each scenario:
  - Loads the scenario YAML and input chain.
  - Runs the node with the scenario input.
  - Compares the output to the canonical snapshot in `snapshots/snapshot_<scenario_id>.yaml`.
  - If the snapshot does not exist, it is created automatically.
  - Supports `--regenerate-snapshots` (or `REGENERATE_SNAPSHOTS=1`) to update all snapshots with current outputs.
- All outputs are validated against the canonical output model and serialized with Enums as strings.

### Running the Scenario Runner
```bash
poetry run pytest src/omnibase/nodes/node_template/v1_0_0/scenarios/test_scenarios.py -v
```
To regenerate all snapshots:
```bash
poetry run pytest src/omnibase/nodes/node_template/v1_0_0/scenarios/test_scenarios.py --regenerate-snapshots -v
```

## Scenario YAML Structure

Each scenario YAML defines a test case for the node. All scenarios must be registered in `scenarios/index.yaml`.

**Canonical scenario YAML:**
```yaml
---
scenario_name: "Smoke Test"
description: "Minimal scenario to validate the reducer runs and returns success."
scenario_type: "smoke"
tags: [onex, node_template, smoke]
version: "v1.0.0"
created_by: "auto"
---
chain:
  - input:
      version: {major: 1, minor: 0, patch: 0}
      output_field: null
    expect:
      status: success
      message: "NodeTemplate ran successfully."
      output_field:
        data:
          processed: test
```

**Required fields:**
- `scenario_name`, `description`, `scenario_type`, `tags`, `version`, `created_by`
- `chain`: List of steps, each with `input` and `expect` blocks matching the canonical input/output models

**Scenario Registry (index.yaml):**
```yaml
scenarios:
  - id: smoke
    description: "Minimal scenario to validate the reducer runs and returns success."
    entrypoint: scenarios/scenario_smoke.yaml
    expected_result: success
```

All scenarios must be listed in `index.yaml` for discovery and introspection.

## Snapshotting and Regression
- Snapshots are stored in `snapshots/snapshot_<scenario_id>.yaml`.
- The scenario runner will fail if the output does not match the snapshot, ensuring regression safety.
- Snapshots are always schema-valid and use canonical serialization.

## Backend Selection Logic

The template node includes a canonical stub backend selection tool in `tools/tool_backend_selection.py` to satisfy protocol requirements for backend selection. This stub always returns an in-memory event bus and is sufficient for most nodes. 

**Note:** Only nodes with real backend logic (such as Kafka) should implement a real backend selection tool. For most nodes, the provided stub is sufficient and should not be replaced unless backend selection is required.

See `tools/tool_backend_selection.py` for details and extension guidance.

## Protocol Compliance and Edge Cases

- All input/output state models are defined in `models/state.py` and use canonical Pydantic models and Enums.
- All protocol and interface definitions must use the strongest possible typing (see project rules).
- Error codes must be referenced from `error_codes.py` and never hardcoded.
- All scenarios must be registered in `scenarios/index.yaml` and exposed via introspection.
- Edge case handling (e.g., degraded mode, async/sync bridging) should be implemented as needed by the node's business logic and documented in the node's README.
- Backend/event bus configuration is node-specific and not included in the template node; see the Kafka node for a full example.

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
- See the Kafka node for advanced backend/event bus configuration and event replay patterns.
- See project rules for interface, typing, and testing standards.