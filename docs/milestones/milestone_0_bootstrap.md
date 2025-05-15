# Milestone 0: ONEX Bootstrap – Initial Project Scaffolding

> **Status:** Canonical Draft
> **Last Updated:** 2025-05-18
> **Purpose:** Establish the foundational directory structure, core libraries, and bootstrapping utilities required to build and validate the ONEX system. This milestone precedes Milestone 1 and enables all metadata, validation, and CI logic to be implemented correctly and consistently.
> **Audience:** Node authors, tool builders, runtime developers, CI engineers

---

## 🔧 Why This Milestone Exists

Although Milestone 1 defines the initial schemas, metadata standards, and validation tools, those deliverables require supporting infrastructure to exist first:
- Source layout for `src/omnibase/`, `tests/`, and CLI tooling
- Base registry for loading and discovering schemas
- Shared validation/error handling infrastructure
- Stamping and hashing utility interfaces
- CI-compatible module layout
- Foundational protocol interfaces
- Canonical `.onex` node handling logic

Rather than duplicating partial setups across multiple tasks, Milestone 0 provides a clean, minimal foundation aligned with ONEX conventions and ready to support all further work.

---

## 🧱 What is an ONEX Node?

An ONEX node is a self-contained, declarative, executable unit defined by a `.onex` metadata file. It can be conceptually viewed as a **function** with a formal, metadata-defined interface. Nodes are:
- Discoverable via `.tree` or registry
- Executable via a defined `entrypoint`
- Validated against schemas and CI rules
- Composable via `dependencies`, `protocols_supported`, and `base_class`
- Optionally stateful, managing internal state via a declared reducer
- Rated via a trust score stub
- Interoperable with ONEX runtimes and agents

---

## 📁 Directory and Module Structure

    ```
    omnibase/
    ├── src/
    │   └── omnibase/
    │       ├── core/              # shared interfaces, registry, loader logic
    │       ├── schema/            # schema registration and JSONSchema tools
    │       ├── tools/             # CLI entrypoints (cli_*.py)
    │       ├── utils/             # shared non-CLI helpers
    │       ├── lifecycle/         # state machine and node lifecycle logic (stubbed)
    │       ├── protocol/          # ported protocols from Foundation
    │       ├── templates/         # scaffolding templates
    │       └── __init__.py
    ├── tests/
    │   ├── core/
    │   ├── schema/
    │   ├── tools/
    │   ├── utils/
    │   ├── lifecycle/
    │   ├── protocol/
    │   ├── template/              # Canonical test templates
    │   └── __init__.py
    ├── docs/
    │   ├── testing.md
    │   ├── migration_log.md
    │   └── README.md
    ├── pyproject.toml
    ├── README.md
    ├── .gitignore
    └── .pre-commit-config.yaml
    ```

---

## ✅ Implementation Checklist

### 🗂️ 1. Repository and Packaging Setup

- [ ] Create `pyproject.toml` with metadata, test tooling, dependencies (e.g., pytest, pydantic, jsonschema, typer)
    - **DoD:** File created, required dependencies listed.
    - **Artifact:** `pyproject.toml`
    - **Reviewer(s):** Infra lead
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add `omnibase` namespace package and `src/omnibase/__init__.py` files for core modules
    - **DoD:** Directories created, `__init__.py` files added for `src/omnibase/`, `core/`, `schema/`, `tools/`, `utils/`, `lifecycle/`, `protocol/`, `templates/`.
    - **Artifact:** `src/omnibase/__init__.py`, `src/omnibase/<module>/__init__.py` (for all core modules)
    - **Reviewer(s):** Infra lead
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Set up editable install (`pip install -e .`) for CLI use
    - **DoD:** Command runs successfully, package is installed.
    - **Artifact:** `pyproject.toml`, installation output
    - **Reviewer(s):** Infra lead
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add top-level `README.md` with project summary and bootstrap milestone context
    - **DoD:** README created, M0 purpose and initial structure documented.
    - **Artifact:** `README.md`
    - **Reviewer(s):** Foundation team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add minimal `docs/README.md` or section in main README explaining the bootstrap milestone, directory structure, and how to run the first CLI/test commands
    - **DoD:** Basic documentation landing page created/updated.
    - **Artifact:** `docs/README.md` or `README.md` section
    - **Reviewer(s):** Foundation team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Create `.gitignore` file with standard entries (e.g., `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.env`, `/dist`)
    - **DoD:** `.gitignore` file created with relevant patterns.
    - **Artifact:** `.gitignore`
    - **Reviewer(s):** Infra lead
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Create `.pre-commit-config.yaml` with `black`, `ruff`, `isort` hooks and usage instructions in README
    - **DoD:** Pre-commit config created, hooks added, instructions documented in README.
    - **Artifact:** `.pre-commit-config.yaml`, `README.md`
    - **Reviewer(s):** Infra lead, Foundation team
    - **Status:** [ ]
    - **PR/Issue:** #

### 📑 2. Protocol Definition and Porting

- [ ] Create `src/omnibase/protocol/` directory and `__init__.py`
    - **DoD:** Directory created, `__init__.py` added.
    - **Artifact:** `src/omnibase/protocol/`
    - **Reviewer(s):** Protocol team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Port core Protocol Interfaces from Foundation codebase to `src/omnibase/protocol/` following naming conventions (`protocol_*.py`)
    - **DoD:** Essential protocol ABCs ported into `src/omnibase/protocol/` (e.g., `registry.py`, `validate.py`, etc.), linting passes. Each ported file contains the abstract definition for a single protocol following `protocol_*.py` naming. Includes `ReducerProtocol`.
    - **Artifact:** `src/omnibase/protocol/*.py` (e.g., `protocol_registry.py`, `protocol_validate.py`, `protocol_reducer.py` etc.)
    - **Reviewer(s):** Protocol team, Infra lead
    - **Status:** [ ]
    - **PR/Issue:** #
    - [ ] Port `RegistryProtocol` as `protocol_registry.py`
    - [ ] Port `ProtocolValidate` as `protocol_validate.py`
    - [ ] Port `ProtocolStamper` as `protocol_stamper.py`
    - [ ] Port `ProtocolCLI` as `protocol_cli.py`
    - [ ] Port `ProtocolTool` as `protocol_tool.py`
    - [ ] Port `ReducerProtocol` as `protocol_reducer.py`
    - [ ] Port other essential protocols as identified (e.g., Logger, Naming Convention, Orchestrator, Output Formatter) using `protocol_` prefix
