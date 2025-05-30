<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: onex_node_and_test_refactor_standards.md
version: 1.0.0
uuid: b87ab6fc-e6cf-4496-923b-0d12fce4a83a
author: OmniNode Team
created_at: '2025-05-30T13:04:27Z'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://onex_node_and_test_refactor_standards
namespace: markdown://onex_node_and_test_refactor_standards
meta_type: tool

<!-- === /OmniNode:Metadata === -->
# ONEX Node and Test Refactor Standards

## Overview

This document defines the required structural and validation standards for all ONEX nodes, shared libraries, and test files to ensure long-term maintainability, automation compatibility, and ecosystem integrity.

---

## 1. Python File Reusability
- **Rule:** All Python files outside node directories must be reusable by multiple nodes.
- **Action:**
  - Audit all .py files.
  - Move any single-node-use files into that node's versioned directory.
  - Shared code is already organized in `core/`, `mixins/`, `runtimes/`, `protocol/`, `utils/`, and `model/`.
  - Only create a new `lib/` or `common/` folder if a new cross-node utility emerges that does not fit the existing structure.
  - **Validator:** ImportValidator
- **2025-05-29 Update:**
  - No new `lib/` or `common/` folder is needed unless justified by new, broadly shared code.
- **AI/Innovation Suggestions:**
  - Develop an automated refactoring tool to move and update imports for single-use files.
  - Add a dependency visualization step to help teams spot accidental coupling.
  - Integrate dynamic import linting in CI to block new cross-node imports unless whitelisted.

---

## 2. Naming Conventions
- **Files:** snake_case
- **Directories:** snake_case (including node directories; PascalCase is NOT used)
- **Classes:** PascalCase
- **Variables/Functions:** snake_case
- **Enforcement Tools:** flake8, pylint, mypy, custom NameValidator
- **2025-05-29 Update:**
  - Node directories must use `snake_case`, not PascalCase, for consistency with the rest of the codebase and Python ecosystem norms.
  - Rationale: Consistent naming reduces cognitive load, avoids tooling/import issues, and matches Python/ONEX conventions. Having a single exception for node directories increases risk and complexity without benefit.
- **AI/Innovation Suggestions:**
  - Generate linter configs from a single source-of-truth YAML/JSON spec.
  - Provide a CLI tool for batch-renaming and import fixups.
  - Add a naming convention diff tool for PRs with auto-suggested fixes.

---

## 3. Test Structure Standards
### 3.1 General Rules
- All tests must use pytest.
- Tests must reside inside the version directory of each node.
- Node tests must include:
  - `tests/test_*.py`
  - `tests/test_cases/*.yaml` or `.json`
### 3.2 Separation of Concerns
- Test logic in `test_*.py`
- Test cases and fixtures in `test_cases/`
- Shared fixtures can live in `lib/test_helpers/` if reused
### 3.3 File Size Enforcement
- Max file size: 500 lines (400 preferred)
- **Validator:** FileSizeValidator
- **AI/Innovation Suggestions:**
  - Central registry for all test cases, auto-injected into pytest via plugin.
  - Test coverage dashboard to visualize missing cases or oversized files.
  - Pre-commit hook to block or warn on oversized test files, with split suggestions.

---

## 4. Node Directory Structure
### 4.1 Structure
```
/nodes/
  ExampleNode/
    contract.yaml        <- abstract contract (optional, root-level)
    v0.1.0/
      contract.yaml      <- concrete version
      run.py
      state.py
      metadata_block.yaml
      tests/
        test_runner.py
        test_cases/
          case_1.yaml
```
### 4.2 Root-Level Contract
- Defines node name, description, type, default parameters, supported versions, tags, and metadata.
- Can act as a base for versioned contracts.
- Schema reference: `$schema: ../schemas/node_contract.schema.yaml`
### 4.3 Enforced By
- StructureValidator
- SchemaValidator
- VersionValidator
- **AI/Innovation Suggestions:**
  - Contract inheritance tool to auto-generate versioned contracts from root.
  - Directory structure validator for both presence and content.
  - Node Explorer UI for interactive browsing of node structure and coverage.

---

## 5. Generator: Node Scaffold CLI
- **CLI Usage:**
  - `onex scaffold node --name LoggerNode --type tool --version v0.1.0`
- **Auto-Generated:**
  - Root contract.yaml
  - Versioned structure with boilerplate
  - Placeholder tests and cases
  - Metadata block
- **AI/Innovation Suggestions:**
  - Customizable templates for teams.
  - Interactive CLI with prompts and best-practice suggestions.
  - Scaffold linting: run all validators and show compliance report after generation.

---

## 6. Validator: Node Compliance
- **Composite Validator:** NodeComplianceValidator wraps:
  - ImportValidator
  - StructureValidator
  - SchemaValidator
  - TestValidator
  - FileSizeValidator
  - NameValidator
- **Execution Modes:**
  - Single node check
  - Batch validation
  - CI integration mode
- **AI/Innovation Suggestions:**
  - Validator as a Service (web API for integration).
  - Self-healing mode: auto-fix minor violations and open a PR.
  - Validation badges for each node/repo.

---

## 7. Future Extensions
- Root contract schema inheritance
- Multi-runtime node templates
- Scoring and rating logic
- Lint/format enforcement via pre-commit hooks
- **AI/Innovation Suggestions:**
  - Node Quality Score (NQS) should be a weighted composite of: contract completeness, test coverage, validation pass rate, and LOC compliance. Define initial weights and surface in compliance reports.
  - Historical compliance tracking
    - Store historical compliance per CI run in `compliance_report.yaml` under each node version. Aggregate reports in a central registry for trend analysis.
  - Plugin ecosystem for custom validators and templates.

---

## Prioritization: What To Do Now vs. Future Milestones

### **Immediate Priorities (Milestone 1/2):**
- Enforce Python file reusability and move single-use files.
- Audit and enforce naming conventions (files, dirs, classes, functions).
- Refactor all tests to follow the new structure (test logic vs. test cases, file size limits).
- Standardize node directory structure and contracts.
- Implement/expand Node Scaffold CLI and NodeComplianceValidator.
- Integrate all validators into CI for batch and PR checks.
- Document standards and rationale in the docs/standards/ and docs/testing/ folders.

### **Future Milestones:**
- Develop and deploy automated refactoring and renaming tools.
- Add dependency visualization and Node Explorer UI.
- Implement contract inheritance and customizable templates.
- Launch Validator as a Service and self-healing PR bots.
- Add Node Quality Score and compliance dashboards.
- Track historical compliance and surface trends.
- Expand plugin ecosystem for custom org needs.

---

## Innovation Opportunities (Summary)
- Automated refactoring and import management
- Centralized, auto-injected test case registries
- Interactive and visual tools for node structure and compliance
- Self-healing and auto-fix bots for minor violations
- Quality scoring and compliance tracking
- Plugin and template extensibility for org-specific needs

---

## Appendix: Original and AI-Augmented Rationale

**Original Standard:**
> (Insert original document content here for traceability)

**AI-Augmented Suggestions:**
> (All AI/innovation suggestions above are marked in each section and summarized for leadership and engineering review.)

---

*This document is living and should be updated as standards, tooling, and ecosystem needs evolve.*