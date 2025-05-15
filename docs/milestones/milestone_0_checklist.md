# Milestone 0: ONEX Bootstrap – Implementation Checklist

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
- [ ] Stub out plugin discovery mechanism in registry/tools to support future validator extensions and org-specific rules (M2+). Include a code comment about future sandboxing and versioning requirements as per [General System Enhancements](../nodes/onex_future_roadmap.md#general-system-enhancements).
    - **DoD:** Placeholder logic for plugin discovery added to `SchemaRegistry` stub and relevant tool stubs (e.g., validator). Code comment regarding sandboxing/versioning added.
    - **Artifact:** `src/omnibase/core/core_registry.py`, `src/omnibase/tools/cli_validate.py` (stub)
    - **Reviewer(s):** Infra lead, Foundation team
    - **Labels:** [infra, plugins, m0]
    - **Status:** [ ]
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

- [ ] Create `tools/cli_validate.py` and `tools/cli_stamp.py` implementing respective protocols, as stub CLI entrypoints using `typer` following [Structural Conventions](../nodes/onex_structural_conventions.md) and [Protocol Definitions](../nodes/onex_protocol_definitions.md)
    - **DoD:** Files created in `src/omnibase/tools/`, implement abstract methods from `ProtocolValidate` and `ProtocolStamper` (imported from `src/omnibase/protocol/`) with placeholder logic (stubs), basic Typer CLI structure in place for each file. Files adhere to `cli_*.py` naming.
    - **Artifact:** `src/omnibase/tools/cli_validate.py`, `src/omnibase/tools/cli_stamp.py`
    - **Reviewer(s):** Tool team, Protocol team
    - **Labels:** [tool, validate, stamp, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
    - [ ] Implements `ProtocolValidate` (stub)
    - [ ] Implements `ProtocolStamper` (stub)
- [ ] Canonical CLI tool name: `onex` (use consistently in entrypoints, help text, and docs as per [Structural Conventions](../nodes/onex_structural_conventions.md#cli-naming-rules))
    - **DoD:** `pyproject.toml` entry point configured as `onex`, main CLI help text uses `onex`.
    - **Artifact:** `pyproject.toml`, `src/omnibase/tools/cli_main.py` (stub)
    - **Reviewer(s):** Tool team
    - **Labels:** [tool, cli, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add CLI `cli_main.py` entrypoint to route subcommands; expose as `__main__` script via `pyproject.toml` following [Structural Conventions](../nodes/onex_structural_conventions.md)
    - **DoD:** `cli_main.py` created in `src/omnibase/tools/`, uses `typer` to call stub validator/stamper functions, `pyproject.toml` entry point configured.
    - **Artifact:** `src/omnibase/tools/cli_main.py`, `pyproject.toml`
    - **Reviewer(s):** Tool team, Infra lead
    - **Labels:** [tool, cli, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Stub validation interface: `validate(path)` within `cli_validate.py` using `ProtocolValidate`
    - **DoD:** `validate` function stub exists in `cli_validate.py`, matches `ProtocolValidate` signature.
    - **Artifact:** `src/omnibase/tools/cli_validate.py` (stub)
    - **Reviewer(s):** Tool team, Protocol team
    - **Labels:** [validate, protocol, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Stub stamping interface: `stamp(path)` within `cli_stamp.py` using `ProtocolStamper`
    - **DoD:** `stamp` function stub exists in `cli_stamp.py`, matches `ProtocolStamper` signature.
    - **Artifact:** `src/omnibase/tools/cli_stamp.py` (stub)
    - **Reviewer(s):** Tool team, Protocol team
    - **Labels:** [stamp, protocol, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Stub logic in `validate` to load and parse a `.onex.yaml` file using the schema loader
    - **DoD:** `validate` stub in `cli_validate.py` includes calls to schema loader for a given path argument, basic placeholder for parsing result (e.g., returning a dict stub).
    - **Artifact:** `src/omnibase/tools/cli_validate.py` (stub)
    - **Reviewer(s):** Tool team, Schema team
    - **Labels:** [validate, schema, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Stub logic in `validate` to read *all key canonical fields* from loaded `.onex` stub, including `schema_version`, `name`, `version`, `uuid`, `description`, `state_contract`, `entrypoint`, `namespace`, `meta_type`, `runtime_language_hint`, `tags`, `trust_score_stub`, `x-extensions`, `protocols_supported`, `base_class`, `dependencies`, `environment`, `license`, and future/optional fields like `reducer`, `cache`, `performance`, `trust` (as defined in [Node Contracts and Metadata](../nodes/node_contracts.md)).
    - **DoD:** `validate` stub includes placeholder code to access these fields (if they exist in the loaded dict stub), e.g., `onex_data.get('field_name', default_value)`. Includes placeholders for optional/future fields.
    - **Artifact:** `src/omnibase/tools/cli_validate.py` (stub)
    - **Reviewer(s):** Tool team, Foundation team
    - **Labels:** [validate, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Stub URI parsing logic (e.g., regex check for `<type>://<namespace>@<version_spec>`) within a utility module (e.g., `utils/uri_parser.py`) following [Structural Conventions](../nodes/onex_structural_conventions.md) and [Node Contracts and Metadata](../nodes/node_contracts.md#uri-format-for-linking-fields)
    - **DoD:** Basic parsing function stub exists in `src/omnibase/utils/uri_parser.py` (or `utils/utils_uri_parser.py`), uses regex pattern from spec, returns a placeholder structure or raises a placeholder error. File adheres to `utils_*.py` naming if applicable.
    - **Artifact:** `src/omnibase/utils/uri_parser.py` (stub)
    - **Reviewer(s):** Utility team, Foundation team
    - **Labels:** [utils, uri, m0]
    - **Status:** [ ]
    - **PR/Issue:** #

### 5. 🧪 Testing & CI Framework Setup

- [ ] Add `tests/` directory structure mirroring `src/omnibase/` modules following [Structural Conventions](../nodes/onex_structural_conventions.md) and [Development Conventions & Best Practices](../nodes/onex_development_process.md#canonical-testing-philosophy)
    - **DoD:** `tests/` directory created with subdirectories `core/`, `schema/`, `tools/`, `utils/`, `lifecycle/`, `protocol/`, `template/`.
    - **Artifact:** `tests/core/`, `tests/schema/`, etc.
    - **Reviewer(s):** Test team
    - **Labels:** [test, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add `tests/__init__.py` and `tests/<module>/__init__.py` files
    - **DoD:** `__init__.py` files added to all test directories.
    - **Artifact:** `tests/__init__.py`, `tests/<module>/__init__.py`
    - **Reviewer(s):** Test team
    - **Labels:** [test, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add placeholder CI workflow (`.github/workflows/bootstrap.yml`) that runs tests and lints following [Development Conventions & Best Practices](../nodes/onex_development_process.md#cicd-integration-guidance)
    - **Suggested CI filename:** `.github/workflows/bootstrap.yml`
    - **DoD:** CI file created in `.github/workflows/`, linting and test execution steps defined for push/pull requests.
    - **Artifact:** `.github/workflows/bootstrap.yml`
    - **Reviewer(s):** CI team, Infra lead
    - **Labels:** [ci, infra, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Configure pytest to run tests from `tests/` directory
    - **DoD:** `pyproject.toml` or `pytest.ini` configured to discover and run tests.
    - **Artifact:** `pyproject.toml` or `pytest.ini`
    - **Reviewer(s):** Test team, Infra lead
    - **Labels:** [test, infra, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Include ruff, black, isort lint hooks in `.pre-commit-config.yaml` and enforce in CI
    - **DoD:** Pre-commit hooks configured in `.pre-commit-config.yaml`, CI workflow includes running pre-commits or equivalent linters, failures block merge.
    - **Artifact:** `.pre-commit-config.yaml`, `.github/workflows/bootstrap.yml`
    - **Reviewer(s):** CI team, Infra lead
    - **Labels:** [ci, infra, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add pre-commit hook or CI step for schema validation in `src/omnibase/schema/schemas/` (validate all schemas for JSONSchema/YAML compliance)
    - **DoD:** Schema linting hook/step configured and running in pre-commit or CI, fails on malformed schemas.
    - **Artifact:** `.pre-commit-config.yaml` or `.github/workflows/bootstrap.yml`
    - **Reviewer(s):** CI team, Schema team
    - **Labels:** [ci, schema, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add CLI smoke test (`onex --help`) to `tests/tools/test_cli_main.py`
    - **DoD:** Test file created in `tests/tools/`, basic CLI invocation test passes.
    - **Artifact:** `tests/tools/test_cli_main.py`
    - **Reviewer(s):** Test team, Tool team
    - **Labels:** [test, cli, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Create example node directory based on [Recommended File Layout](../nodes/onex_structural_conventions.md#file-layout-recommended) with `node.onex.yaml` stub including key canonical fields
    - **DoD:** Directory structure created (`nodes/example_node/`), minimal `node.onex.yaml` stub file added in `nodes/example_node/` conforming to the [Node Contracts and Metadata Specification](../nodes/node_contracts.md). Include placeholders/comments for key fields (schema_version, name, version, uuid, meta_type, entrypoint, dependencies, base_class, reducer, etc.). Include placeholder `src/` and `tests/` directories within the example node directory structure.
    - **Artifact:** `nodes/example_node/node.onex.yaml` (stub), `nodes/example_node/src/`, `nodes/example_node/tests/`
    - **Reviewer(s):** Foundation team, Schema team
    - **Labels:** [node, structure, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add a `.tree` file stub at the repository root referencing the example `node.onex.yaml` following [.tree Discovery Format](../nodes/onex_structural_conventions.md#tree-discovery-format)
    - **DoD:** `.tree` file created at the repo root, references the example node's `node.onex.yaml` path.
    - **Artifact:** `.tree` (stub)
    - **Reviewer(s):** Foundation team
    - **Labels:** [discovery, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add CI step to validate the example `node.onex.yaml` stub against the `onex_node.yaml` schema stub using the validator stub
    - **DoD:** CI workflow includes a step calling `onex validate nodes/example_node/node.onex.yaml` (or similar CLI command), the validator stub runs and reports success for the valid stub file (placeholder logic in validator).
    - **Artifact:** `.github/workflows/bootstrap.yml`, `src/omnibase/tools/cli_validate.py` (stub)
    - **Reviewer(s):** CI team, Tool team, Schema team
    - **Labels:** [ci, validate, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add CI/lint/test badge to `README.md` as soon as workflow is live
    - **DoD:** Badges added to README and displaying correctly (e.g., using Shield.io or similar).
    - **Artifact:** `README.md`
    - **Reviewer(s):** Foundation team, CI team
    - **Labels:** [ci, docs, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add placeholder for test coverage report/badge in `README.md`
    - **DoD:** Placeholder text or badge added to README, indicating where coverage will be displayed.
    - **Artifact:** `README.md`
    - **Reviewer(s):** Foundation team
    - **Labels:** [docs, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Create unit test for .onex metadata parsing using the validator stub, checking for the presence of key canonical fields
    - **DoD:** Test file created (e.g., `tests/tools/test_validator_stub.py`), test loads and parses the example `node.onex.yaml` stub using the validator stub's internal parsing logic. Test asserts that expected key fields (schema_version, name, version, etc.) are present in the loaded dict stub.
    - **Artifact:** `tests/tools/test_validator_stub.py` (or similar)
    - **Reviewer(s):** Test team, Tool team
    - **Labels:** [test, validate, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add a comment in plugin discovery stub about future sandboxing and versioning requirements
    - **DoD:** Comment added in the relevant M0 stub code (e.g., SchemaRegistry or validator stub) noting the future need for secure and versioned plugin handling.
    - **Artifact:** Relevant stub code file(s)
    - **Reviewer(s):** Infra lead, Protocol team
    - **Labels:** [infra, plugins, security, m0]
    - **Status:** [ ]
    - **PR/Issue:** #

- [ ] Write a verification walkthrough for new contributors in `docs/getting_started.md`
    - **DoD:** Step-by-step guide includes clone, env setup, install, lint, test, and stub CLI invocation.
    - **Artifact:** `docs/getting_started.md`
    - **Reviewer(s):** Foundation team
    - **Labels:** [docs, onboarding, m0]
    - **Status:** [ ]
    - **PR/Issue:** #

### 6. ⚠️ Error Handling and Taxonomy

- [ ] Define minimal error taxonomy or base error class in `core/errors.py`
    - **DoD:** `core/errors.py` created in `src/omnibase/core/`, contains base exception class (e.g., `OmniBaseError`).
    - **Artifact:** `src/omnibase/core/errors.py`
    - **Reviewer(s):** Core team, Foundation team
    - **Labels:** [core, errors, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Ensure shared error types are used across tools and loaders (stubs)
    - **DoD:** Tool and loader stubs (`cli_validate.py`, `cli_stamp.py`, `loader.py`) include basic error handling using the defined base error class.
    - **Artifact:** `src/omnibase/tools/*.py` (stubs), `src/omnibase/schema/loader.py` (stub)
    - **Reviewer(s):** Core team, Tool team, Schema team
    - **Labels:** [core, errors, m0]
    - **Status:** [ ]
    - **PR/Issue:** #

### 7. 📄 Canonical Testing Document

- [ ] Add canonical testing document (`docs/testing.md`) describing markerless, registry-swappable philosophy as per [Development Conventions & Best Practices](../nodes/onex_development_process.md#canonical-testing-philosophy)
    - **DoD:** Document created in `docs/`, includes key principles (no markers, fixture swapping), pytest guidance, and reference to registry fixture.
    - **Artifact:** `docs/testing.md`
    - **Reviewer(s):** Foundation team, Test team
    - **Labels:** [docs, test, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Include pytest registry fixture example and guidance for contributors in `docs/testing.md` as per [Development Conventions & Best Practices](../nodes/onex_development_process.md#registry-swapping-in-tests)
    - **DoD:** `docs/testing.md` includes a code example and explanation for the parametrized registry fixture.
    - **Artifact:** `docs/testing.md`
    - **Reviewer(s):** Foundation team, Test team
    - **Labels:** [docs, test, m0]
    - **Status:** [ ]
    - **PR/Issue:** #

### 8. 🧰 Canonical Template Files

- [ ] Create canonical template files for node metadata and scaffolding in `src/omnibase/templates/` following [Canonical Templates](../nodes/onex_templates_scaffolding.md)
    - **DoD:** Template files created in `src/omnibase/templates/`, follow Naming Conventions (`*.tmpl`), include placeholder content for scaffolding based on the examples in this document and [Canonical Templates](../nodes/onex_templates_scaffolding.md).
    - **Artifact:** `src/omnibase/templates/tool_node.yaml.tmpl`, `src/omnibase/templates/test_sample.py.tmpl`, `src/omnibase/templates/cli_tool.py.tmpl`, `src/omnibase/templates/protocol.py.tmpl`, `src/omnibase/templates/utils.py.tmpl` etc.
    - **Reviewer(s):** CAIA, Foundation team
    - **Labels:** [templates, m0]
    - **Status:** [ ]
    - **PR/Issue:** #
    - [ ] Files created in `src/omnibase/templates/`
    - [ ] Follow Naming Conventions (`.tmpl` extension)
    - [ ] Reviewed by CAIA

# Supplement: Additions to Milestone 0 Implementation Checklist

> These items augment the original Milestone 0 checklist with specific stubs and tests for planner compatibility, snapshot integrity, and tree discovery validation.

---

### 🔁 Validator and Metadata Tooling (Stub Only) – Additions

- [ ] Add placeholder logic to compute `trace_hash` in `cli_stamp.py` using `onex_data` content
    - **DoD:** Stub logic added to `cli_stamp.py` that computes a simple hash (e.g., SHA256 of `json.dumps(onex_data)`), stored in a variable `trace_hash`. This field will be later persisted in stamped metadata.
    - **Artifact:** `src/omnibase/tools/cli_stamp.py`
    - **Reviewer(s):** Tool team
    - **Labels:** [stamp, trace_hash, m0]
    - **Status:** [ ]
    - **PR/Issue:** #

---

### 🧪 Testing & CI Framework Setup – Additions

- [ ] Add unit test validating that reducer `snapshot_state()` returns a `BaseModel`
    - **DoD:** Test created (e.g., `tests/protocol/test_reducer_snapshot.py`) instantiating a stub `ReducerProtocol` implementation and asserting `isinstance(result, BaseModel)` for `snapshot_state()`.
    - **Artifact:** `tests/protocol/test_reducer_snapshot.py`
    - **Reviewer(s):** Protocol team, Test team
    - **Labels:** [test, reducer, m0]
    - **Status:** [ ]
    - **PR/Issue:** #

- [ ] Add `.tree` validation test asserting structure and existence of referenced files
    - **DoD:** Test created (e.g., `tests/tools/test_tree_discovery.py`) that loads `.tree`, asserts paths are valid, and verifies that each referenced `node.onex.yaml` is parseable.
    - **Artifact:** `tests/tools/test_tree_discovery.py`
    - **Reviewer(s):** Foundation team, Test team
    - **Labels:** [test, discovery, m0]
    - **Status:** [ ]
    - **PR/Issue:** #

# ## 🔭 Milestone Overview (Supplemental)
## 🔭 Milestone Overview (Supplemental)

| Milestone | Scope                            | Key Deliverables                            | Outcome               |
|-----------|----------------------------------|----------------------------------------------|------------------------|
| M0        | Bootstrap + Protocol Scaffolds   | CLI, Protocols, Templates, Validator Stubs   | Local execution + CI  |
| M1        | Validation + Execution Engine    | Full Validator, Registry, Reducer Runtime    | Executable Nodes      |
| M2        | Planning + Caching + Trust       | Planner, Composite Graph, Node Metrics       | Composable Execution  |
| M3+       | Federation + Interop             | P2P Nodes, Remote Execution, Consensus       | Federated Graph infra |