- [ ] Add minimal usage example or stub for each ported protocol in docstrings or separate canonical templates
    - **DoD:** Basic examples or docstrings added to ported protocol files, illustrating core methods/attributes (e.g., `initial_state`, `dispatch` for `ReducerProtocol`).
    - **Artifact:** `src/omnibase/protocol/*.py` docstrings/examples
    - **Reviewer(s):** Protocol team, Foundation team
    - **Status:** [ ]
    - **PR/Issue:** #

### 🔁 3. Schema Loader and Handlers

- [ ] Implement minimal concrete `SchemaRegistry` class in `core/registry.py` implementing `ProtocolRegistry`
    - **DoD:** `SchemaRegistry` class created in `core/registry.py`, implements abstract methods from `ProtocolRegistry` (imported from `src/omnibase/protocol/registry.py`) with placeholder logic (stubs). Class adheres to `core_*.py` naming if applicable to this file.
    - **Artifact:** `src/omnibase/core/registry.py` (or `src/omnibase/core/core_registry.py` if file prefixing is used)
    - **Reviewer(s):** Infra lead, Protocol team
    - **Status:** [ ]
    - **PR/Issue:** #
    - [ ] Class exists and implements `ProtocolRegistry`
    - [ ] Stub `load_from_disk()` method
    - [ ] Stub `load_mock()` method
    - [ ] Stub `get_node(node_id)` method
- [ ] Implement loader functions for `.yaml` and `.json` schema files in `schema/loader.py`
    - **DoD:** Loader functions exist in `src/omnibase/schema/loader.py` (or `schema/schema_loader.py`), can read YAML/JSON files using a library like PyYAML/json.
    - **Artifact:** `src/omnibase/schema/loader.py` (or `schema/schema_loader.py`)
    - **Reviewer(s):** Schema team, Infra lead
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Create stub `onex-node.yaml` schema file with minimal valid content conforming to the Node Spec (Canonical Draft)
    - **DoD:** File created at canonical location (`src/omnibase/schema/schemas/`), contains basic JSONSchema structure (e.g., `$schema`, `type: object`, `properties`, `required`) and includes all fields marked as `required` in the ONEX Node Spec. Includes placeholder definitions for `meta_type` and a comment/placeholder for the future `reducer` field. Uses hyphen-separated naming (`onex-node.yaml`).
    - **Artifact:** `src/omnibase/schema/schemas/onex-node.yaml`
    - **Reviewer(s):** Schema team, Foundation team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Create stub `state-contract.json` schema file with minimal valid content
    - **DoD:** File created at canonical location (`src/omnibase/schema/schemas/`), contains basic JSONSchema structure (e.g., `$schema`, `type: object`). Uses hyphen-separated naming (`state-contract.json`).
    - **Artifact:** `src/omnibase/schema/schemas/state-contract.json`
    - **Reviewer(s):** Schema team, Foundation team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Ensure schema files reside in `src/omnibase/schema/schemas/` following naming conventions (`hyphen-separated.yaml/.json`)
    - **DoD:** Directory created, stub schema files placed here with correct naming.
    - **Artifact:** `src/omnibase/schema/schemas/` directory with `onex-node.yaml` and `state-contract.json`
    - **Reviewer(s):** Schema team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Loader should handle recursive discovery in `src/omnibase/schema/schemas/` and fail gracefully on malformed formats.
    - **DoD:** Loader function stubs include recursive directory scanning placeholder and basic try/except for parsing errors.
    - **Artifact:** `src/omnibase/schema/loader.py` (or `schema_loader.py`)
    - **Reviewer(s):** Schema team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add schema auto-registration stub in registry/schema loader for M1 use
    - **DoD:** Placeholder logic in `SchemaRegistry` or loader to register schemas upon loading.
    - **Artifact:** `src/omnibase/core/registry.py` (or `core_registry.py`), `src/omnibase/schema/loader.py` (or `schema_loader.py`)
    - **Reviewer(s):** Schema team, Infra lead
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Stub out plugin discovery mechanism in registry/tools to support future validator extensions and org-specific rules (M2+)
    - **DoD:** Placeholder logic for plugin discovery added to `SchemaRegistry` stub and relevant tool stubs (e.g., validator).
    - **Artifact:** `src/omnibase/core/registry.py` (or `core_registry.py`), `src/omnibase/tools/cli_validate.py` (stub)
    - **Reviewer(s):** Infra lead
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Write unit test in `tests/core/test_registry.py` for basic registry loading and stub lookup
    - **DoD:** Test file created in `tests/core/`, tests `SchemaRegistry.load_from_disk()`/`load_mock()` stubs and `get_node()` stub. Test code uses the parametrized `registry` fixture (defined in `conftest.py`).
    - **Artifact:** `tests/core/test_registry.py`
    - **Reviewer(s):** Test team, Infra lead
    - **Status:** [ ]
    - **PR/Issue:** #

### 🔍 4. Validator and Metadata Tools (Stub Only)

- [ ] Create `tools/cli_validate.py` and `tools/cli_stamp.py` implementing respective protocols, as stub CLI entrypoints using `typer`
    - **DoD:** Files created in `src/omnibase/tools/`, implement abstract methods from `ProtocolValidate` and `ProtocolStamper` (imported from `src/omnibase/protocol/`) with placeholder logic (stubs), basic Typer CLI structure in place for each file. Files adhere to `cli_*.py` naming.
    - **Artifact:** `src/omnibase/tools/cli_validate.py`, `src/omnibase/tools/cli_stamp.py`
    - **Reviewer(s):** Tool team, Protocol team
    - **Status:** [ ]
    - **PR/Issue:** #
    - [ ] Implements `ProtocolValidate` (stub)
    - [ ] Implements `ProtocolStamper` (stub)
