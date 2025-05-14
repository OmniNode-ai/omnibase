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

An ONEX node is a self-contained, declarative, executable unit defined by a `.onex` metadata file. Nodes are:
- Discoverable via `.tree` or registry
- Executable via a defined `entrypoint`
- Validated against schemas and CI rules
- Composable via `dependencies`, `protocols_supported`, and `base_class`
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

- [ ] Create `pyproject.toml` with metadata, test tooling, dependencies
- [ ] Add `omnibase` namespace package and `src/omnibase/__init__.py` files for core modules
- [ ] Set up editable install
- [ ] Add top-level `README.md` with milestone summary
- [ ] Add minimal `docs/README.md` or section in main README explaining the bootstrap milestone, directory structure, and how to run the first CLI/test commands
- [ ] Create `.gitignore` file with standard entries (e.g., `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.env`, `/dist`)
- [ ] Create `.pre-commit-config.yaml` with `black`, `ruff`, `isort` hooks and usage instructions in README

### 📑 2. Protocol Definition and Porting

- [ ] Create `src/omnibase/protocol/` directory and `__init__.py`
- [ ] Port core Protocol Interfaces from Foundation codebase to `src/omnibase/protocol/` following naming conventions
    - [ ] Port `RegistryProtocol` as `protocol_registry.py`
    - [ ] Port `ProtocolValidate` as `protocol_validate.py`
    - [ ] Port `ProtocolStamper` as `protocol_stamper.py`
    - [ ] Port `ProtocolCLI` as `protocol_cli.py`
    - [ ] Port `ProtocolTool` as `protocol_tool.py`
    - [ ] Port other essential protocols as identified (e.g., Logger, Naming Convention, Orchestrator, Output Formatter) using `protocol_` prefix
- [ ] Add minimal usage example or stub for each ported protocol in docstrings or separate canonical templates

### 🔁 3. Schema Loader and Handlers

- [ ] Implement minimal concrete `SchemaRegistry` class in `core/registry.py` implementing `RegistryProtocol`
    - [ ] Class exists and implements `ProtocolRegistry`
    - [ ] Stub `load_from_disk()` method
    - [ ] Stub `load_mock()` method
    - [ ] Stub `get_node(node_id)` method
- [ ] Implement loader functions for `.yaml` and `.json` schema files in `schema/loader.py`
- [ ] Create stub `onex-node.yaml` schema file with minimal valid content conforming to the Node Spec
- [ ] Create stub `state-contract.json` schema file with minimal valid content
- [ ] Ensure schema files reside in `src/omnibase/schema/schemas/` following naming conventions (`hyphen-separated.yaml/.json`)
- [ ] Loader should handle recursive discovery in `src/omnibase/schema/schemas/` and fail gracefully on malformed formats.
- [ ] Add schema auto-registration stub in registry/schema loader for M1 use
- [ ] Stub out plugin discovery mechanism in registry/tools to support future validator extensions and org-specific rules (M2+)
- [ ] Write unit test in `tests/core/test_registry.py` for basic registry loading and stub lookup

### 🔍 4. Validator and Metadata Tooling

- [ ] Create `tools/cli_validate.py` and `tools/cli_stamp.py` implementing respective protocols, as stub CLI entrypoints using `typer`
    - [ ] Implements `ProtocolValidate` (stub)
    - [ ] Implements `ProtocolStamper` (stub)
- [ ] Canonical CLI tool name: `onex` (use consistently in entrypoints, help text, and docs)
- [ ] Add CLI `cli_main.py` entrypoint to route subcommands; expose as `__main__` script via `pyproject.toml`
- [ ] Stub validation interface: `validate_onex(path)` within `cli_validate.py` using `ProtocolValidate`
- [ ] Stub stamping interface: `stamp_metadata(path)` within `cli_stamp.py` using `ProtocolStamper`
- [ ] Stub logic in `validate_onex` to load and parse a `.onex.yaml` file using the schema loader
- [ ] Stub logic in `validate_onex` to read `dependencies` and `base_class` fields from loaded `.onex` stub
- [ ] Stub URI parsing logic (e.g., regex check for `<type>://<namespace>@<version_spec>`) within a utility module (e.g., `utils/uri_parser.py`)

### 🧪 5. Testing and CI Framework

- [ ] Add `tests/` directory structure mirroring `src/omnibase/` modules
- [ ] Add `tests/__init__.py` and `tests/<module>/__init__.py` files
- [ ] Add `tests/conftest.py` with `registry` fixture swapping logic
    - [ ] Implements `registry` fixture
    - [ ] Mock/real stubs implemented
- [ ] Add placeholder CI workflow (`.github/workflows/bootstrap.yml`) that runs tests and lints
    - **Suggested CI filename:** `.github/workflows/bootstrap.yml`
