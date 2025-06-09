# ONEX Node Migration Milestone Checklist

This document tracks the migration of all ONEX nodes to the new protocol-driven, dependency-injected, DRY, and standards-compliant pattern (as established with the Kafka node).

---

## Canonical Scenario Configuration Pattern (Registry/DI)

**All scenario configurations must use a declarative, type-safe ToolCollection for registry-driven dependency injection.**

- Scenarios specify a `registry_tools` field, which is a ToolCollection mapping tool names to the actual tool classes or instances to be used for that scenario.
- This enables fully declarative, per-scenario dependency injection: you can see exactly which implementation is used for each tool in each scenario.
- No string-based "real"/"mock"/"mixed" selection is allowed; the scenario config is the source of truth for all tool wiring.
- The scenario harness and registry must use this ToolCollection for all tool resolution.

**Example scenario YAML:**
```yaml
scenario_name: "Kafka Event Bus Custom Registry"
registry_tools:
  event_bus: !python/name:omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus.KafkaEventBus
  logger: !python/name:omnibase.nodes.node_logger.v1_0_0.tools.tool_text_format.ToolTextFormat
  backend_selection: !python/name:omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_backend_selection.ToolBackendSelection
  output_field_tool: !python/name:omnibase.tools.tool_compute_output_field.tool_compute_output_field
# ... rest of scenario ...
```

- The scenario harness will instantiate the registry with this ToolCollection and inject it into the node.
- This pattern is required for all new and migrated scenarios.

---

## General Migration Process

1. [x] **Audit node** for hardcoded strings, direct tool usage, and custom fixtures.
2. [x] **Move generic tool logic** to shared tools d then update theirectory.
3. [x] **Refactor node** for dependency injection of all tools.
4. [x] **Ensure all node run methods accept strongly typed Pydantic models, not dicts.**
5. [x] **Ensure all interfaces use Protocols.**
6. [x] **Refactor tests** to use only injected fixtures.
7. [x] **Centralize all shared fixtures/utilities.** migration milestone checklist
8. [x] **Use shared scenario test harness.**
9. [x] **Remove redundant node-specific files.**
10. [x] **Run and pass all tests.**
11. [x] **Run parity/standards validation.**
12. [x] **Replace all string literals** with canonical constants/enums.
13. [x] **Update documentation.**
14. [x] **Confirm CI/pre-commit compliance.**

---

## Template Node Canonicalization Checklist

To ensure the template node is the canonical, standards-compliant reference for all ONEX node generation, complete the following steps:

1. [x] **Migrate to models/ directory:**
    - Ensure all models are in a `models/` directory (no single `models.py` file).
    - All input/output state models must be auto-generated from the contract.
2. [x] **Add tools/ directory:**
    - Create a `tools/` directory (add a placeholder if no tools yet).
    - Move any node-specific helpers or business logic here.
3. [x] **Ensure snapshots/ directory and scenario regression:**
    - If scenario-driven regression testing is used, ensure a `snapshots/` directory exists and is documented.
    - All scenarios must have corresponding regression outputs if applicable.
4. [x] **Use canonical test harness and fixtures:**
    - All scenario and regression tests must use the shared scenario test harness and canonical fixtures.
    - Remove any node-specific test logic outside the harness.
5. [x] **Canonical logging and debug instrumentation:**
    - Replace all `print` or ad-hoc logging with the canonical logging/event system (e.g., `emit_log_event_sync`).
6. [x] **Contract-driven model and error code generation:**
    - Ensure all output field models and error codes are generated from `contract.yaml`.
    - Update all code to reference generated models and error codes only.
7. [x] **Canonical import and path resolution:**
    - Use standards-compliant import paths for all models, fixtures, and tools.
    - Use the node class's `__file__` attribute for path resolution where needed.
8. [x] **Audit and update README/documentation:**
    - Update the README to document structure, standards, and any deviations.
    - Follow the canonical documentation pattern.
9. [x] **Contract and introspection compliance:**
    - Ensure `contract.yaml`, `node.onex.yaml`, and `introspection.py` are schema-valid and up-to-date.
