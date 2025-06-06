# ONEX Node Migration Milestone Checklist

This document tracks the migration of all ONEX nodes to the new protocol-driven, dependency-injected, DRY, and standards-compliant pattern (as established with the Kafka node).

---

## General Migration Process

1. [ ] **Audit node** for hardcoded strings, direct tool usage, and custom fixtures.
2. [ ] **Move generic tool logic** to shared tools d then update theirectory.

3. [ ] **Refactor node** for dependency injection of all tools.
4. [ ] **Ensure all node run methods accept strongly typed Pydantic models, not dicts.**
5. [ ] **Ensure all interfaces use Protocols.**
6. [ ] **Refactor tests** to use only injected fixtures.
7. [ ] **Centralize all shared fixtures/utilities.** migration milestone checklist
8. [ ] **Use shared scenario test harness.**
9. [ ] **Remove redundant node-specific files.**
10. [ ] **Run and pass all tests.**
11. [ ] **Run parity/standards validation.**
12. [ ] **Replace all string literals** with canonical constants/enums.
13. [ ] **Update documentation.**
14. [ ] **Confirm CI/pre-commit compliance.**

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
| template_node             | [ ]   | [ ]   | [ ]      | [ ]         | [ ]       | [ ]   | [ ]      | [ ]     | [ ]        | [ ]        | [ ]    | [ ]     | [ ] | [ ]|
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