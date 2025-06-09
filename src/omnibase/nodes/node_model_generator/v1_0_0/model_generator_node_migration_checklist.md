# Node Model Generator Migration Checklist (Canonical ONEX Node Standards)

> **NOTE:**
> This checklist tracks the creation and migration of `node_model_generator` to full ONEX node standards. This node will implement contract-to-Pydantic model generation for all referenced `definitions` and `$ref` types in contract.yaml files, enabling standards-compliant, DRY, and automated model generation for all ONEX nodes.

---

## General Migration Steps

- [ ] **Backup and Scaffold**
    - [ ] Backup the initial clone if needed.
    - [ ] Rename all files, classes, and documentation from `model_generator` to `model_generator`.
    - [ ] Update node directory, version, and metadata files accordingly.

- [ ] **Directory and File Structure**
    - [ ] Ensure all canonical directories exist: `models/`, `tools/`, `scenarios/`, `snapshots/`, `node_tests/`, `protocols/`.
    - [ ] Remove any model_generator-specific or placeholder files not relevant to model generator functionality.

- [ ] **Models and Contracts**
    - [ ] Create or update `contract.yaml` to define the input/output state for model generation (e.g., contract path, output directory, options).
    - [ ] Regenerate `models/state.py` and `error_codes.py` from `contract.yaml` using the schema generator node (until the new generator is self-hosting).
    - [ ] Ensure all config models are in `models/` and re-exported in `__init__.py`.
    - [ ] Ensure `node.onex.yaml` is schema-valid and up-to-date.
    - [ ] All model and contract references in code and test harnesses updated to canonical names (no model_generator node references remain).

- [ ] **Tools and Logic**
    - [ ] Implement core logic for parsing contract.yaml and emitting Pydantic models for all referenced `definitions` and `$ref` types.
    - [ ] Refactor helpers to use dependency injection and protocol interfaces as needed.
    - [ ] Add or update tools for YAML parsing, type mapping, and code emission.

- [ ] **Protocols and Interfaces**
    - [ ] Define all interfaces using `Protocol` (not ABC), per interface design rules.
    - [ ] Use strongest possible typing for all protocol methods (Pydantic models, Enums, generics).

- [ ] **Error Codes and Handling**
    - [ ] Define all error codes in `contract.yaml` and regenerate `error_codes.py` (never hardcode or hand-edit).
    - [ ] Reference error codes via canonical Enums/constants in all logic and tests.
    - [ ] Ensure all errors are protocol-compliant and discoverable via introspection.

- [ ] **Introspection and Metadata**
    - [ ] Implement standards-compliant `introspection.py` (dependency-injected metadata loader, protocol-compliant output).
    - [ ] Expose all scenarios, error codes, and contract fields via introspection.

- [ ] **Code and Test Harness Canonicalization**
    - [ ] All code, test harnesses, and fixtures reference only canonical model generator models and node names.
    - [ ] All model_generator node references removed from code and tests.

- [ ] **Testing and Scenarios**
    - [ ] Update or create scenario YAMLs and snapshot YAMLs to cover all key model generator behaviors (contract parsing, model emission, error handling, config edge cases, etc.).
    - [ ] Register all scenarios in `scenarios/index.yaml`.
    - [ ] Add scenario YAMLs for all key behaviors.
    - [ ] Add snapshot YAMLs for regression testing in `snapshots/`.
    - [ ] Ensure all tests use only injected fixtures and registry-driven data.
    - [ ] Remove any placeholder or model_generator scenarios/tests that are not relevant to model generator functionality.

- [ ] **Documentation**
    - [ ] Update `README.md` to document structure, standards, extensibility, and scenario-driven testing (see Kafka node for thoroughness).
    - [ ] Document any deviations from canonical standards and justify them.

- [ ] **Validation and Compliance**
    - [ ] Run and pass all tests (mock, integration, regression).
    - [ ] Run parity/standards validation (`parity_validator_node`).
    - [ ] Confirm CI/pre-commit compliance.

---

## References
- See `node_kafka_event_bus` for backend/event bus logic, degraded mode, and advanced configuration patterns.
- See `model_generator_node` for canonical structure, scenario-driven testing, and documentation patterns.
- See `docs/migration_milestone_checklist.md` for the unified migration process.
- See `.cursor/rules/` for enforced standards on interface design, typing, and testing.

---

**All items must be checked and justified before migration is considered complete.** 