10. [x] **Error handling and introspection:**
    - All error codes must be protocol-compliant and discoverable via introspection.
    - Reference all error codes via canonical constants/enums.
11. [x] **Traceability fields:**
    - Confirm all required traceability fields (event_id, correlation_id, node_name, node_version, timestamp) are present in input/output models and contract.
12. [x] **Node generator test:**
    - After updating the template node, generate a new node using the node generator and verify it is standards-compliant and passes all tests.
13. [x] **Introspection metadata loader injection:**
    - Refactor introspection.py to require dependency injection for the metadata loader (do not instantiate internally).
    - Implement get_metadata_loader as an abstract classmethod in the mixin, and require all nodes to provide/inject the loader.
    - Document this pattern in the node and standards as the canonical approach.

### Kafka Parity Tasks

To ensure the template node is fully in parity with the Kafka node, complete the following additional tasks:

1. [x] **Backend Selection Tool Parity**
    - If the Kafka node has a `tool_backend_selection.py` in `tools/`, ensure the template node has a stub or placeholder (even if only a minimal Protocol-compliant stub, as in its `conftest.py`).
    - Document in the template node's README and code comments that real backend selection logic is only required for nodes with actual backend logic (like Kafka).
2. [x] **Model Output Field Parity**
    - Ensure the template node's output field model (`ModelTemplateOutputField`) is as extensible as the Kafka node's (`ModelEventBusOutputField`), supporting optional fields and future extension.
    - Add a comment or example for extending output fields in the template node's models.
3. [x] **models/__init__.py Parity**
    - Update the template node's `models/__init__.py` to match the Kafka node's pattern, re-exporting all canonical models and including a comment about adding new models as needed.
4. [x] **Scenario and Snapshot Coverage**
    - Ensure the template node's `scenarios/` and `snapshots/` directories cover all canonical scenario types present in the Kafka node (e.g., degraded mode, async, backend-specific, etc.), or document why not applicable.
5. [x] **Test Fixture and Harness Parity**
    - Double-check that all fixtures in `conftest.py` are present and named consistently, and that the test harness usage matches the Kafka node's pattern.
    - If the Kafka node uses any additional fixtures or test setup, add stubs or documentation in the template node.
6. [x] **README and Documentation Parity**
    - Ensure the template node's README(s) document all canonical patterns, including backend selection, extensibility, and scenario-driven testing, as thoroughly as the Kafka node.
7. [x] **Contract and Model Comments**
    - Add comments in the template node's `contract.yaml` and models about how to extend for new fields, error codes, or backend logic, mirroring any such guidance in the Kafka node.
8. [x] **Remove Redundant Files**
    - Remove any files in the template node that are not present in the Kafka node and are not justified by standards (e.g., legacy constants, unused helpers).
9. [x] **Introspection metadata loader injection**
    - Ensure the template node's introspection.py uses dependency injection for the metadata loader, not instantiation.
    - The mixin should enforce this via an abstract classmethod, and the loader must be set externally.

---

## Nodes to Migrate (Recommended Order)

### 1. **template_node**
- Rationale: Serves as the canonical example for all future nodes; migration here will clarify patterns for others.

### 2. **logger_node**
- Rationale: Common utility node, likely to benefit from DRY/shared logic.

### 3. **docstring_generator_node**
- Rationale: Simple business logic, good for early migration.

### 4. **node_manager_node**
- Rationale: Central to node orchestration; migration will help standardize management patterns.

### 5. **node_registry_node**
- Rationale: Registry logic is core to ONEX; should be protocol-compliant.

### 6. **registry_loader_node**
- Rationale: Handles registry loading, should use shared tools and patterns.

### 7. **node_tree_generator**
- Rationale: Tree generation logic can benefit from shared output field tools.

### 8. **stamper_node**
- Rationale: Complex, but migration will help enforce standards for critical nodes.

### 9. **schema_generator_node**
- Rationale: Schema logic should be protocol-driven and DRY.

### 10. **node_runtime**
- Rationale: Core runtime logic, migrate after patterns are solidified.