- [ ] Canonical CLI tool name: `onex` (use consistently in entrypoints, help text, and docs)
    - **DoD:** `pyproject.toml` entry point configured as `onex`, main CLI help text uses `onex`.
    - **Artifact:** `pyproject.toml`, `src/omnibase/tools/cli_main.py` (stub)
    - **Reviewer(s):** Tool team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add CLI `cli_main.py` entrypoint to route subcommands; expose as `__main__` script via `pyproject.toml`
    - **DoD:** `cli_main.py` created in `src/omnibase/tools/`, uses `typer` to call stub validator/stamper functions, `pyproject.toml` entry point configured.
    - **Artifact:** `src/omnibase/tools/cli_main.py`, `pyproject.toml`
    - **Reviewer(s):** Tool team, Infra lead
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Stub validation interface: `validate_onex(path)` within `cli_validate.py` using `ProtocolValidate`
    - **DoD:** `validate_onex` function stub exists in `cli_validate.py`, matches `ProtocolValidate` signature.
    - **Artifact:** `src/omnibase/tools/cli_validate.py` (stub)
    - **Reviewer(s):** Tool team, Protocol team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Stub stamping interface: `stamp_metadata(path)` within `cli_stamp.py` using `ProtocolStamper`
    - **DoD:** `stamp_metadata` function stub exists in `cli_stamp.py`, matches `ProtocolStamper` signature.
    - **Artifact:** `src/omnibase/tools/cli_stamp.py` (stub)
    - **Reviewer(s):** Tool team, Protocol team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Stub logic in `validate_onex` to load and parse a `.onex.yaml` file using the schema loader
    - **DoD:** `validate_onex` stub in `cli_validate.py` includes calls to schema loader for a given path argument, basic placeholder for parsing result (e.g., returning a dict stub).
    - **Artifact:** `src/omnibase/tools/cli_validate.py` (stub)
    - **Reviewer(s):** Tool team, Schema team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Stub logic in `validate_onex` to read `dependencies`, `base_class`, `meta_type`, and `reducer` fields from loaded `.onex` stub
    - **DoD:** `validate_onex` stub includes placeholder code to access these fields (if they exist in the loaded dict stub), e.g., `onex_data.get('dependencies', [])`. Includes placeholders for new fields (`meta_type`, `reducer`).
    - **Artifact:** `src/omnibase/tools/cli_validate.py` (stub)
    - **Reviewer(s):** Tool team, Foundation team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Stub URI parsing logic (e.g., regex check for `<type>://<namespace>@<version_spec>`) within a utility module (e.g., `utils/uri_parser.py`)
    - **DoD:** Basic parsing function stub exists in `src/omnibase/utils/uri_parser.py` (or `utils/utils_uri_parser.py`), uses regex pattern from spec, returns a placeholder structure or raises a placeholder error. File adheres to `utils_*.py` naming if applicable.
    - **Artifact:** `src/omnibase/utils/uri_parser.py` (stub)
    - **Reviewer(s):** Utility team, Foundation team
    - **Status:** [ ]
    - **PR/Issue:** #

### 🧪 5. Testing & CI Framework Setup

- [ ] Add `tests/` directory structure mirroring `src/omnibase/` modules
    - **DoD:** `tests/` directory created with subdirectories `core/`, `schema/`, `tools/`, `utils/`, `lifecycle/`, `protocol/`, `template/`.
    - **Artifact:** `tests/core/`, `tests/schema/`, etc.
    - **Reviewer(s):** Test team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add `tests/__init__.py` and `tests/<module>/__init__.py` files
    - **DoD:** `__init__.py` files added to all test directories.
    - **Artifact:** `tests/__init__.py`, `tests/<module>/__init__.py`
    - **Reviewer(s):** Test team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add `tests/conftest.py` with `registry` fixture swapping logic
    - **DoD:** File created in `tests/`, `registry` fixture implemented with mock/real stubs (calling `SchemaRegistry.load_mock`/`load_from_disk` stubs).
    - **Artifact:** `tests/conftest.py`
    - **Reviewer(s):** Test team, Infra lead
    - **Status:** [ ]
    - **PR/Issue:** #
    - [ ] Implements `registry` fixture
    - [ ] Mock/real stubs implemented
- [ ] Add placeholder CI workflow (`.github/workflows/bootstrap.yml`) that runs tests and lints
    - **Suggested CI filename:** `.github/workflows/bootstrap.yml`
    - **DoD:** CI file created in `.github/workflows/`, linting and test execution steps defined for push/pull requests.
    - **Artifact:** `.github/workflows/bootstrap.yml`
    - **Reviewer(s):** CI team, Infra lead
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Configure pytest to run tests from `tests/` directory
    - **DoD:** `pyproject.toml` or `pytest.ini` configured to discover and run tests.
    - **Artifact:** `pyproject.toml` or `pytest.ini`
    - **Reviewer(s):** Test team, Infra lead
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Include ruff, black, isort lint hooks in `.pre-commit-config.yaml` and enforce in CI
    - **DoD:** Pre-commit hooks configured in `.pre-commit-config.yaml`, CI workflow includes running pre-commits or equivalent linters, failures block merge.
    - **Artifact:** `.pre-commit-config.yaml`, `.github/workflows/bootstrap.yml`
    - **Reviewer(s):** CI team, Infra lead
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add pre-commit hook or CI step for schema validation in `src/omnibase/schema/schemas/` (validate all schemas for JSONSchema/YAML compliance)
    - **DoD:** Schema linting hook/step configured and running in pre-commit or CI, fails on malformed schemas.
    - **Artifact:** `.pre-commit-config.yaml` or `.github/workflows/bootstrap.yml`
    - **Reviewer(s):** CI team, Schema team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add CLI smoke test (`onex --help`) to `tests/tools/test_cli_main.py`
    - **DoD:** Test file created in `tests/tools/`, basic CLI invocation test passes.
    - **Artifact:** `tests/tools/test_cli_main.py`
    - **Reviewer(s):** Test team, Tool team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Create example node directory based on recommended layout with `node.onex.yaml` stub
    - **DoD:** Directory structure created (`nodes/example_node/`), minimal `node.onex.yaml` stub file added in `nodes/example_node/` conforming to the Node Spec. Include placeholder `src/` and `tests/` directories within the example node directory structure.
    - **Artifact:** `nodes/example_node/node.onex.yaml` (stub), `nodes/example_node/src/`, `nodes/example_node/tests/`
    - **Reviewer(s):** Foundation team, Schema team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add a `.tree` file stub at the repository root referencing the example `node.onex.yaml`
    - **DoD:** `.tree` file created at the repo root, references the example node's `node.onex.yaml` path.
    - **Artifact:** `.tree` (stub)
    - **Reviewer(s):** Foundation team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add CI step to validate the example `node.onex.yaml` stub against the `onex-node.yaml` schema stub using the validator stub
    - **DoD:** CI workflow includes a step calling `onex validate nodes/example_node/node.onex.yaml` (or similar CLI command), the validator stub runs and reports success for the valid stub file (placeholder logic in validator).
    - **Artifact:** `.github/workflows/bootstrap.yml`, `src/omnibase/tools/cli_validate.py` (stub)
    - **Reviewer(s):** CI team, Tool team, Schema team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add CI/lint/test badge to `README.md` as soon as workflow is live
    - **DoD:** Badges added to README and displaying correctly (e.g., using Shield.io or similar).
    - **Artifact:** `README.md`
    - **Reviewer(s):** Foundation team, CI team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Add placeholder for test coverage report/badge in `README.md`
    - **DoD:** Placeholder text or badge added to README, indicating where coverage will be displayed.
    - **Artifact:** `README.md`
    - **Reviewer(s):** Foundation team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Create unit test for .onex metadata parsing using the validator stub
    - **DoD:** Test file created (e.g., `tests/tools/test_validator_stub.py`), test loads and parses the example `node.onex.yaml` stub using the validator stub's internal parsing logic.
    - **Artifact:** `tests/tools/test_validator_stub.py` (or similar)
    - **Reviewer(s):** Test team, Tool team
    - **Status:** [ ]
    - **PR/Issue:** #