- [ ] Configure pytest to run tests from `tests/` directory
- [ ] Include ruff, black, isort lint hooks in `.pre-commit-config.yaml` and enforce in CI
- [ ] Add pre-commit hook or CI step for schema validation in `src/omnibase/schema/schemas/` (validate all schemas for JSONSchema/YAML compliance)
- [ ] Add CLI smoke test (`onex --help`) to `tests/tools/test_cli_main.py`
- [ ] Create example node directory based on recommended layout with `node.onex.yaml` stub
- [ ] Add a `.tree` file stub at the repository root referencing the example `node.onex.yaml`
- [ ] Add CI step to validate the example `node.onex.yaml` stub against the `onex-node.yaml` schema stub using the validator stub
- [ ] Add CI/lint/test badge to `README.md` as soon as workflow is live
- [ ] Add placeholder for test coverage report/badge in `README.md`

### ⚠️ 6. Error Handling and Taxonomy

- [ ] Define minimal error taxonomy or base error class in `core/errors.py`
- [ ] Ensure shared error types are used across tools and loaders (stubs)

### 📄 7. Canonical Testing Document

- [ ] Add canonical testing document (`docs/testing.md`) describing markerless, registry-swappable philosophy
- [ ] Include pytest registry fixture example and guidance for contributors in `docs/testing.md`

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

## 📄 Canonical `.onex` Metadata Schema (Explanation)

> This section explains the structure and fields of the canonical `.onex` metadata file. The schema definition is the source of truth.

Each node must include a `node.onex.yaml` metadata file located in its top-level directory. This file must conform to the canonical schema defined in [`src/omnibase/schema/schemas/onex-node.yaml`](../src/omnibase/schema/schemas/onex-node.yaml).

    ```yaml
    # node.onex.yaml (example)
    schema_version: "0.1.0"
    name: "extract_summary_block"
    version: "1.0.0"
    uuid: "65dfc205-96f3-4f86-8497-cf6d8a1c4b95"
    author: "foundation"
    created_at: 2025-05-17T10:05:00Z
    last_modified_at: 2025-05-17T10:15:00Z
    description: "Parses a metadata block and extracts summary and status fields for display."
    state_contract: "state_contract://summary_block_schema.json"
    lifecycle: "active"
    hash: "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    entrypoint:
      type: python
      target: src/omnibase/tools/cli_extract_summary_block.py
    namespace: "omninode.tools.extract_summary_block"
    meta_type: "tool"
    runtime_language_hint: "python>=3.11"
    tags: ["metadata", "docs", "summary"]
    trust_score_stub:
      runs: 12
      failures: 0
      trust_score: 1.0
    x-extensions: {}
    protocols_supported: []
    base_class:
      - validator://core.schema_validator@1.0.0
    dependencies:
      - tool://tools.tree_generator@>=0.2.0
    environment: []
    license: "Apache-2.0"
    # Optional field not shown: signature_block
    ```

---

## 🔗 Canonical Linking Fields (Explanation)

Nodes are linkable via metadata fields that describe relationships, composition, and origin. These links enable execution graphs, provenance chains, UI visualization, and dependency resolution.

### M1 Fields (Current)

| Field             | Type     | Description                                            |
|------------------|----------|--------------------------------------------------------|
| `dependencies`    | list     | Other nodes this node requires at runtime             |
| `base_class`      | list     | Interface or abstract class this node adheres to      |
| `protocols_supported` | list | Protocols or standards this node conforms to          |

These fields **must use a standardized URI format** (see below). The checklist items for stubbing parsing and reading these fields are included in the main Implementation Checklist (Section 4).

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

## 📦 File Layout (Recommended)

Each node should be self-contained in its own directory, named to match the `name` in the `.onex`. The checklist items for creating an example node directory and `.onex` stub are included in the main Implementation Checklist (Section 5).

    ```
    extract_summary_block/
    ├── node.onex.yaml
    ├── src/
    │   └── omnibase/
    │       └── tools/
    │           └── cli_extract_summary_block.py
    ├── tests/
    │   └── test_extract_summary_block.py
    ├── README.md
    ```

This layout:
- Ensures tooling and CI can discover node boundaries
- Matches `.tree` generation
- Keeps implementation, metadata, and tests co-located

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

## 🧭 Future Work (Explanation)

| Proposed Field     | Purpose                                                             |
|--------------------|---------------------------------------------------------------------|
| `consumes`         | Declares what formats or data types this node reads                |
| `produces`         | Declares what formats or data types this node emits                |
| `compatible_with`  | Links nodes that can be safely chained (based on state_contract)   |
| `fork_of`          | Declares this node as a fork/derivative of another node            |
| `generated_by`     | Links the tool or node that scaffolded/generated this node         |

- These fields are optional in the current schema but may be added as extensions or in a schema upgrade (v0.2+).
- Validation rules and CI enforcement for them will be introduced in Milestone 3 or later.

---

## 🔁 Schema Extension Strategy (Explanation)

- All schemas must include `schema_version`
- Additive fields allowed in minor versions
- Breaking changes require new schema version
- x-prefixed fields (`x-extensions`) are always ignored by validators and can be used for node-local metadata

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