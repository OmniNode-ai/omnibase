# Template Node (ONEX Canonical)

The Template Node implements the canonical ONEX reducer pattern and serves as the reference for all new nodes.

## Key Features
- **Reducer Pattern:** Implements `.run()` and `.bind()` lifecycle. All business logic is delegated to inline handlers or runtime helpers.
- **Introspection:** Standards-compliant introspection via `introspection.py`, exposing node metadata, contract, CLI arguments, capabilities, and scenario registry.
- **Scenario-Driven Validation:** All validation and testing is scenario-driven. Scenarios are defined in `scenarios/index.yaml` and exposed via introspection.
- **Error Codes:** Canonical error codes are defined in `error_codes.py` and exposed via introspection.

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
poetry run pytest src/omnibase/nodes/template_node/v1_0_0/scenarios/test_scenarios.py -v
```
To regenerate all snapshots:
```bash
poetry run pytest src/omnibase/nodes/template_node/v1_0_0/scenarios/test_scenarios.py --regenerate-snapshots -v
```

## Scenario YAML Structure

Each scenario YAML defines a test case for the node. All scenarios must be registered in `scenarios/index.yaml`.

**Canonical scenario YAML:**
```yaml
---
scenario_name: "Smoke Test"
description: "Minimal scenario to validate the reducer runs and returns success."
scenario_type: "smoke"
tags: [onex, template_node, smoke]
version: "v1.0.0"
created_by: "auto"
---
chain:
  - input:
      version: {major: 1, minor: 0, patch: 0}
      output_field: null
    expect:
      status: success
      message: "TemplateNode ran successfully."
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

## References
- See `introspection.py` for the full introspection implementation.
- See `template_node_milestone1_checklist.md` for milestone requirements.
- See project rules for interface, typing, and testing standards. 