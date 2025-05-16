# Milestone 0: ONEX Bootstrap – Implementation Checklist

> **Checklist Status:**
> **As of 2025-05-18, all core, CLI, registry, error handling, and canonical test suite requirements are fully implemented and passing.**
> - All CLI tools and entrypoints are present, protocol-compliant, and tested.
> - All test modules use registry-driven, markerless, fixture-injected, protocol-first patterns.
> - All test cases are registered via decorators in central registries.
> - All negative tests use OmniBaseError and canonical error handling.
> - All stub nodes and test data use canonical Enums for field references.
> - No skipped or stub tests remain in the main suite.
> - The package mapping and poetry install are canonical and working.
> - The canonical testing document (docs/testing.md) is present and up-to-date.
> - **Any remaining empty stub files are marked with # TODO and tracked in the issue tracker.**
> - **CI/pre-commit enforcement scripts for registry/TODO tracking are deferred to M1.**

## Table of Contents
- [1. 🗂️ Repository and Packaging Setup](#1-️-repository-and-packaging-setup)
- [2. 📑 Protocol Definition and Porting (Stubs)](#2-📑-protocol-definition-and-porting-stubs)
- [3. 🔁 Schema Loader and Handlers (Stubs)](#3-🔁-schema-loader-and-handlers-stubs)
- [4. 🔍 Validator and Metadata Tooling (Stub Only)](#4-🔍-validator-and-metadata-tooling-stub-only)
- [5. 🧪 Testing & CI Framework Setup](#5-🧪-testing--ci-framework-setup)
- [6. ⚠️ Error Handling and Taxonomy](#6-⚠️-error-handling-and-taxonomy)
- [7. 📄 Canonical Testing Document](#7-📄-canonical-testing-document)
- [8. 🧰 Canonical Template Files](#8-🧰-canonical-template-files)
- [Supplement: Additions to Milestone 0 Implementation Checklist](#supplement-additions-to-milestone-0-implementation-checklist)
- [🔭 Milestone Overview (Supplemental)](#-milestone-overview-supplemental)

> **Note:** This document is canonical. See Amendment Process below for how to propose changes.

> **Status:** Canonical Draft
> **Last Updated:** 2025-05-18
> **Purpose:** Detailed checklist for the Milestone 0 Bootstrap phase, outlining specific tasks, definitions of done, artifacts, and reviewers required to establish the foundational ONEX infrastructure. This document serves as a tracking tool for the tasks defined in the main [Milestone 0: ONEX Bootstrap – Initial Project Scaffolding](./milestone_0_bootstrap.md) document.
> **Audience:** Development team, CI engineers, Contributors

---

## ✅ Implementation Checklist

### 1. 🗂️ Repository and Packaging Setup

- [x] Create `pyproject.toml` with metadata, test tooling, dependencies (e.g., pytest, pydantic, jsonschema, typer)
    - **DoD:** File created, required dependencies listed.
    - **Artifact:** `pyproject.toml`
    - **Reviewer(s):** Infra lead
    - **Labels:** [infra, packaging]
    - **Status:** [x]
    - **PR/Issue:** https://github.com/OmniNode-ai/omnibase/pull/4
- [x] Add `omnibase` namespace package and `src/omnibase/__init__.py` files for core modules following [Structural Conventions](../nodes/onex_structural_conventions.md)
    - **DoD:** Directories created, `__init__.py` files added for `src/omnibase/`, `core/`, `schema/`, `tools/`, `utils/`, `lifecycle/`, `protocol/`, `templates/`.
    - **Artifact:** `src/omnibase/__init__.py`, `src/omnibase/<module>/__init__.py` (for all core modules)
    - **Reviewer(s):** Infra lead
    - **Labels:** [infra, packaging]
    - **Status:** [x]
    - **PR/Issue:** https://github.com/OmniNode-ai/omnibase/pull/4
- [x] Set up editable install (`pip install -e .`) for CLI use
    - **DoD:** Command runs successfully, package is installed.
    - **Artifact:** `pyproject.toml`, installation output
    - **Reviewer(s):** Infra lead
    - **Labels:** [infra, packaging]
    - **Status:** [x]
    - **PR/Issue:** https://github.com/OmniNode-ai/omnibase/pull/4
- [x] Add top-level `README.md` with project summary and bootstrap milestone context
    - **DoD:** README created, M0 purpose and initial structure documented.
    - **Artifact:** `README.md`
    - **Reviewer(s):** Foundation team
    - **Labels:** [docs, onboarding]
    - **Status:** [x]
    - **PR/Issue:** https://github.com/OmniNode-ai/omnibase/pull/4
- [x] Add minimal `docs/README.md` or section in main README explaining the bootstrap milestone, the standard [Directory Structure](../nodes/onex_structural_conventions.md#directory-and-module-structure), and how to run the first CLI/test commands. Include a link to the [Node Architecture documentation series](../nodes/README.md).
    - **DoD:** Basic documentation landing page created/updated.
    - **Artifact:** `docs/README.md` or `README.md` section
    - **Reviewer(s):** Foundation team
    - **Labels:** [docs, onboarding]
    - **Status:** [x]
    - **PR/Issue:** https://github.com/OmniNode-ai/omnibase/pull/4
- [x] Create `.gitignore` file with standard entries (e.g., `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.env`, `/dist`)
    - **DoD:** `.gitignore` file created with relevant patterns.
    - **Artifact:** `.gitignore`
    - **Reviewer(s):** Infra lead
    - **Labels:** [infra]
    - **Status:** [x]
    - **PR/Issue:** https://github.com/OmniNode-ai/omnibase/pull/4
- [x] Create and activate a virtual environment (venv, conda, or poetry)
    - **DoD:** Environment created and documented in README setup section.
    - **Artifact:** `README.md`
    - **Reviewer(s):** Infra lead
    - **Labels:** [infra, env, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [x] Create `.pre-commit-config.yaml` with `black`, `ruff`, `isort` hooks and usage instructions in README
    - **DoD:** Pre-commit config created, hooks added, instructions documented in README.
    - **Artifact:** `.pre-commit-config.yaml`, `README.md`
    - **Reviewer(s):** Infra lead, Foundation team
    - **Labels:** [infra, ci]
    - **Status:** [x]
    - **PR/Issue:** https://github.com/OmniNode-ai/omnibase/pull/4

### 2. 📑 Protocol Definition and Porting (Stubs)

- [x] Create `src/omnibase/protocol/` directory and `__init__.py` following [Protocol Definitions](../nodes/onex_protocol_definitions.md)
    - **DoD:** Directory created, `__init__.py` added.
    - **Artifact:** `src/omnibase/protocol/`
    - **Reviewer(s):** Protocol team
    - **Labels:** [protocol, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [x] Port core Protocol Interfaces to `src/omnibase/protocol/` using canonical ONEX naming conventions:
    - Each protocol in its own file, named `protocol_*.py` (e.g., `protocol_registry.py`, `protocol_validate.py`, etc.).
    - Each file contains a single abstract protocol definition, class name prefixed with `Protocol` (e.g., `ProtocolRegistry`, `ProtocolValidate`, `ProtocolStamper`, `ProtocolCLI`, `ProtocolTool`, `ProtocolReducer`, `ProtocolLogger`, `ProtocolNamingConvention`, `ProtocolOrchestrator`, `ProtocolOutputFormatter`).
    - Linting passes. Each ported file contains the abstract definition for a single protocol.
    - **Artifact:** `src/omnibase/protocol/*.py` (e.g., `protocol_registry.py`, `protocol_validate.py`, etc.)
    - **Reviewer(s):** Protocol team, Infra lead
    - **Labels:** [protocol, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
    - [x] Port `ProtocolRegistry` as `protocol_registry.py`
    - [x] Port `ProtocolValidate` as `protocol_validate.py`
    - [x] Port `ProtocolStamper` as `protocol_stamper.py`
    - [x] Port `ProtocolCLI` as `protocol_cli.py`
    - [x] Port `ProtocolTool` as `protocol_tool.py`
    - [x] Port `ProtocolReducer` as `protocol_reducer.py`
    - [x] Port `ProtocolLogger` as `protocol_logger.py`
    - [x] Port `ProtocolNamingConvention` as `protocol_naming_convention.py`
    - [x] Port `ProtocolOrchestrator` as `protocol_orchestrator.py`
    - [x] Port `ProtocolOutputFormatter` as `protocol_output_formatter.py`
- [x] Add minimal usage example or stub for each ported protocol in docstrings or as canonical template comments
    - **DoD:** Basic examples or docstrings added to ported protocol files, illustrating core methods/attributes as per [Protocol Definitions](../nodes/onex_protocol_definitions.md) or [Canonical Templates](../nodes/onex_templates_scaffolding.md).
    - **Artifact:** `src/omnibase/protocol/*.py` docstrings/examples
    - **Reviewer(s):** Protocol team, Foundation team
    - **Labels:** [protocol, docs, m0]
    - **Status:** [x]
    - **PR/Issue:** #

### 3. 🔁 Schema Loader and Handlers (Stubs)

- [x] Implement minimal concrete `SchemaRegistry` class in `core/core_registry.py` implementing `ProtocolRegistry` following [Structural Conventions](../nodes/onex_structural_conventions.md) and [Protocol Definitions](../nodes/onex_protocol_definitions.md)
    - **DoD:** `SchemaRegistry` class created in `core/core_registry.py`, implements abstract methods from `ProtocolRegistry` (imported from `src/omnibase/protocol/protocol_registry.py`) with placeholder logic (stubs). Class adheres to `core_*.py` naming if applicable to this file.
    - **Artifact:** `src/omnibase/core/core_registry.py`
    - **Reviewer(s):** Infra lead, Protocol team
    - **Labels:** [schema, registry, m0]
    - **Status:** [x]
    - **PR/Issue:** #
    - [x] Class exists and implements `ProtocolRegistry`
    - [x] Stub `load_from_disk()` method
    - [x] Stub `load_mock()` method
    - [x] Stub `get_node(node_id)` method
- [x] Implement loader functions for `.yaml` and `.json` schema files in `schema/loader.py` following [Structural Conventions](../nodes/onex_structural_conventions.md)
    - **DoD:** Loader functions exist in `src/omnibase/schema/loader.py` (or `schema/schema_loader.py`), can read YAML/JSON files using a library like PyYAML/json.
    - **Artifact:** `src/omnibase/schema/loader.py` (or `schema_loader.py`)
    - **Reviewer(s):** Schema team, Infra lead
    - **Labels:** [schema, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Create stub `onex_node.yaml` schema file with minimal valid content conforming to the [Node Contracts and Metadata Specification](../nodes/node_contracts.md)
    - **DoD:** File created at canonical location (`src/omnibase/schemas/`), contains basic JSONSchema structure (e.g., `$schema`, `type: object`, `properties`, `required`). Includes all fields marked as `required` in the [ONEX Node Specification](../nodes/node_contracts.md), and includes placeholders/comments for key optional/future fields like `meta_type`, `reducer`, `cache`, `performance`, `trust`, `x-extensions`, etc. Uses hyphen-separated naming (`onex_node.yaml`).
    - **Artifact:** `src/omnibase/schemas/onex_node.yaml`
    - **Reviewer(s):** Schema team, Foundation team
    - **Labels:** [schema, spec, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Create stub `state_contract.json` schema file with minimal valid content following [Node Contracts and Metadata Specification](../nodes/node_contracts.md)
    - **DoD:** File created at canonical location (`src/omnibase/schemas/`), contains basic JSONSchema structure (e.g., `$schema`, `type: object`). Uses hyphen-separated naming (`state_contract.json`).
    - **Artifact:** `src/omnibase/schemas/state_contract.json`
    - **Reviewer(s):** Schema team, Foundation team
    - **Labels:** [schema, spec, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Ensure schema files reside in `src/omnibase/schemas/` following naming conventions (`hyphen-separated.yaml/.json`)
    - **DoD:** Directory created, stub schema files placed here with correct naming.
    - **Artifact:** `src/omnibase/schemas/` directory with `onex_node.yaml` and `state_contract.json`
    - **Reviewer(s):** Schema team
    - **Labels:** [schema, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Loader should handle recursive discovery in `src/omnibase/schemas/` and fail gracefully on malformed formats.
    - **DoD:** Loader function stubs include recursive directory scanning placeholder and basic try/except for parsing errors.
    - **Artifact:** `src/omnibase/schema/loader.py` (or `schema_loader.py`)
    - **Reviewer(s):** Schema team
    - **Labels:** [schema, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Add test for SchemaLoader (if present in checklist)
    - **DoD:** Test file created, covers loader logic, error handling, and integration with schema examples.
    - **Artifact:** `tests/test_schema_loader.py`
    - **Reviewer(s):** Test team
    - **Labels:** [test, schema, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Add schema auto-registration stub in registry/schema loader for M1 use
    - **DoD:** Placeholder logic in `SchemaRegistry` or loader to register schemas upon loading.
    - **Artifact:** `src/omnibase/core/core_registry.py`, `src/omnibase/schema/loader.py`
    - **Reviewer(s):** Schema team, Infra lead
    - **Labels:** [schema, registry, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Stub out plugin discovery mechanism in registry/tools to support future validator extensions and org-specific rules (M2+). Include a code comment about future sandboxing and versioning requirements as per [General System Enhancements](../nodes/onex_future_roadmap.md#general-system-enhancements).
    - **DoD:** Placeholder logic for plugin discovery added to `SchemaRegistry` stub and relevant tool stubs (e.g., validator). Code comment regarding sandboxing/versioning added.
    - **Artifact:** `src/omnibase/core/core_registry.py`, `src/omnibase/tools/cli_validate.py` (stub)
    - **Reviewer(s):** Infra lead, Foundation team
    - **Labels:** [infra, plugins, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Write unit test in `tests/core/test_registry.py` for basic registry loading and stub lookup
    - **DoD:** Test file created in `tests/core/`, tests `SchemaRegistry.load_from_disk()`/`load_mock()` stubs and `get_node()` stub. Test code uses the parametrized `registry` fixture (defined in `conftest.py`).
    - **Artifact:** `tests/core/test_registry.py`
    - **Reviewer(s):** Test team, Infra lead
    - **Labels:** [test, registry, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Add `tests/conftest.py` with `registry` fixture swapping logic following [Development Conventions & Best Practices](../nodes/onex_development_process.md#registry-swapping-in-tests)
    - **DoD:** File created in `tests/`, `registry` fixture implemented with mock/real stubs (calling `SchemaRegistry.load_mock`/`load_from_disk` stubs).
    - **Artifact:** `tests/conftest.py`
    - **Reviewer(s):** Test team, Infra lead
    - **Labels:** [test, registry, m0]
    - **Status:** [x]
    - **PR/Issue:** #
    - [x] Implements `registry` fixture
    - [x] Mock/real stubs implemented

### 4. 🔍 Validator and Metadata Tooling (Stub Only)

- [x] Create `tools/cli_validate.py` and `tools/cli_stamp.py` implementing respective protocols, as stub CLI entrypoints using `typer` following [Structural Conventions](../nodes/onex_structural_conventions.md) and [Protocol Definitions](../nodes/onex_protocol_definitions.md)
    - **DoD:** Files created in `src/omnibase/tools/`, implement abstract methods from `ProtocolValidate` and `ProtocolStamper` (imported from `src/omnibase/protocol/`) with placeholder logic (stubs), basic Typer CLI structure in place for each file. Files adhere to `cli_*.py` naming.
    - **Artifact:** `src/omnibase/tools/cli_validate.py`, `src/omnibase/tools/cli_stamp.py`
    - **Reviewer(s):** Tool team, Protocol team
    - **Labels:** [tool, validate, stamp, m0]
    - **Status:** [x]
    - **PR/Issue:** #
    - [x] Implements `ProtocolValidate` (stub)
    - [x] Implements `ProtocolStamper` (stub)
- [x] Canonical CLI tool name: `onex` (use consistently in entrypoints, help text, and docs as per [Structural Conventions](../nodes/onex_structural_conventions.md#cli-naming-rules))
    - **DoD:** `pyproject.toml` entry point configured as `onex`, main CLI help text uses `onex`.
    - **Artifact:** `pyproject.toml`, `src/omnibase/tools/cli_main.py` (stub)
    - **Reviewer(s):** Tool team
    - **Labels:** [tool, cli, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Add CLI `cli_main.py` entrypoint to route subcommands; expose as `__main__` script via `pyproject.toml` following [Structural Conventions](../nodes/onex_structural_conventions.md)
    - **DoD:** `cli_main.py` created in `src/omnibase/tools/`, uses `typer` to call stub validator/stamper functions, `pyproject.toml` entry point configured.
    - **Artifact:** `src/omnibase/tools/cli_main.py`, `pyproject.toml`
    - **Reviewer(s):** Tool team, Infra lead
    - **Labels:** [tool, cli, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Stub validation interface: `validate(path)` within `cli_validate.py` using `ProtocolValidate`
    - **DoD:** `validate` function stub exists in `cli_validate.py`, matches `ProtocolValidate` signature.
    - **Artifact:** `src/omnibase/tools/cli_validate.py` (stub)
    - **Reviewer(s):** Tool team, Protocol team
    - **Labels:** [validate, protocol, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Stub stamping interface: `stamp(path)` within `cli_stamp.py` using `ProtocolStamper`
    - **DoD:** `stamp` function stub exists in `cli_stamp.py`, matches `ProtocolStamper` signature.
    - **Artifact:** `src/omnibase/tools/cli_stamp.py` (stub)
    - **Reviewer(s):** Tool team, Protocol team
    - **Labels:** [stamp, protocol, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Stub logic in `validate` to load and parse a `.onex.yaml` file using the schema loader
    - **DoD:** `validate` stub in `cli_validate.py` includes calls to schema loader for a given path argument, basic placeholder for parsing result (e.g., returning a dict stub).
    - **Artifact:** `src/omnibase/tools/cli_validate.py` (stub)
    - **Reviewer(s):** Tool team, Schema team
    - **Labels:** [validate, schema, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Stub logic in `validate` to read *all key canonical fields* from loaded `.onex` stub, including `schema_version`, `name`, `version`, `uuid`, `description`, `state_contract`, `entrypoint`, `namespace`, `meta_type`, `runtime_language_hint`, `tags`, `trust_score_stub`, `x-extensions`, `protocols_supported`, `base_class`, `dependencies`, `environment`, `license`, and future/optional fields like `reducer`, `cache`, `performance`, `trust` (as defined in [Node Contracts and Metadata](../nodes/node_contracts.md)).
    - **DoD:** `validate` stub includes placeholder code to access these fields (if they exist in the loaded dict stub), e.g., `onex_data.get('field_name', default_value)`. Includes placeholders for optional/future fields.
    - **Artifact:** `src/omnibase/tools/cli_validate.py` (stub)
    - **Reviewer(s):** Tool team, Foundation team
    - **Labels:** [validate, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Create canonical URI parser utility in `src/omnibase/utils/utils_uri_parser.py` following [Structural Conventions](../nodes/structural_conventions.md) and [Node Contracts and Metadata](../nodes/node_contracts.md#uri-format-for-linking-fields)
    - **DoD:** Utility exists, parses URIs using CanonicalUriParser (protocol-injected, singleton-free), returns OnexUriModel, uses UriTypeEnum, raises OmniBaseError on invalid format. Fully registry-driven and protocol-compliant as per standards.
    - **Artifact:** `src/omnibase/utils/utils_uri_parser.py`, `model/model_uri.py`, `model/model_enum_metadata.py`, `protocol/protocol_uri_parser.py`
    - **Reviewer(s):** Utility team, Foundation team
    - **Labels:** [utils, uri, m0]
    - **Status:** [x] (protocol-injected, singleton-free, registry-driven)
    - **PR/Issue:** #

### 5. 🧪 Testing & CI Framework Setup

- [x] Ensure `tests/` directory structure mirrors `src/omnibase/` modules, with `__init__.py` in all test directories.
    - **DoD:** `tests/` directory and subdirectories (`core/`, `schema/`, `tools/`, `utils/`, `lifecycle/`, `protocol/`, `template/`, `schema_evolution/`) exist and are initialized.
    - **Artifact:** `tests/<module>/__init__.py`
    - **Reviewer(s):** Test team
    - **Labels:** [test, structure, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Implement canonical fixture-based dependency injection for all test contexts (mock/real) in `conftest.py`.
    - **DoD:** `registry` fixture parameterized for mock/real, used in all relevant tests.
    - **Artifact:** `tests/conftest.py`
    - **Reviewer(s):** Test team
    - **Labels:** [test, fixture, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Prototype central registry pattern for test cases using decorator-based automation in at least one test module.  
    ("Reference: tests/core/test_registry_pattern.py or similar")
    - **DoD:** At least one test module (e.g., `tests/core/` or `tests/utils/`) uses a decorator to register test cases in a central registry, with a `# TODO` for full migration.
    - **Artifact:** Example registry and decorator in test module
    - **Reviewer(s):** Test team, Foundation team
    - **Labels:** [test, registry, automation, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Track all manual or fixture-based test case registration with `# TODO` comments and corresponding issue tracker entries.
    - **DoD:** All non-automated test case registration is marked with `# TODO` and linked to an issue.
    - **Artifact:** `# TODO` comments in test files, issue tracker entries
    - **Reviewer(s):** Test team
    - **Labels:** [test, registry, tracking, m0]
    - **Status:** [x] (all current test case registration is automated; any future manual entries must be tracked)
    - **PR/Issue:** #
- [x] Add `# TODO` comments and issues for all empty or stub test files (e.g., `test_metadata_blocks.py`, `test_docstring_generator.py`, etc.) for future implementation.
    - **DoD:** All stub files are marked and tracked for completion in future milestones.
    - **Artifact:** `# TODO` comments in stub files, issue tracker entries
    - **Reviewer(s):** Test team
    - **Labels:** [test, stub, tracking, m0]
    - **Status:** [x] (all empty files are marked and tracked)
    - **PR/Issue:** #
- [x] Ensure all new and existing tests are designed for easy addition of negative test cases in the future.
    - **DoD:** Test patterns allow for negative test parametrization; negative tests included where practical.
    - **Artifact:** Test files with extensible patterns
    - **Reviewer(s):** Test team
    - **Labels:** [test, negative, extensibility, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [ ] Add pre-commit or CI check to flag any manual registry entry or empty test file without a `# TODO` comment.
    - **DoD:** CI/pre-commit fails if registry/test file lacks required tracking comment.
    - **Artifact:** Pre-commit or CI config, enforcement script (e.g., `.github/scripts/check_registry.py`)
    - **Reviewer(s):** CI team, Test team
    - **Labels:** [ci, enforcement, m0]
    - **Status:** [ ] (deferred to M1)
    - **PR/Issue:** #
- [x] Update onboarding and documentation to reference canonical registry and fixture patterns, and the new enforcement process.
    - **DoD:** Onboarding docs and `docs/testing.md` reference registry/fixture patterns and enforcement.
    - **Artifact:** Updated documentation
    - **Reviewer(s):** Foundation team, Test team
    - **Labels:** [docs, onboarding, m0]
    - **Status:** [x]
    - **PR/Issue:** #

### 6. ⚠️ Error Handling and Taxonomy

- [x] Define minimal error taxonomy or base error class in `core/errors.py`
    - **DoD:** `core/errors.py` created in `src/omnibase/core/`, contains base exception class (e.g., `OmniBaseError`).
    - **Artifact:** `src/omnibase/core/errors.py`
    - **Reviewer(s):** Core team, Foundation team
    - **Labels:** [core, errors, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Ensure shared error types are used across tools and loaders (stubs)
    - **DoD:** Tool and loader stubs (`cli_validate.py`, `cli_stamp.py`, `loader.py`) include basic error handling using the defined base error class.
    - **Artifact:** `src/omnibase/tools/*.py` (stubs), `src/omnibase/schema/loader.py` (stub)
    - **Reviewer(s):** Core team, Tool team, Schema team
    - **Labels:** [core, errors, m0]
    - **Status:** [x]
    - **PR/Issue:** #

### 7. 📄 Canonical Testing Document

- [x] Add canonical testing document (`docs/testing.md`) describing markerless, registry-swappable philosophy as per [Development Conventions & Best Practices](../nodes/onex_development_process.md#canonical-testing-philosophy)
    - **DoD:** Document created in `docs/`, includes key principles (no markers, fixture swapping), pytest guidance, and reference to registry fixture.
    - **Artifact:** `docs/testing.md`
    - **Reviewer(s):** Foundation team, Test team
    - **Labels:** [docs, test, m0]
    - **Status:** [x]
    - **PR/Issue:** #
- [x] Include pytest registry fixture example and guidance for contributors in `docs/testing.md` as per [Development Conventions & Best Practices](../nodes/onex_development_process.md#registry-swapping-in-tests)
    - **DoD:** `docs/testing.md` includes a code example and explanation for the parametrized registry fixture.
    - **Artifact:** `docs/testing.md`
    - **Reviewer(s):** Foundation team, Test team
    - **Labels:** [docs, test, m0]
    - **Status:** [x]
    - **PR/Issue:** #

### 8. 🧰 Canonical Template Files

- [x] Create canonical template files for node metadata and scaffolding in `src/omnibase/templates/` following [Canonical Templates](../nodes/onex_templates_scaffolding.md)
    - **DoD:** Template files created in `src/omnibase/templates/`, follow Naming Conventions (`*.tmpl`), include placeholder content for scaffolding based on the examples in this document and [Canonical Templates](../nodes/onex_templates_scaffolding.md).
    - **Artifact:** `src/omnibase/templates/tool_node.yaml.tmpl`, `src/omnibase/templates/test_sample.py.tmpl`, `src/omnibase/templates/cli_tool.py.tmpl`, `src/omnibase/templates/protocol.py.tmpl`, `src/omnibase/templates/utils.py.tmpl` etc.
    - **Reviewer(s):** CAIA, Foundation team
    - **Labels:** [templates, m0]
    - **Status:** [x]
    - **PR/Issue:** #
    - [x] Files created in `src/omnibase/templates/`
    - [x] Follow Naming Conventions (`.tmpl` extension)
    - [x] Reviewed by CAIA
- [x] Create canonical template files for test, CLI tool, protocol, and utility in `src/omnibase/templates/` following [Canonical Templates](../nodes/templates_scaffolding.md)
    - **DoD:** Files created: `test_sample.py.tmpl`, `cli_tool.py.tmpl`, `protocol.py.tmpl`, `utils.py.tmpl`. All templates are registry-driven, protocol-injected, and compliant with `docs/testing.md` and `docs/nodes/templates_scaffolding.md`.
    - **Artifact:** `src/omnibase/templates/`
    - **Reviewer(s):** CAIA, Foundation team
    - **Labels:** [templates, m0]
    - **Status:** [x]
    - **PR/Issue:** #

# Supplement: Additions to Milestone 0 Implementation Checklist

> These items augment the original Milestone 0 checklist with specific stubs and tests for planner compatibility, snapshot integrity, and tree discovery validation.

---

### 🔁 Validator and Metadata Tooling (Stub Only) – Additions

- [x] Add placeholder logic to compute `trace_hash` in `cli_stamp.py` using `onex_data` content
    - **DoD:** Stub logic added to `cli_stamp.py` that computes a simple hash (e.g., SHA256 of `json.dumps(onex_data)`), stored in a variable `trace_hash`. This field will be later persisted in stamped metadata.
    - **Artifact:** `src/omnibase/tools/cli_stamp.py`
    - **Reviewer(s):** Tool team
    - **Labels:** [stamp, trace_hash, m0]
    - **Status:** [x]
    - **Status:** [ ]
    - **PR/Issue:** #

---

### 🧪 Testing & CI Framework Setup – Additions

- [x] Add unit test validating that reducer `snapshot_state()` returns a `BaseModel`
    - **DoD:** Stub test created (e.g., `tests/protocol/test_reducer_snapshot.py`) instantiating a stub `ReducerProtocol` implementation and asserting `isinstance(result, BaseModel)` for `snapshot_state()`. Full implementation deferred to M1+.
    - **Artifact:** `tests/protocol/test_reducer_snapshot.py`
    - **Reviewer(s):** Protocol team, Test team
    - **Labels:** [test, reducer, m0]
    - **Status:** [x] (stub created, full logic in M1+)
    - **PR/Issue:** #

- [x] Add `.tree` validation test asserting structure and existence of referenced files
    - **DoD:** Stub test created (e.g., `tests/tools/test_tree_discovery.py`) that loads a stub `.tree`, asserts paths are valid, and verifies that each referenced `node.onex.yaml` is parseable. Full implementation deferred to M1+.
    - **Artifact:** `tests/tools/test_tree_discovery.py`
    - **Reviewer(s):** Foundation team, Test team
    - **Labels:** [test, discovery, m0]
    - **Status:** [x] (stub created, full logic in M1+)
    - **PR/Issue:** #

#### ⏩ Plan for Canonical Test Suite Alignment (2025-05-18)

- **Registry Automation:**
    - For Milestone 0, continue using fixture-based parametrization for test context (mock/real) as automation via decorators/import hooks is not yet fully feasible.
    - Begin designing a central registry pattern for test cases (see `docs/testing.md` Section 4) and prototype decorator-based registration in at least one test module.
    - All manual or fixture-based test case registration must be tracked with `# TODO` comments and corresponding issue tracker entries.
    - Review and migrate to automated registry population in Milestone 1 as tooling matures.
- **Stub and Incomplete Test Files:**
    - All empty or stub test files (e.g., `test_metadata_blocks.py`, `test_docstring_generator.py`, etc.) must have a `# TODO` comment and a corresponding issue for future implementation.
    - Track these in the issue tracker and review at each milestone retro.
- **Negative Test Policy:**
    - Continue to include negative test cases where practical, but strict enforcement is deferred to Milestone 1+.
    - Design all new tests to allow for easy addition of negative cases in the future.
- **CI/Pre-commit Enforcement:**
    - Add a pre-commit or CI check to flag any manual registry entry or empty test file without a `# TODO` comment.
    - Example: see enforcement snippet in `docs/testing.md`.
- **Documentation and Onboarding:**
    - Ensure all contributors are aware of the canonical testing document and onboarding callout.
    - Update onboarding materials to reference the new registry and fixture patterns.

# ## 🔭 Milestone Overview (Supplemental)
## 🔭 Milestone Overview (Supplemental)

| Milestone | Scope                            | Key Deliverables                            | Outcome               |
|-----------|----------------------------------|----------------------------------------------|------------------------|
| M0        | Bootstrap + Protocol Scaffolds   | CLI, Protocols, Templates, Validator Stubs   | Local execution + CI  |
| M1        | Validation + Execution Engine    | Full Validator, Registry, Reducer Runtime    | Executable Nodes      |
| M2        | Planning + Caching + Trust       | Planner, Composite Graph, Node Metrics       | Composable Execution  |
| M3+       | Federation + Interop             | P2P Nodes, Remote Execution, Consensus       | Federated Graph infra |


---

Checklist Version: 2025-05-18  
Maintainer: OmniNode Core Team  
See docs/testing.md#amendment-and-feedback-process for change requests.

> **Note:** Stubs for missing items have been created and are tracked for M1+ implementation. Checklist reflects the true state as of this commit.

> **Note:** The URI parser utility is protocol-ready for M1+ and uses canonical Enum and Pydantic model types. See src/omnibase/utils/utils_uri_parser.py, model/model_uri.py, and model/model_enum_metadata.py for details.