### ⚠️ 6. Error Handling and Taxonomy

- [ ] Define minimal error taxonomy or base error class in `core/errors.py`
    - **DoD:** `core/errors.py` created in `src/omnibase/core/`, contains base exception class (e.g., `OmniBaseError`).
    - **Artifact:** `src/omnibase/core/errors.py`
    - **Reviewer(s):** Core team, Foundation team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Ensure shared error types are used across tools and loaders (stubs)
    - **DoD:** Tool and loader stubs (`cli_validate.py`, `cli_stamp.py`, `loader.py`) include basic error handling using the defined base error class.
    - **Artifact:** `src/omnibase/tools/*.py` (stubs), `src/omnibase/schema/loader.py` (stub)
    - **Reviewer(s):** Core team, Tool team, Schema team
    - **Status:** [ ]
    - **PR/Issue:** #

### 📄 7. Canonical Testing Document

- [ ] Add canonical testing document (`docs/testing.md`) describing markerless, registry-swappable philosophy
    - **DoD:** Document created in `docs/`, includes key principles (no markers, fixture swapping), pytest guidance, and reference to registry fixture.
    - **Artifact:** `docs/testing.md`
    - **Reviewer(s):** Foundation team, Test team
    - **Status:** [ ]
    - **PR/Issue:** #
- [ ] Include pytest registry fixture example and guidance for contributors in `docs/testing.md`
    - **DoD:** `docs/testing.md` includes a code example and explanation for the parametrized registry fixture.
    - **Artifact:** `docs/testing.md`
    - **Reviewer(s):** Foundation team, Test team
    - **Status:** [ ]
    - **PR/Issue:** #

### 🧰 8. Canonical Template Files

- [ ] Create canonical template files for node metadata and scaffolding in `src/omnibase/templates/`
    - **DoD:** Template files created in `src/omnibase/templates/`, follow Naming Conventions (`*.tmpl`), include placeholder content for scaffolding based on the examples in this document.
    - **Artifact:** `src/omnibase/templates/tool_node.yaml.tmpl`, `src/omnibase/templates/test_sample.py.tmpl`, `src/omnibase/templates/cli_tool.py.tmpl`, `src/omnibase/templates/protocol.py.tmpl`, `src/omnibase/templates/utils.py.tmpl` etc.
    - **Reviewer(s):** CAIA, Foundation team
    - **Status:** [ ]
    - **PR/Issue:** #
    - [ ] Files created in `src/omnibase/templates/`
    - [ ] Follow Naming Conventions (`.tmpl` extension)
    - [ ] Reviewed by CAIA

---

## 🧠 The ONEX Node as a Function: Conceptual Model

> This section describes the conceptual model of an ONEX node as a declarative function, providing context for its design and behavior.

An ONEX node can be viewed as a **function** with a well-defined, metadata-driven interface. By default, nodes are intended to operate similarly to **pure functions** – deterministic transformations of input state into output state, without side effects. However, the model also supports **impure nodes** through explicit metadata flags and optional embedded reducers, allowing for controlled side effects (e.g., I/O, logging, memory management, retries).

### Core Principles

- **Input/Output is explicit**: Defined via `state_contract`
- **Execution is declarative**: Entrypoints point to callable scripts or modules
- **Purity is preferred**: Nodes are functional by default where feasible
- **State is scoped**: Persistent/impure state is isolated and declared
- **Metadata drives everything**: All behavior is declared in `.onex`

### Node Typing: Pure vs Impure

| Type        | Characteristics                                           | Metadata Hint                  |
|-------------|-----------------------------------------------------------|--------------------------------|
| Pure        | Stateless, deterministic transformation, schema-driven      | Typically `meta_type: tool`    |
| Impure      | May have I/O, external dependencies, manage internal state  | `meta_type: agent`, explicit `reducer:` or side-effect declaration |
| Middleware  | Primarily performs side effects (e.g., logging, caching)    | `meta_type: utility` or specific side-effect declaration |

---

## 🌀 Reducer-Based Internal State

Some nodes require **local state transitions** beyond a single input/output pass. ONEX supports an embedded reducer model to define internal state machines.

### Reducer Protocol

All reducers must implement:

    ```python
    class ReducerProtocol:
        def initial_state(self) -> dict:
            """Returns the initial state for the reducer."""
            ...

        def dispatch(self, state: dict, action: dict) -> dict:
            """Processes an action and returns the next state."""
            ...
    ```

The checklist item for porting this protocol definition is included in the main Implementation Checklist (Section 2).

### Use Cases

- Retry tracking for idempotent operations
- Local orchestration or branching within a node
- Stepwise generation (e.g., in scaffold nodes)
- Buffered/cached state across subcalls
- Managing long-running tasks or conversations within an agent node

### Example (`reducer` field in .onex - Future)

    ```yaml
    # Proposed addition to node.onex.yaml schema (Future M2+)
    reducer: "src/omnibase/reducers/retry_step_reducer.py" # Path to the reducer implementation
    ```

---

## 📜 Internal vs External State (Explanation)

