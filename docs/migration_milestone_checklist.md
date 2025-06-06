# ONEX Node Migration Milestone Checklist

This document tracks the migration of all ONEX nodes to the new protocol-driven, dependency-injected, DRY, and standards-compliant pattern (as established with the Kafka node).

---

## General Migration Process

1. [ ] **Audit node** for hardcoded strings, direct tool usage, and custom fixtures.
2. [ ] **Move generic tool logic** to shared tools directory.
3. [ ] **Refactor node** for dependency injection of all tools.
4. [ ] **Ensure all node run methods accept strongly typed Pydantic models, not dicts.**
5. [ ] **Ensure all interfaces use Protocols.**
6. [ ] **Refactor tests** to use only injected fixtures.
7. [ ] **Centralize all shared fixtures/utilities.**
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