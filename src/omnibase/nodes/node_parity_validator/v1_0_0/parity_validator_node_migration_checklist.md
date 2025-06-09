# Node Parity Validator Migration Checklist (Canonical ONEX Node Standards)

> **NOTE:**
> Migration is currently **paused** pending a refactor of the schema generator node. The generator must be enhanced to emit Pydantic models for all contract `definitions` and `$ref` types (not just root input/output state). This is required for standards compliance and to unblock further node migrations. See the master migration plan for details.

This checklist tracks the migration of `node_parity_validator` to full ONEX node standards, using `template_node` and `node_kafka_event_bus` as canonical references.

---

## General Migration Steps

- [x] **Backup and Scaffold**
    - [x] Move legacy `parity_validator_node` to backup (if applicable).
    - [x] Clone `template_node` to `node_parity_validator`.
    - [x] Copy core parity validator logic (engine, helpers, config, state) to canonical `tools/` and `models/`.

- [x] **Directory and File Structure**
    - [x] Ensure all canonical directories exist: `models/`, `tools/`, `scenarios/`, `snapshots/`, `node_tests/`, `protocols/`.
    - [x] Remove any non-canonical or legacy files not justified by standards.
    - [x] Remove any template-specific files (e.g., `template_node_contract.yaml`), placeholder scenarios, or tools not relevant to parity validator functionality.

- [x] **Models and Contracts**
    - [x] Update or create `contract.yaml` to match parity validator node's protocol, traceability fields, and all required input/output state and error codes.
    - [x] Regenerate `models/state.py` and `error_codes.py` from `contract.yaml` using the schema generator node. **Never edit these files by hand.**
    - [x] Ensure all config models (e.g., `ParityValidatorConfig`) are in `models/` and re-exported in `__init__.py`.
    - [x] Ensure `node.onex.yaml` is schema-valid and up-to-date.
    - [x] All model and contract references in code and test harnesses updated to canonical names (no template node references remain).
    - [ ] **BLOCKED:** The schema generator does not currently emit Pydantic models for all contract `definitions` and `$ref` types (e.g., `DiscoveredNode`, `NodeValidationResult`). Migration is paused until the generator is refactored to support this.

- [x] **Tools and Helpers**
    - [x] Move all parity validator business logic (engine, output handler, formatters) to `tools/`.
    - [x] Refactor helpers to use dependency injection and protocol interfaces (see Kafka node for backend selection pattern).
    - [x] Add a stub `tool_backend_selection.py` if backend selection is not required, with documentation.

- [x] **Handlers and Registry**
    - [x] Move or refactor output format handlers to canonical locations (e.g., `handlers/`, `tools/`).
    - [x] Ensure handler registry uses protocol-first, registry-driven pattern (see Kafka node for event bus registry).

- [x] **Protocols and Interfaces**
    - [x] Define all interfaces using `Protocol` (not ABC), per interface design rules.
    - [x] Use strongest possible typing for all protocol methods (Pydantic models, Enums, generics).

- [x] **Error Codes and Handling**
    - [x] Define all error codes in `contract.yaml` and regenerate `error_codes.py` (never hardcode or hand-edit).
    - [x] Reference error codes via canonical Enums/constants in all logic and tests.
    - [x] Ensure all errors are protocol-compliant and discoverable via introspection.

- [x] **Introspection and Metadata**
    - [x] Implement standards-compliant `introspection.py` (dependency-injected metadata loader, protocol-compliant output).
    - [x] Expose all scenarios, error codes, and contract fields via introspection.

- [x] **Code and Test Harness Canonicalization**
    - [x] All code, test harnesses, and fixtures reference only canonical parity validator models and node names.
    - [x] All template node references removed from code and tests.

- [ ] **Testing and Scenarios**
    - [ ] Update all scenario YAMLs and snapshot YAMLs to use canonical node/model names and structure.
    - [ ] Migrate or rewrite tests to use canonical scenario-driven, fixture-injected, protocol-first harness (see Kafka node and standards).
    - [ ] Register all scenarios in `scenarios/index.yaml`.
    - [ ] Add scenario YAMLs for all key parity validator behaviors (output formats, error handling, config edge cases, etc.).
    - [ ] Add snapshot YAMLs for regression testing in `snapshots/`.
    - [ ] Ensure all tests use only injected fixtures and registry-driven data.
    - [ ] Remove any placeholder or template scenarios/tests that are not relevant to parity validator functionality.

- [ ] **Documentation**
    - [ ] Update `README.md` to document structure, standards, backend selection (if any), extensibility, and scenario-driven testing (see Kafka node for thoroughness).
    - [ ] Document any deviations from canonical standards and justify them.

- [ ] **Validation and Compliance**
    - [ ] Run and pass all tests (mock, integration, regression).
    - [ ] Run parity/standards validation (`parity_validator_node`).
    - [ ] Confirm CI/pre-commit compliance.

---

## References
- See `node_kafka_event_bus` for backend/event bus logic, degraded mode, and advanced configuration patterns.
- See `template_node` for canonical structure, scenario-driven testing, and documentation patterns.
- See `docs/migration_milestone_checklist.md` for the unified migration process.
- See `.cursor/rules/` for enforced standards on interface design, typing, and testing.

---

**All items must be checked and justified before migration is considered complete.** 