- **External State**: Defined via `state_contract`, validated against its schema, passed *between* nodes (like function arguments/return values). This is the node's public data interface.
- **Internal State**: Managed via the node's embedded `reducer` (Future M2+), scoped to a single node’s runtime instance, not validated against a public schema unless explicitly declared. This is the node's private, internal state.

This distinction supports **encapsulation** and **composability**—external consumers interact only with the node’s declared external state interface.

---

## 🧠 Middleware Nodes (Impure Helpers) (Explanation)

Middleware nodes perform impure tasks—logging, saving files, updating memory, calling external services. They are useful in workflows for their side effects rather than producing a transformational business logic output.

- Can be marked with `meta_type: utility` or a more specific future `meta_type` if defined.
- Often leverage reducers for stateful side effects or manage side effects directly.
- Should clearly document what external systems or state they affect.

---

## 📦 Orchestration Per Node (Explanation)

ONEX supports **decentralized orchestration**. Each node can:
- Declare its direct dependencies (`dependencies`)
- Handle local state transitions with a reducer (`reducer`)
- Define its chaining or compositional relationships via `base_class`, `protocols_supported`, or future fields (`generated_by`, `consumes`, `produces`).

This model enables recursive composition and makes each node a potentially autonomous participant in a larger system or workflow, with linking metadata declaring the relationships.

---

## 🔁 Node = Function (Redux-Like) (Explanation)

At a conceptual level, an ONEX node is:

    ```
    (input_state: dict) -> (output_state: dict)
    ```

This transformation is performed by the code at the `entrypoint`. The function's behavior is optionally enhanced with:

- Internal state managed by a `reducer` (Future M2+)
- Composability links (`dependencies`, `base_class`, future `consumes`/`produces`)
- Trust/validation metadata (`trust_score_stub`, `hash`, etc.)
- CI and validation rules (`.tree`, `schema_version`, validation enforcement)
- Defined Execution Environment (`entrypoint`, `runtime_language_hint`)

---

## 🔐 Trust and Reducer Cohesion (Explanation)

Because reducers define dynamic, potentially stateful behavior within a node, they will be integrated into the trust and validation model in future milestones:
- The `reducer` field will reference the implementation file path in `.onex`.
- Reducer implementation files will be subject to validation (e.g., linting, protocol compliance).
- In future releases, reducers may optionally declare a versioned schema for their *internal* state (`reducer_contract`) to aid testing and introspection.

---

## 📑 Protocol Porting: Foundation to ONEX (Explanation)

This section defines the plan for porting essential protocol interfaces from the legacy Foundation module to the ONEX/OmniBase codebase. These protocols form the backbone of all validators, registries, CLI tools, and utilities, and must be present from the bootstrap milestone onward. The checklist items for porting these protocols are included in the main Implementation Checklist (Section 2).

### Protocols to Port
- ProtocolValidateMetadataBlock
- RegistryProtocol
- ProtocolValidatorRegistry
- ProtocolValidate
- ProtocolStamper
- ProtocolTestableCLI
- ProtocolCLI
- ProtocolTool
- ProtocolLogger
- ProtocolYamlUtils
- ProtocolNamingConvention
- OrchestratorProtocol
- OutputFormatterProtocol
- **ReducerProtocol** (Added for stateful nodes)

### Directory Structure
- Place all protocol definitions in `src/omnibase/protocol/` following naming conventions (`protocol_*.py`).
- Add an `__init__.py` that re-exports the canonical set.

### Documentation and Templates
- Reference these protocols in documentation (e.g., `docs/testing.md`) and code docstrings/examples.
- Provide a minimal usage example or stub for each protocol in docstrings or separate canonical templates.
- Require that all protocol changes are versioned and reviewed alongside schema/protocol changes.
- Document protocol usage and evolution policy in documentation.

---

## 📦 Legacy Migration Plan (Explanation)

> **Note:** While this migration plan is scaffolded in Milestone 0 documentation, the actual execution of migrating legacy tests and code will span Milestone 1 and possibly Milestone 2, as ONEX protocols and runtime stabilize. Migration progress and deliverables should be tracked across these milestones using a migration log (`docs/migration_log.md`).

### Hybrid Migration-by-Legacy Staging Approach

To ensure a safe, reviewable, and incremental migration from the Foundation codebase to ONEX/OmniBase standards, we will use the following process:

1. **Initial Stage:**
   - Move all relevant files from the previous foundation (protocols, validators, utilities, etc.) into a `legacy/` directory in the new repo.
   - Mark the `legacy/` directory as non-canonical and for migration only. Exclude it from production builds, CI, and documentation.
2. **Migration Stage:**
   - Port/refactor files one at a time into their new canonical locations, following all naming and protocol standards.
   - As each file is migrated, remove it from `legacy/`.
   - Track migration progress in a migration log (e.g., `docs/migration_log.md`).
3. **Final Stage:**
   - Once all files are migrated, delete the `legacy/` directory.

This approach ensures nothing is lost, migration is incremental and reviewable, and the codebase remains clean and policy-compliant.

### Best Practices (for Migration Execution)

- Migrate to protocol-driven tests aligned with `docs/testing.md`.
- Replace on-disk test files with in-memory fixtures.
- Use parametrized `pytest` test formats.
- Enforce coverage parity between legacy and new tests where feasible.
- Require a migration log entry for each ported component, documenting source, approach, and changes.

---

## 🌐 URI Format for Linking Fields (Explanation)

### Canonical Format

    ```
    <type>://<namespace>@<version_spec>
    ```

- `<type>`: `tool`, `validator`, `agent`, `model`, `schema`, `plugin`
- `<namespace>`: Dot-delimited identifier (e.g. `core.schema_validator`)
- `<version_spec>`: Semver or constraint (e.g. `1.0.0`, `>=0.2.0`)

### Examples

    ```yaml
    dependencies:
      - tool://tools.tree_generator@>=0.2.0
      - validator://core.schema_validator@1.0.0
    base_class:
      - validator://core.base@^1.0
    ```

The checklist item for stubbing URI parsing logic is included in the main Implementation Checklist (Section 4).

---

## 📜 State Contract (Input/Output Interface) (Explanation)

The `state_contract` field links to a JSON Schema file that defines the node’s expected input/output shape. Example:

    ```json
    {
      "title": "SummaryBlockState",
      "type": "object",
      "properties": {
        "summary": { "type": "string" },
        "status": { "type": "string" }
      },
      "required": ["summary", "status"]
    }
    ```

