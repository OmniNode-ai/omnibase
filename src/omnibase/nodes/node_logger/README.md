# Logger Node (ONEX Canonical)

This node implements the canonical ONEX logger pattern, providing structured, multi-format logging with full standards compliance, registry-driven dependency injection, and scenario-driven validation. It serves as the reference for all logging and output-format nodes in the ONEX ecosystem.

## Key Features
- **Reducer Pattern:** Implements `.run()` and `.bind()` lifecycle. All business logic is delegated to protocol-typed helpers in `tools/`.
- **Registry-Driven Dependency Injection:** Uses a canonical registry (`registry/registry_node_logger.py`) for all tool resolution, supporting per-scenario overrides and extensibility.
- **Multi-Format Output:** Supports JSON, YAML, Markdown, Text, and CSV log output via pluggable format tools.
- **Scenario-Driven Validation:** All validation and regression testing is scenario-driven. Scenarios are defined in `scenarios/index.yaml` and exposed via introspection.
- **Extensible Output Fields:** Output model includes a dedicated `LoggerOutputField` for future extensibility.
- **Error Codes:** Canonical error codes are defined in `error_codes.py` and exposed via introspection.
- **Introspection:** Standards-compliant introspection via `introspection.py`, exposing node metadata, contract, CLI arguments, capabilities, and scenario registry.

## Usage

### CLI Introspection
```bash
poetry run onex run node_logger --introspect
```
Prints full node contract, metadata, CLI arguments, and available scenarios as JSON.

### Scenario Discovery
```bash
poetry run onex run node_logger --args='["--run-scenario", "smoke"]'
```
Prints the scenario config for the given scenario ID from the node's scenario registry.

### Direct CLI Invocation
```bash
poetry run onex run node_logger --args='["--health-check"]'
```

### Serve/Daemon Mode
```bash
poetry run python -m omnibase.nodes.node_logger.v1_0_0.node --serve
# or
poetry run onex run node_logger --args='["--serve"]'
```

## Developer Notes
- **Input/Output Models:** Defined in `models/state.py` (`LoggerInputState`, `LoggerOutputState`, `LoggerOutputField`).
- **Config Model:** See `models/logger_output_config.py` for output configuration options.
- **Protocol Interfaces:** All helpers/tools use Protocols (see `protocols/`).
- **Registry Pattern:** All tools are resolved via the registry (`registry/registry_node_logger.py`). To override or extend, provide a custom tool collection per scenario.
- **Business Logic:** All logic is in protocol-typed helpers in `tools/` (e.g., `tool_logger_engine.py`, `tool_text_format.py`, etc.).
- **Extending Output Formats:** Add a new tool in `tools/` and register it in the registry.

## Scenario Runner (Canonical)

All validation and regression testing is performed by the scenario runner (`node_tests/test_scenarios.py`).
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
poetry run pytest src/omnibase/nodes/node_logger/v1_0_0/node_tests/ -v
```
To regenerate all snapshots:
```bash
poetry run pytest src/omnibase/nodes/node_logger/v1_0_0/node_tests/ --regenerate-snapshots -v
```

## Scenario YAML Structure

Each scenario YAML defines a test case for the node. All scenarios must be registered in `scenarios/index.yaml`.

**Canonical scenario YAML:**
```yaml
---
scenario_name: "Smoke Test"
description: "Minimal scenario to validate the logger runs and returns success."
scenario_type: "smoke"
tags: [onex, node_logger, smoke]
version: "v1.0.0"
created_by: "auto"
---
chain:
  - input:
      version: {major: 1, minor: 0, patch: 0}
      log_level: info
      message: "LoggerNode ran successfully."
      output_format: json
    expect:
      status: success
      message: "LoggerNode ran successfully."
      formatted_log: "..."
      output_format: json
      timestamp: "..."
      log_level: info
      entry_size: ...
      output_field:
        backend: inmemory
```

**Required fields:**
- `scenario_name`, `description`, `scenario_type`, `tags`, `version`, `created_by`
- `chain`: List of steps, each with `input` and `expect` blocks matching the canonical input/output models

**Scenario Registry (index.yaml):**
```yaml
scenarios:
  - id: smoke
    description: "Minimal scenario to validate the logger runs and returns success."
    entrypoint: scenarios/scenario_smoke.yaml
    expected_result: success
```

All scenarios must be listed in `index.yaml` for discovery and introspection.

## Snapshotting and Regression
- Snapshots are stored in `snapshots/snapshot_<scenario_id>.yaml`.
- The scenario runner will fail if the output does not match the snapshot, ensuring regression safety.
- Snapshots are always schema-valid and use canonical serialization.

## Supported Output Formats
- **JSON:** Machine-readable, default format.
- **YAML:** Human-friendly, supports comments.
- **Markdown:** For documentation and reporting.
- **Text:** Plain text, for logs and CLI output.
- **CSV:** Tabular data, for export and analysis.

To add a new format, implement a tool in `tools/` and register it in the registry.

## Extensibility
- **Add Output Formats:** Create a new tool in `tools/` and register it in the registry.
- **Extend Output Fields:** Add fields to `LoggerOutputField` in `models/state.py`.
- **Override Tools:** Provide a custom tool collection in the scenario config or registry.

## Backend Selection
- The logger node includes a stub backend selection tool (`tools/tool_backend_selection.py`) to satisfy protocol requirements. For most use cases, the in-memory backend is sufficient. For real backend/event bus logic, see the Kafka node.

## Protocol Compliance and Edge Cases
- All input/output state models use canonical Pydantic models and Enums.
- All protocol and interface definitions use the strongest possible typing.
- Error codes are referenced from `error_codes.py` and never hardcoded.
- All scenarios are registered in `scenarios/index.yaml` and exposed via introspection.
- Traceability fields (event_id, correlation_id, node_name, node_version, timestamp) are present in input/output models and contract.
- Edge case handling (e.g., degraded mode, async/sync bridging) should be implemented as needed and documented here.

## Naming Standards (Canonical)
All files (except for explicit exceptions below) must be prefixed with the name of their immediate parent directory, using all-lowercase and underscores. See `.cursor/rules/standards.mdc` for authoritative rules.

## References
- See `introspection.py` for the full introspection implementation.
- See `contract.yaml` for the canonical contract and model definitions.
- See `error_codes.py` for error code enums.
- See the Kafka node for advanced backend/event bus configuration and event replay patterns.
- See project rules for interface, typing, and testing standards.
- See `v1_0_0/README.md` for version-specific notes and implementation details.