### 11. **node_scenario_runner**
- Rationale: Scenario runner should use shared test harness and fixtures.

### 12. **parity_validator_node**
- Rationale: Validation logic should be last, as it may depend on all other nodes being compliant.

---

## Migration Progress Table

| Node                      | Audit | Tools | Refactor | Model Input | Protocols | Tests | Fixtures | Harness | Redundancy | Tests Pass | Parity | Strings | Docs | CI |
|---------------------------|-------|-------|----------|-------------|-----------|-------|----------|---------|------------|------------|--------|---------|-----|----|
| template_node             | [x]   | [x]   | [x]      | [x]         | [x]       | [x]   | [x]      | [x]     | [x]        | [x]        | [x]    | [x]     | [x] | [x]|
| logger_node               | [ ]   | [ ]   | [ ]      | [ ]         | [ ]       | [ ]   | [ ]      | [ ]     | [ ]        | [ ]        | [ ]    | [ ]     | [ ] | [ ]|
| docstring_generator_node  | [ ]   | [ ]   | [ ]      | [ ]         | [ ]       | [ ]   | [ ]      | [ ]     | [ ]        | [ ]        | [ ]    | [ ]     | [ ] | [ ]|
| node_manager_node         | [ ]   | [ ]   | [ ]      | [ ]         | [ ]       | [ ]   | [ ]      | [ ]     | [ ]        | [ ]        | [ ]    | [ ]     | [ ] | [ ]|
| node_registry_node        | [ ]   | [ ]   | [ ]      | [ ]         | [ ]       | [ ]   | [ ]      | [ ]     | [ ]        | [ ]        | [ ]    | [ ]     | [ ] | [ ]|
| registry_loader_node      | [ ]   | [ ]   | [ ]      | [ ]         | [ ]       | [ ]   | [ ]      | [ ]     | [ ]        | [ ]        | [ ]    | [ ]     | [ ] | [ ]|
| node_tree_generator       | [ ]   | [ ]   | [ ]      | [ ]         | [ ]       | [ ]   | [ ]      | [ ]     | [ ]        | [ ]        | [ ]    | [ ]     | [ ] | [ ]|
| stamper_node              | [ ]   | [ ]   | [ ]      | [ ]         | [ ]       | [ ]   | [ ]      | [ ]     | [ ]        | [ ]        | [ ]    | [ ]     | [ ] | [ ]|
| schema_generator_node     | [ ]   | [ ]   | [ ]      | [ ]         | [ ]       | [ ]   | [ ]      | [ ]     | [ ]        | [ ]        | [ ]    | [ ]     | [ ] | [ ]|
| node_runtime              | [ ]   | [ ]   | [ ]      | [ ]         | [ ]       | [ ]   | [ ]      | [ ]     | [ ]        | [ ]        | [ ]    | [ ]     | [ ] | [ ]|
| node_scenario_runner      | [ ]   | [ ]   | [ ]      | [ ]         | [ ]       | [ ]   | [ ]      | [ ]     | [ ]        | [ ]        | [ ]    | [ ]     | [ ] | [ ]|
| parity_validator_node     | [ ]   | [ ]   | [ ]      | [ ]         | [ ]       | [ ]   | [ ]      | [ ]     | [ ]        | [ ]        | [ ]    | [ ]     | [ ] | [ ]|
| node_kafka_event_bus      | [x]   | [x]   | [x]      | [x]         | [x]       | [x]   | [x]      | [x]     | [x]        | [x]        | [x]    | [x]     | [x] | [x]|

---

**Legend:**
- Each column corresponds to a step in the migration process above.
- Mark each cell with [x] when complete for each node. 

---

## Node Pattern Audit: template_node vs. node_kafka_event_bus

### Audit Date: 2024-06-10

### File/Folder Structure Comparison