- File is referenced via `state_contract: "state_contract://summary_block_schema.json"`
- Schema lives under `src/omnibase/schema/schemas/`
- Used for both runtime validation and CI enforcement

The checklist items for creating the state contract schema stub and ensuring its resolution logic is stubbed are included in the main Implementation Checklist (Section 3).

---

## ✅ Validation Rules (Explanation)

Milestone 1 CI must enforce:

- All `.onex` files must pass schema validation (`onex-node.yaml`)
- `uuid` must be a valid v4 UUID
- `hash` must match file hash of `node.onex.yaml`
- `lifecycle` must be one of: `draft`, `active`, `deprecated`, `archived`
- `.tree` file must reference this node correctly
- `entrypoint.target` must exist and be executable

Optional (Stretch):
- Signature block validation
- Trust score consistency across executions
- URI parsing and dereferencing for dependency validation

The checklist items for setting up basic `.onex` schema validation and related stubs in CI and the validator are included in the main Implementation Checklist (Sections 4 and 5).

---

## 🔐 Trust and Signature Fields (Explanation)

Optional, planned for M3/M4:

- `trust_score_stub` records execution history
- `signature_block` enables cryptographic verification of the node metadata

---

## 🔧 Templates and Node Scaffolding (Explanation)

ONEX will support generation of nodes via reusable templates. The checklist item for creating these template files is included in the main Implementation Checklist (Section 8).

- Templates reside in `src/omnibase/templates/`
- Scaffold nodes (coming in Milestone 2) will generate compliant `.onex`, source, and test files

---

## 📁 .tree Discovery Format (Explanation)

Each project or container should have a top-level `.tree` file that enumerates valid nodes. Example:

    ```yaml
    nodes:
      - name: extract_summary_block
        path: extract_summary_block/node.onex.yaml
      - name: validate_tree_file
        path: tree_validator/node.onex.yaml
    ```

The checklist items for creating a `.tree` stub and ensuring its reference in CI are included in the main Implementation Checklist (Section 5).

---

## 📚 Cross-References (Explanation)

- [`src/omnibase/schema/schemas/onex-node.yaml`](../schema/schemas/onex-node.yaml)
- [`src/omnibase/schema/schemas/execution-result.json`](../schema/schemas/execution-result.json)
- [`src/omnibase/schema/schemas/state-contract.json`](../schema/schemas/state-contract.json)
- [Milestone 1 Checklist](../milestones/milestone_1_protocol_and_schema.md)
- [ONEX Bootstrap / Milestone 0](./milestone_0_bootstrap.md)

---

## 🧰 Canonical Templates (Explanation Snippets)

> These code snippets illustrate the *structure* of canonical implementations and are intended to guide contributors. The actual template *files* reside in `src/omnibase/templates/` and `tests/template/`.

### `src/omnibase/core/registry.py` (Illustrative Snippet)

    ```python
    from omnibase.protocol.registry import RegistryProtocol # Import the protocol

    class SchemaRegistry(RegistryProtocol): # Implement the protocol
        def __init__(self):
            self._schemas = {} # Placeholder for schema storage

        @classmethod
        def load_from_disk(cls):
            # Stub: Placeholder for M1 schema loading logic
            # M0 ensures this method exists and conforms to protocol
            print("Stub: Loading schemas from disk")
            instance = cls()
            # In M0, load the minimal onex_node.yaml and state_contract.json stubs
            # In M1+, load all schemas and register them
            return instance

        @classmethod
        def load_mock(cls):
            # Stub: Placeholder for M1 mock schema loading logic
            # M0 ensures this method exists and conforms to protocol
            print("Stub: Loading mock schemas")
            instance = cls()
            # In M0, add minimal stub data or loaded stub schemas
            return instance

        def get_node(self, node_id: str):
            # Stub: Placeholder for M1 node lookup logic
            # M0 ensures this method exists and conforms to protocol
            print(f"Stub: Getting node {node_id}")
            # In M0, return a minimal stub dict that allows tests to pass basic assertions
            return {"name": node_id, "stub": True, "dependencies": [], "base_class": []} # Return a minimal stub dict with required/optional fields
    ```

### `src/omnibase/tools/cli_validate.py` (Illustrative Snippet)

    ```python
    import typer
    from typing import Any
    from omnibase.protocol.validate import ProtocolValidate # Import the protocol
    from omnibase.schema.loader import load_onex_yaml # Import schema loader stub
    from omnibase.utils.uri_parser import parse_uri # Import URI parser stub
    from omnibase.core.errors import OmniBaseError # Import error base

    class MetadataValidator(ProtocolValidate): # Implement the protocol (stub)
        def __init__(self, schema_registry): # M1+ will inject registry
            # In M0, registry is likely passed in here or accessed globally (stub)
            self.registry = schema_registry # Stub for registry
            # Stub: Placeholder for M1 schema storage/lookup
            self.onex_schema = {} # Stub for ONEX schema
            print("Stub: Initializing MetadataValidator")

        def validate(self, path: str) -> bool:
            # Stub: Placeholder for M1 validation logic
            print(f"Stub: Validating .onex file at {path}")

            try:
                # Stub: Load and parse the .onex file using the schema loader stub
                onex_data = load_onex_yaml(path) # Use schema loader stub

                # Stub: Access and read dependencies/base_class fields
                dependencies = onex_data.get('dependencies', [])
                base_classes = onex_data.get('base_class', [])
                print(f"Stub: Found dependencies: {dependencies}")
                print(f"Stub: Found base_class: {base_classes}")

                # Stub: Parse URIs using the URI parser stub
                for dep_uri in dependencies + base_classes:
                     parsed_uri = parse_uri(dep_uri) # Use URI parser stub
                     print(f"Stub: Parsed URI: {dep_uri} -> {parsed_uri}")
                     # M1+ would validate against registry/format

                # Stub: Validate hash (placeholder)
                # Stub: Ensure entrypoint.target exists (placeholder)

                # Stub validation logic (M1+ will do full schema validation)
                if not onex_data or not isinstance(onex_data, dict):
                     raise OmniBaseError("Stub validation failed: Could not load .onex data")
                if 'schema_version' not in onex_data: # Basic stub check
                     raise OmniBaseError("Stub validation failed: Missing schema_version")


                print("Stub: .onex validation logic placeholder passed")
                return True # Stub success

            except Exception as e:
                # Use error base for predictable failure
                raise OmniBaseError(f"Stub .onex validation failed: {e}")


    # Typer CLI command stub
    app = typer.Typer()

    @app.command()
    def validate(path: str = typer.Argument(..., help=".onex file path to validate.")):
        # In M0, validator stub is instantiated and called
        # M1+ will handle dependency injection of registry etc.
        print(f"Stub: onex validate command called for {path}")
        # Instantiate validator stub (M0 does simple instantiation)
        validator_stub = MetadataValidator(schema_registry=None) # Pass stub registry or None in M0
        try:
            validator_stub.validate(path)
            print("Stub: Validation successful (M0 placeholder)")
        except OmniBaseError as e:
            print(f"Stub: Validation failed (M0 placeholder): {e}")
            raise typer.Exit(code=1)


    # Example usage in cli_main.py:
    # from .cli_validate import app as validate_app
    # cli_app = typer.Typer()
    # cli_app.add_typer(validate_app, name="validate")
    # ... add other tool apps
    # if __name__ == "__main__":
    #     cli_app()
    ```

