# Node Manager Migration & Completion Checklist (Canonical ONEX Node Standards)

> This checklist tracks all work required to complete the new node_manager node, unifying node generation, artifact generation, and orchestration. All steps must be completed for full standards compliance and maintainability.

---

## 1. Template Preparation & Tokenization
- [x] Clone template node structure into node_manager/template
- [x] Add tokenization table to template/README.md
- [x] Remove all auto-generated files from the template (models/state.py, error_codes.py, introspection.py)
- [x] Tokenize all template files and directories (replace template-specific names with tokens)
- [x] Document all tokens in template/README.md

## 2. Migration of Functionality from Existing Nodes
- [ ] Audit `node_manager_node`, `node_model_generator`, and `schema_generator_node` for unique business logic, tools, and protocols
    - **Current Priority: Canonical Protocol, Tool, and Template Refactor**
        - [ ] **Inventory and Audit**
            - [ ] List all protocol files in `src/omnibase/nodes/node_manager/v1_0_0/protocols/`
            - [ ] List all tool files in `src/omnibase/nodes/node_manager/v1_0_0/tools/`
            - [ ] List all template files in `src/omnibase/nodes/node_manager/template/`
            - [ ] Identify any use of `dict`, `str`, or other primitives for domain data in method signatures or template tokens.
        - [x] **Model and Enum Definition**
            - [x] For each protocol/tool, define or update Pydantic models in `models/` for all arguments and return values.
            - [x] Define Enums in a central `enums/` module for any fixed sets of options (e.g., template types, output formats).
            - [x] Ensure all template context and output fields are represented as models/enums.
        - [x] **Protocol Refactor**
            - [x] Update all protocol method signatures to use the new models and enums.
            - [x] Add/Update docstrings to document all types, generics, and expected usage.
            - [x] Remove any use of `dict`, `str`, or other primitives for domain-specific data.
        - [x] **Tool Implementation Refactor**
            - [x] Update all tool classes to implement the updated protocols.
            - [x] Refactor internal logic to use models/enums instead of primitives.
            - [x] Ensure all file paths use `Path` (not `str`).
            - [x] **See debug log for 2025-06-09 for full context and handoff.**
        - [x] **Template Refactor**
            - [x] Audit all template files for token usage.
            - [x] Ensure all tokens correspond to fields in a canonical Pydantic model (e.g., `ModelTemplateContext`).
            - [x] Add or update `[ONEX_PROMPT]` comments to guide future customization and agent-driven generation.
            - [x] Remove any hardcoded or ambiguous tokens; all must be model-driven.
        - [x] **Registry and Injection**
            - [x] Update registry logic to use the new protocols and models.
            - [x] Ensure all scenario harnesses and test fixtures inject dependencies via the updated registry.
        - [x] **Testing**
            - [x] Update or write tests to use the new models and protocol contracts.
            - [x] Ensure all fixtures and test harnesses are registry-driven and protocol-first.
            - [x] Add/Update tests for template rendering, model validation, and protocol compliance.
        - [ ] **Documentation**
            - [ ] Update README(s) to document the new models, enums, and protocol patterns.
            - [ ] Document any deviations or open questions.
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