| File/Folder         | template_node | node_kafka_event_bus | Notes/Deviations |
|---------------------|:-------------:|:-------------------:|------------------|
| __init__.py         |      ✔️       |         ✔️          |                  |
| contract.yaml       |      ✔️       |         ✔️          |                  |
| error_codes.py      |      ✔️       |         ✔️          |                  |
| introspection.py    |      ✔️       |         ✔️          |                  |
| models/             |      ✔️       |         ❌           | template uses a directory, kafka uses a single file |
| models.py           |      ❌       |         ✔️          | see above |
| node.onex.yaml      |      ✔️       |         ✔️          |                  |
| node.py             |      ✔️       |         ✔️          |                  |
| node_tests/         |      ✔️       |         ✔️          |                  |
| scenarios/          |      ✔️       |         ✔️          |                  |
| snapshots/          |      ✔️       |         ❌           | only in template_node |
| tools/              |      ❌       |         ✔️          | only in kafka node |
| README.md           |      ✔️       |         ✔️          |                  |

### Notable Differences & Analysis

- **models structure:**
  - `template_node` uses a `models/` directory (modular, extensible).
  - `node_kafka_event_bus` uses a single `models.py` file.
  - *Recommendation:* Standardize on the `models/` directory approach for extensibility and consistency across nodes.

- **tools directory:**
  - Present in Kafka node for helper logic, absent in template_node.
  - *Recommendation:* All nodes should include a `tools/` directory (even if empty or with a placeholder) to encourage modular helper/tool logic and future extensibility.

- **snapshots directory:**
  - Present in template_node, absent in Kafka node.
  - *Recommendation:* If snapshot-based testing is a standard, ensure all nodes include a `snapshots/` directory, or clarify/document when it is required.

- **All other core files** (contract.yaml, error_codes.py, introspection.py, node.py, node.onex.yaml, node_tests/, scenarios/, README.md) are present in both nodes and follow the expected pattern.

### General Recommendation

- The Kafka node (`node_kafka_event_bus`) generally follows the intended ONEX node pattern and should be considered the reference for most structural and architectural patterns.
- The template_node should be updated to:
  - Use a `models/` directory (if not already) and avoid single-file `models.py` patterns.
  - Add a `tools/` directory (with a placeholder if no tools yet).
  - Ensure the use of `snapshots/` is documented and consistent across nodes.
- All future nodes should follow this standardized structure for maintainability and clarity.

---

## Canonical Node Migration Checklist (Unified Standard)

This checklist synthesizes the best practices from both `template_node` and `node_kafka_event_bus` to define the canonical ONEX node structure and migration steps. All nodes should be updated to conform to this unified pattern.

### Canonical Node Structure & Practices

1. **models/ directory**
   - Use a `models/` directory with explicit, auto-generated Pydantic models for input/output state.
   - Re-export shared models as needed, but allow for node-specific extensions.
2. **tools/ directory**
   - Include a `tools/` directory for node-specific helpers and business logic (even if empty initially).
3. **snapshots/ directory**
   - Include a `snapshots/` directory for scenario regression outputs if the node uses scenario-driven testing.
4. **error_codes.py**
   - Define a local error code enum in `error_codes.py` (can re-export shared/core codes if needed).
5. **protocols/ directory**
   - Include a `protocols/` directory for protocol interfaces (local or re-exported from shared locations).
6. **introspection.py**
   - Implement a dedicated `introspection.py` with a standards-compliant introspection class.
7. **node.py**
   - Follow the canonical reducer pattern: `.run()`, `.bind()`, event-driven `handle_event`, dependency injection for all tools/protocols.
   - Implement robust event bus selection and degraded mode handling as in the Kafka node.
8. **scenarios/ directory**
   - Use a `scenarios/` directory with YAML scenario files and an `index.yaml` registry.
9. **node_tests/ directory**
   - Include scenario-driven and unit tests in `node_tests/`.
10. **README.md**
    - Provide a detailed, version-specific README and a canonical node-level README, following the Kafka node's documentation pattern.
11. **contract.yaml & node.onex.yaml**
    - Ensure both are present, schema-valid, and up-to-date with the node's models and contract.
12. **Traceability Fields**
    - Include traceability fields (event_id, correlation_id, node_name, node_version, timestamp) in input/output state models and contract where appropriate.