### `src/omnibase/utils/uri_parser.py` (Illustrative Snippet)

    ```python
    import re
    from omnibase.core.errors import OmniBaseError # Import error base

    # Canonical URI format regex (example)
    URI_PATTERN = re.compile(r"^(tool|validator|agent|model|schema|plugin)://([^@]+)@(.+)$")

    def parse_uri(uri_string: str) -> dict:
        # Stub: Placeholder for M1 URI parsing logic
        print(f"Stub: Parsing URI: {uri_string}")
        match = URI_PATTERN.match(uri_string)
        if not match:
            raise OmniBaseError(f"Stub URI parsing failed: Invalid format for {uri_string}")

        uri_type, namespace, version_spec = match.groups()
        print(f"Stub: Parsed: Type={uri_type}, Namespace={namespace}, Version={version_spec}")

        # In M0, just return the parsed components.
        # M1+ would add more robust validation and potentially dereferencing lookup stubs.
        return {
            "type": uri_type,
            "namespace": namespace,
            "version_spec": version_spec,
            "original": uri_string # Keep original for reference
        }

    # Add other utility functions...
    ```

---

## 📄 Canonical Testing Document (Explanation Snippets)

> These explanation snippets are intended to reside within the `docs/testing.md` file, providing canonical guidance on test structure and dependency handling.

### Registry Swapping in Tests (Example Snippet for `docs/testing.md`)

    ```python
    import pytest
    from omnibase.core.registry import SchemaRegistry # Import the concrete registry stub

    @pytest.fixture(params=["mock", "real"])
    def registry(request):
        """
        Pytest fixture to swap between mock and real registry implementations.
        In M0, this uses the minimal SchemaRegistry stub and its load_mock/load_from_disk stubs.
        In M1+, this will use the fully implemented SchemaRegistry.
        """
        if request.param == "mock":
            # In M0, this calls the SchemaRegistry.load_mock() stub
            return SchemaRegistry.load_mock()
        # In M0, this calls the SchemaRegistry.load_from_disk() stub
        return SchemaRegistry.load_from_disk()

    # Example test using the fixture:
    # def test_node_lookup_behavior(registry):
    #     # Test logic here works with either mock or real registry
    #     # In M0, this test will hit the SchemaRegistry.get_node() stub
    #     node_stub = registry.get_node("example_node_id")
    #     assert node_stub.get("stub") is True # Verify stub behavior
    ```

### Test Naming and Scope (Example Snippet for `docs/testing.md`)

> OmniBase/ONEX does **not** distinguish between "unit" and "integration" tests using markers or subdirectories within `tests/`. Instead, test organization relies on directory structure mirroring the source code (`tests/core/`, `tests/tools/`, etc.) and descriptive file names.

While markers like `unit` and `integration` are not used, contributors may still name test files to suggest scope if helpful. For example:
- `tests/tools/test_cli_invocation.py` for basic CLI entry point tests.
- `tests/schema/test_schema_loading.py` for focused tests of the schema loader utility functions.
- `tests/tools/test_validator_stub.py` for testing the minimal logic in the M0 validator stub.

This is optional and not enforced by the test runner's marker system, but promotes clarity for contributors. The canonical `tests/template/test_sample.py` provides a starting point.

---

## 🧰 Canonical Templates (Explanation Snippets)

> These code snippets illustrate the *structure* of canonical implementations and are intended to guide contributors. The actual template *files* reside in `src/omnibase/templates/` and `tests/template/`.

### `src/omnibase/core/registry.py` (Illustrative Snippet)

    ```python
    from omnibase.protocol.registry import RegistryProtocol # Import the protocol

    class SchemaRegistry(RegistryProtocol): # Implement the protocol
        def __init__(self):
            self._schemas = {} # Placeholder for schema storage

        @classmethod
        def load_from_disk(cls):
            # Stub: Placeholder for M1 schema loading logic
            # M0 ensures this method exists and conforms to protocol
            print("Stub: Loading schemas from disk")
            instance = cls()
            # In M0, load the minimal onex_node.yaml and state_contract.json stubs
            # In M1+, load all schemas and register them
            return instance

        @classmethod
        def load_mock(cls):
            # Stub: Placeholder for M1 mock schema loading logic
            # M0 ensures this method exists and conforms to protocol
            print("Stub: Loading mock schemas")
            instance = cls()
            # In M0, add minimal stub data or loaded stub schemas
            return instance

        def get_node(self, node_id: str):
            # Stub: Placeholder for M1 node lookup logic
            # M0 ensures this method exists and conforms to protocol
            print(f"Stub: Getting node {node_id}")
            # In M0, return a minimal stub dict that allows tests to pass basic assertions
            return {"name": node_id, "stub": True, "dependencies": [], "base_class": []} # Return a minimal stub dict with required/optional fields
    ```

