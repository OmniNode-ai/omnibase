# Node Manager Migration & Completion Checklist (Canonical ONEX Node Standards)

> This checklist tracks all work required to complete the new node_manager node, unifying node generation, artifact generation, and orchestration. All steps must be completed for full standards compliance and maintainability.

---

## 1. Template Preparation & Tokenization
- [x] Clone template node structure into node_manager/template
- [x] Add tokenization table to template/README.md
- [x] Remove all auto-generated files from the template (models/state.py, error_codes.py, introspection.py)
- [ ] Tokenize all template files and directories (replace template-specific names with tokens)
- [ ] Document all tokens in template/README.md

## 2. Migration of Functionality from Existing Nodes
- [ ] Audit `node_manager_node`, `node_model_generator`, and `schema_generator_node` for unique business logic, tools, and protocols
- [ ] Refactor and merge relevant logic into node_manager (tools/, protocols/, main node, etc.)
- [ ] Ensure all migrated logic is standards-compliant and protocol-driven
- [ ] Remove or deprecate the old nodes after migration is complete
- [ ] Document any changes or deviations in node_manager/README.md

## 3. Artifact Generation Design & Implementation
- [ ] Design code generation logic for:
    - [ ] Pydantic models (models/state.py, models/__init__.py)
    - [ ] Error codes (error_codes.py)
    - [ ] Introspection (introspection.py)
    - [ ] Registry (registry/registry_{NODE_NAME}.py)
    - [ ] Protocols (protocols/*.py)
    - [ ] Scenarios (scenarios/scenario_*.yaml, scenarios/index.yaml)
    - [ ] Snapshots (snapshots/snapshot_*.yaml)
    - [ ] node.onex.yaml (from template + user input)
    - [ ] README.md (boilerplate sections)
    - [ ] CLI/entrypoint boilerplate (main(), arg parsing)
    - [ ] Test harness/fixtures (node_tests/conftest.py, test_scenarios.py)
- [ ] Implement code generation logic for each artifact
- [ ] Add commands or API to node_manager for generating each artifact
- [ ] Document code generation process in node_manager/README.md

## 4. Manual Business Logic & Customization
- [ ] Implement or migrate business logic in node.py (reducer/orchestrator pattern)
- [ ] Integrate or stub custom tools/handlers as needed
- [ ] Add unique documentation or usage examples (beyond what can be templated)
- [ ] Ensure contract.yaml is hand-authored and up to date

## 5. Scenario & Test Harness Updates
- [ ] Update or add scenarios for all major workflows (node creation, model generation, error cases, etc.)
- [ ] Ensure all tests use registry-driven, protocol-first, fixture-injected patterns
- [ ] Add/verify scenario-driven regression tests and snapshots

## 6. Documentation & Standards Compliance
- [ ] Update node_manager/README.md to document new structure, tokenization, and extensibility
- [ ] Document any deviations from canonical standards and justify them
- [ ] Ensure all files, directories, and code artifacts follow ONEX naming conventions

## 7. Final Validation & CI
- [ ] Run and pass all tests (mock, integration, regression)
- [ ] Run parity/standards validation (parity_validator_node)
- [ ] Confirm CI/pre-commit compliance
- [ ] Remove or mark as deprecated the old node_manager_node, node_model_generator, and schema_generator_node after migration is complete

---

## References
- See node_kafka_event_bus for canonical structure, scenario-driven testing, and extensibility patterns.
- See docs/migration_milestone_checklist.md for the unified migration process.
- See .cursor/rules/ for enforced standards on interface design, typing, and testing.

---

**All items must be checked and justified before node_manager is considered complete.** 