13. **Error Handling**
    - Use local error codes and ensure all errors are protocol-compliant and discoverable via introspection.
14. **Protocols & Dependency Injection**
    - All tools/helpers must be injected via protocol interfaces, supporting easy swapping/mocking.
15. **Scenario Registry & Regression**
    - All scenarios must be registered in `scenarios/index.yaml` and, if using snapshots, have corresponding regression outputs.
16. **Documentation & Standards**
    - Document any deviations from this checklist and justify them in the node's README and/or standards file.

**All future node migrations and new node creations should follow this checklist as the canonical ONEX node standard.**

---

## Parity Validator Logic Migration to node_manager (Unified Standard)

1. [ ] Audit current parity validator logic, protocols, and test coverage
2. [ ] Extract all reusable validation logic, protocols, and models into node_manager (as tools, protocols, or submodules)
3. [ ] Tokenize and generalize parity logic for use with any node type
4. [ ] Update CLI, scenarios, and documentation to use node_manager for all parity/standards validation
5. [ ] Migrate all tests and scenarios, ensuring full coverage and regression protection
6. [ ] Deprecate standalone parity_validator_node (optionally keep a stub for backward compatibility)
7. [ ] Document the new pattern in the master migration plan and node_manager README

Reference: See master_migration_plan.md for canonical steps.

- [x] Tokenize all template files and embed [ONEX_PROMPT] comments (root, protocols, models, tools, registry, tests, scenarios, snapshots are now fully agent-friendly)

---

## node_manager_node: Canonical Protocol, Tool, and Template Refactor (Current Priority)

**Goal:** Refactor all protocols, tools, and templates in node_manager to use canonical Pydantic models, Enums, and strongest possible typing. Ensure all interfaces, templates, and registry logic are model-driven, protocol-first, and agent/generator-friendly.

### Canonical Refactor Checklist

1. **Inventory and Audit**
    - [ ] List all protocol files in `src/omnibase/nodes/node_manager/v1_0_0/protocols/`
    - [ ] List all tool files in `src/omnibase/nodes/node_manager/v1_0_0/tools/`
    - [ ] List all template files in `src/omnibase/nodes/node_manager/template/`
    - [ ] Identify any use of `dict`, `str`, or other primitives for domain data in method signatures or template tokens.

2. **Model and Enum Definition**
    - [ ] For each protocol/tool, define or update Pydantic models in `models/` for all arguments and return values.
    - [ ] Define Enums in a central `enums/` module for any fixed sets of options (e.g., template types, output formats).
    - [ ] Ensure all template context and output fields are represented as models/enums.

3. **Protocol Refactor**
    - [ ] Update all protocol method signatures to use the new models and enums.
    - [ ] Add/Update docstrings to document all types, generics, and expected usage.
    - [ ] Remove any use of `dict`, `str`, or other primitives for domain-specific data.

4. **Tool Implementation Refactor**
    - [ ] Update all tool classes to implement the updated protocols.
    - [ ] Refactor internal logic to use models/enums instead of primitives.
    - [ ] Ensure all file paths use `Path` (not `str`).

5. **Template Refactor**
    - [ ] Audit all template files for token usage.
    - [ ] Ensure all tokens correspond to fields in a canonical Pydantic model (e.g., `ModelTemplateContext`).
    - [ ] Add or update `[ONEX_PROMPT]` comments to guide future customization and agent-driven generation.
    - [ ] Remove any hardcoded or ambiguous tokens; all must be model-driven.

6. **Registry and Injection**
    - [ ] Update registry logic to use the new protocols and models.
    - [ ] Ensure all scenario harnesses and test fixtures inject dependencies via the updated registry.

7. **Testing**
    - [ ] Update or write tests to use the new models and protocol contracts.
    - [ ] Ensure all fixtures and test harnesses are registry-driven and protocol-first.
    - [ ] Add/Update tests for template rendering, model validation, and protocol compliance.

8. **Documentation**
    - [ ] Update README(s) to document the new models, enums, and protocol patterns.
    - [ ] Document any deviations or open questions.

---

# (The rest of the checklist continues below as before) 