### `src/omnibase/tools/cli_validate.py` (Illustrative Snippet)

    ```python
    import typer
    from typing import Any
    from omnibase.protocol.validate import ProtocolValidate # Import the protocol
    from omnibase.schema.loader import load_onex_yaml # Import schema loader stub
    from omnibase.utils.uri_parser import parse_uri # Import URI parser stub
    from omnibase.core.errors import OmniBaseError # Import error base

    class MetadataValidator(ProtocolValidate): # Implement the protocol (stub)
        def __init__(self, schema_registry): # M1+ will inject registry
            # In M0, registry is likely passed in here or accessed globally (stub)
            self.registry = schema_registry # Stub for registry
            # Stub: Placeholder for M1 schema storage/lookup
            self.onex_schema = {} # Stub for ONEX schema
            print("Stub: Initializing MetadataValidator")

        def validate(self, path: str) -> bool:
            # Stub: Placeholder for M1 validation logic
            print(f"Stub: Validating .onex file at {path}")

            try:
                # Stub: Load and parse the .onex file using the schema loader stub
                onex_data = load_onex_yaml(path) # Use schema loader stub

                # Stub: Access and read dependencies/base_class fields
                dependencies = onex_data.get('dependencies', [])
                base_classes = onex_data.get('base_class', [])
                print(f"Stub: Found dependencies: {dependencies}")
                print(f"Stub: Found base_class: {base_classes}")

                # Stub: Parse URIs using the URI parser stub
                for dep_uri in dependencies + base_classes:
                     parsed_uri = parse_uri(dep_uri) # Use URI parser stub
                     print(f"Stub: Parsed URI: {dep_uri} -> {parsed_uri}")
                     # M1+ would validate against registry/format

                # Stub: Validate hash (placeholder)
                # Stub: Ensure entrypoint.target exists (placeholder)

                # Stub validation logic (M1+ will do full schema validation)
                if not onex_data or not isinstance(onex_data, dict):
                     raise OmniBaseError("Stub validation failed: Could not load .onex data")
                if 'schema_version' not in onex_data: # Basic stub check
                     raise OmniBaseError("Stub validation failed: Missing schema_version")


                print("Stub: .onex validation logic placeholder passed")
                return True # Stub success

            except Exception as e:
                # Use error base for predictable failure
                raise OmniBaseError(f"Stub .onex validation failed: {e}")


    # Typer CLI command stub
    app = typer.Typer()

    @app.command()
    def validate(path: str = typer.Argument(..., help=".onex file path to validate.")):
        # In M0, validator stub is instantiated and called
        # M1+ will handle dependency injection of registry etc.
        print(f"Stub: onex validate command called for {path}")
        # Instantiate validator stub (M0 does simple instantiation)
        validator_stub = MetadataValidator(schema_registry=None) # Pass stub registry or None in M0
        try:
            validator_stub.validate(path)
            print("Stub: Validation successful (M0 placeholder)")
        except OmniBaseError as e:
            print(f"Stub: Validation failed (M0 placeholder): {e}")
            raise typer.Exit(code=1)


    # Example usage in cli_main.py:
    # from .cli_validate import app as validate_app
    # cli_app = typer.Typer()
    # cli_app.add_typer(validate_app, name="validate")
    # ... add other tool apps
    # if __name__ == "__main__":
    #     cli_app()
    ```

### `src/omnibase/utils/uri_parser.py` (Illustrative Snippet)

    ```python
    import re
    from omnibase.core.errors import OmniBaseError # Import error base

    # Canonical URI format regex (example)
    URI_PATTERN = re.compile(r"^(tool|validator|agent|model|schema|plugin)://([^@]+)@(.+)$")

    def parse_uri(uri_string: str) -> dict:
        # Stub: Placeholder for M1 URI parsing logic
        print(f"Stub: Parsing URI: {uri_string}")
        match = URI_PATTERN.match(uri_string)
        if not match:
            raise OmniBaseError(f"Stub URI parsing failed: Invalid format for {uri_string}")

        uri_type, namespace, version_spec = match.groups()
        print(f"Stub: Parsed: Type={uri_type}, Namespace={namespace}, Version={version_spec}")

        # In M0, just return the parsed components.
        # M1+ would add more robust validation and potentially dereferencing lookup stubs.
        return {
            "type": uri_type,
            "namespace": namespace,
            "version_spec": version_spec,
            "original": uri_string # Keep original for reference
        }

    # Add other utility functions...
    ```

---

## 📂 Notes

- Milestone 0 unblocks Milestone 1 (schema enforcement and runtime)
- Canonical templates, protocols, and test structure must be complete before beginning Milestone 1
- Bootstrap includes only stubs—not full validation logic

---

## Process Enhancements and Contributor Guidance (Explanation)

The following process and documentation enhancements are recommended to further improve maintainability, clarity, and contributor onboarding for this and future milestones:

1. **Batch/Phase Tagging for Checklist Items:**
   - Group checklist items into explicit "batches" or "phases" for execution and tracking. This helps teams coordinate work, enables staged PRs, and reduces context switching.

2. **Explicit Cross-Referencing:**
   - Where checklist items depend on others (e.g., protocol porting before registry implementation), add dependency notes or cross-references. This prevents misordered work and clarifies execution order.

3. **Status Tracking Automation:**
   - Maintain a YAML/JSON manifest of checklist items for CI or dashboard integration. This enables automated status badges, progress bars, or PR gating, and keeps progress visible to all contributors.

4. **Contributor Guidance Section:**
   - Add a short guide at the top or bottom explaining how to use this document, including how to interpret DoD, artifact, reviewer, and status fields. This supports onboarding and consistent usage.

5. **Explicit Policy for Template Evolution:**
   - Define a policy for updating canonical templates (e.g., versioning, review process, required approvals). This ensures templates remain authoritative and up to date.

6. **Future Enhancements/Stretch Goals:**
   - Add a subsection for ideas that are out of scope for Milestone 0 but should be revisited later (e.g., richer plugin discovery, advanced error reporting, automated migration tools). This keeps forward-looking ideas visible and actionable.

7. **CI/CD Integration Guidance:**
   - Briefly describe how to integrate with CI/CD systems, including required secrets, environment variables, and badge setup. This helps new teams or contributors set up automation quickly and correctly.

8. **Glossary or Terminology Table:**
   - Add a glossary at the end of the document for specialized terms (e.g., DoD, artifact, protocol, registry). This aids new contributors and ensures consistent understanding.

9. **Explicit 'Review and Audit' Steps:**
   - For each batch or phase, add a checklist item for review/audit, ensuring that nothing is merged without explicit review against the plan. This enforces quality and policy compliance.

10. **Feedback Loop:**
    - Encourage contributors to propose improvements to the milestone document itself, via a dedicated issue template or PR label. This keeps the document living and responsive to project needs.

These enhancements are intended to be actionable and extensible, supporting a robust, reviewable, and contributor-friendly engineering process for ONEX and OmniBase.