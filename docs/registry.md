# OmniBase Registry Specification

> **Status:** Canonical (ONEX v0.1 Supersedes)  
> **Maintainers:** foundation-team  
> **Last Updated:** 2025-05-16
> **Precedence:** This document incorporates and is governed by the ONEX v0.1 protocol and metadata specifications. Any conflicting or missing details in previous versions are overridden by ONEX v0.1.

---

## Overview

The OmniBase Registry system is responsible for tracking all registered components:
- Validators
- Tools (transformers)
- Test Cases
- Artifacts
- Pipelines

Registries enable discoverability, dynamic execution, dependency resolution, and metadata-driven orchestration. All validators, tools, tests, and artifacts must be registered and queryable via a uniform protocol.

---

## Registry Types

### 1. `ValidatorRegistry`
Tracks all validator components. Discoverable by:
- Artifact type
- Tags (e.g. `schema`, `canary`)
- Version
- Lifecycle

### 2. `ToolRegistry`
Tracks transformation functions. Supports:
- Toolchain construction
- Versioned composition
- Metadata-based filtering

### 3. `TestCaseRegistry`
Tracks declarative test cases. Filters by:
- Test type (unit, integration, e2e)
- Tags and targets
- Lifecycle phase

### 4. `Artifact` and `Pipeline`
Artifacts are typed input/output units in CAS. Pipelines are ordered chains of tools/validators.

---

## Discovery Protocol

```python
class Registry(Protocol):
    def find(self, query: RegistryQuery) -> list[RegistryEntry]: ...
    def resolve(self, uuid: str, version: Optional[str] = None) -> RegistryEntry: ...
    def search(self, filters: dict[str, Any]) -> list[RegistryEntry]: ...
    def register(self, entry: RegistryEntry) -> None: ...
```

---

## Query Patterns

All registries support query-by:
- Input/output types (via `Artifact[T]` and `Result[U]`)
- Tags (`canary`, `pre-commit`, etc.)
- Version (`SemVer` range supported)
- Lifecycle (`canary`, `stable`, `deprecated`, `experimental`)
- Source (`hardcoded`, `agent-generated`, `external`)
- UUID or name
- Capabilities
- Status (`active`, `deprecated`, `draft`)

### Query Fields

| Field          | Description                        |
|----------------|------------------------------------|
| `uuid`         | Global identifier                  |
| `name`         | Human-readable label               |
| `tags`         | Filter execution stages, CLI runs  |
| `type`         | Validator, tool, test, etc.        |
| `version_spec` | SemVer range (`>=0.1.0,<0.2.0`)     |
| `capabilities` | Required permissions               |
| `status`       | `active`, `deprecated`, `draft`    |
| `lifecycle`    | `canary`, `stable`, `experimental` |

---

## Metadata Block (Canonical Schema)

Each registered component must have a metadata block (in-file or sidecar).

    # === OmniNode:Metadata ===
    metadata_version: "0.2.1"
    schema_version: "1.1.0"
    uuid: "123e4567-e89b-12d3-a456-426614174000"
    name: "example_validator"
    namespace: "foundation.script.validate"
    version: "0.1.0"
    type: "validator"
    entrypoint: "python_validate_example.py"
    protocols_supported: ["O.N.E. Core v0.1"]
    author: "OmniNode Team"
    owner: "foundation-team"
    created_at: "2025-05-12T12:00:00+00:00"
    last_modified_at: "2025-05-13T10:00:00+00:00"
    parent_id: "uuid_of_root_validator_metadata_block"
    child_ids: ["uuid_of_child1_metadata", "uuid_of_child2_metadata"]
    dependencies:
      - id: "tool_fix_format_headers_uuid"
        type: "tool"
        version_spec: ">=0.1.0,<0.2.0"
        required: true
    tags: ["canary", "pre-commit"]
    lifecycle: "canary"
    status: "active"
    idempotent: true
    description: "A canonical example of a validator metadata block."
    # === /OmniNode:Metadata ===

---

## Version Resolution

- Registry uses a modified Pubgrub algorithm:
    - Enforces SemVer compatibility
    - Prefers newer compatible versions
    - Flags major mismatches
    - Allows local override
- Registry maintains a `resolved_versions.json` file for reproducibility

---

## UUID Graph Model

- Each component has a UUID
- `parent_id` and `child_ids` form a DAG
- Enables:
  - Lineage queries
  - Inheritance resolution
  - Impact analysis

---

## Registry Backend

Authoritative store: **PostgreSQL**
- JSON/JSONB columns for metadata
- Fast indexed lookups by UUID, tag, type, etc.
- Transactional integrity

Cache layer: **Write-through file-based**
- Used for CLI and local workflows
- Periodic sync
- Optional read-only offline mode

---

## CLI Examples

    omnibase list validators --tag canary
    omnibase run tool fix_format_headers --input example.py
    omnibase inspect metadata 123e4567-e89b-12d3-a456-426614174000
    omnibase validate metadata my_validator.yaml
    omnibase visualize dependencies fix_format_headers
    omnibase compose pipeline --from fix_format_headers --to check_header_spacing
    omnibase list --type tool --tags canary
    omnibase search --filter 'name=fix_header,type=tool'
    omnibase resolve validator:abc123
    omnibase inspect uuid-of-component

---

## Registry Policy

- Components must have a valid, parseable metadata block
- All entries must include:
  - UUID
  - Version (SemVer)
  - Tags
  - Lifecycle
  - Idempotency flag
- All registry reads/writes validated against schema
- CI blocks unversioned or malformed entries

---

## Federation Strategy (Planned)

- Future registries can sync with one another
- Priority order controlled by trust/config
- Conflicts resolved using `source_precedence`
- Components may be promoted/demoted based on validation success

---

## Planned Enhancements
- [ ] Implement versioned PostgreSQL registry schema
- [ ] Implement CLI-backed file cache
- [ ] Add schema validators for metadata structure
- [ ] Create visualization tools for UUID graph traversal
- [ ] GraphQL adapter for registry access
- [ ] Federation metadata schema (`registry_remote.yaml`)
- [ ] Trust scoring for source registries
- [ ] Differential sync for CI pipelines

---

> Registry state is the source of truth for all validation, execution, and orchestration decisions. 

# ONEX v0.1 Canonical Registry and Federation Model

> **This section is canonical and supersedes any conflicting details below.**

## Registry Mission
The ONEX registry is the canonical, signed, and federated source of truth for all nodes, agents, tools, transformers, and plans. It supports multi-org federation, trust negotiation, and policy enforcement.

## Registry Entry Model
- All entries are signed, hash-addressed, and time-stamped.
- Required fields: object_type, payload, fingerprint (SHA-256), trust_level (UNVERIFIED/SIGNED/VERIFIED), attestation, registered_at, doc_url, schema_url.
- Namespace format: org.project.domain.transformer

## Federation and Trust
- Federation via manifest sync and trust anchor rotation.
- Trust anchors are signed by org or federation root.
- Conflict resolution via trust_policy: local_prefer | remote_prefer | quarantine.
- Fallback to local transformer on latency failure, signature mismatch, or quorum disagreement.

## Attestation and Execution Trust Chain
- Registry entries must support attestation and execution trust chain: agent keypair, node identity, signed registry entry, session grant, execution attestation.

## CI and Result Reporting
- Registry must support CI integration, result reporting, and conformance suite:
  - Schema validation, retry/fallback conformance, budget exhaustion tracing, policy injection enforcement, federation failover simulation, chaos test validation.
- Emit logs for execution_start, execution_end, retry, fallback, error, budget_exceeded, deprecation_warning, policy_violation, resource_usage.

## Deprecation and Sunset Policy
- Deprecated entries must emit warnings and provide replacement references.

# ONEX v0.1 Canonical Registry Migration and Bootstrap Policy

> **This section is canonical and supersedes any conflicting details below.**

## Migration Workflow
- Parse legacy entries with `onex registry import legacy_fixtures.yaml --type fixture`
- Apply normalization rules: auto-inject required fields, infer missing schema URLs
- Validate runtime import: decorator presence, bootstrap() for plugins, entrypoint load
- Stage in registry draft index with `onex registry stage --from legacy_normalized.yaml`

## Bootstrap Convention
- All plugin, tool, or injectable modules MUST expose:
```python
def bootstrap(registry):
    registry.register("scaffold", MyTool())
```
- Enables runtime DI population and introspection via CLI

## Required Decorators (Enforced)
| Object Type | Required Decorator        |
| ----------- | ------------------------- |
| tool        | `@tool`                   |
| validator   | `@validator`              |
| fixture     | `@fixture`                |
| plugin      | `@plugin` + `bootstrap()` |

## CI Validation Steps
- Lint for `bootstrap()` if plugin
- Enforce decorator presence on import
- Hash metadata and compare to registry entry
- Fail if entrypoint missing/malformed, decorator not present, YAML/NDJSON missing required fields

## CLI Integration
- `onex migrate legacy.yaml --fix`
- `onex lint --registry plugin.*`
- `onex validate --entrypoint fixtures/*.py`
- `onex sync --verify-hashes`

**Status:** Formalized migration and enforcement model for cleaning up legacy registries and validating runtime discoverability through decorator and `bootstrap()` compliance. 

# ONEX v0.1 Canonical Plugin Registry and Dependency Injection

> **This section is canonical and supersedes any conflicting details below.**

## Plugin Object Format
- Each plugin is a registry entry with `object_type: plugin`.
- Required fields: module, class_name, provides, entrypoint, compatible_with, default_scope.

## Plugin DI Registration
- All plugins must implement a `bootstrap()` or `register()` function to expose methods, register hooks, and validate compatibility.
- Example:
```python
def bootstrap(registry):
    registry.register("scaffold", AutogenScaffolder())
```

## Runtime Hooks
- Plugins may define hooks (e.g., on_create, on_validate) to trigger at key lifecycle events.

## Plugin Metadata Fields
- provides, default_scope, supports_roles, requires_gpu, compatible_types, etc.

## CLI Integration
- `onex scaffold --plugin ...`, `onex validate --wrap ... --with plugin...`

## Discovery
- Plugins are registered like any other node, discoverable by namespace/type/metadata scan.
- Example: `onex registry list --type plugin --provides scaffold`

**Status:** Canonical plugin and DI architecture for ONEX nodes and CLI tooling, based on dynamic hook-based registration, scoped DI injection, and CLI-aware plugin orchestration. 

# ONEX v0.1 Canonical Registry Architecture

> **This section is canonical and supersedes any conflicting details below.**

## Registry Object Types
- transformer, schema, agent, test, tool, fixture, plugin, plan, policy
- All share a common wrapper format, differentiated by schema/metadata fields

## Core Fields (Shared)
- id, version, namespace, object_type, registered_at, fingerprint, trust_level, schema_url, entrypoint, source_url, status

## Registry Categories
- Tools, Validators, Fixtures, Plugins, Agents (each with specific metadata fields)

## Trust and Status Fields
- trust: level, signed_by, signature, federation_scope

## Storage and Discovery
- Canonical format: .yaml or .ndjson
- Indexable via GraphQL or JetStream event feeds
- Supports batch export by type, namespace, lifecycle, trust status

## CLI Integration
- `onex registry list --type validator`, `onex registry get ...`, `onex registry sync --to remote`, `onex publish ... --status frozen`

**Status:** Canonical registry layout for ONEX project-wide components, migrated from fixture/tool/plugin/validator split registries into unified, polymorphic structure. 

# ONEX v0.1 Canonical Result Reporting and CI Integration

> **This section is canonical and supersedes any conflicting details below.**

## Result Model Schema
- NodeExecutionResult: node_id, input_hash, output_hash, success, execution_time_ms, metadata, errors, warnings, status
- BatchExecutionResult: batch_id, status, results, started_at, completed_at, coverage_percent, trust_delta, trust_notes

## Output Format
- Recommended: .json or .ndjson
- Supports filters: --only-failed, --only-regression, --include-coverage
- Optional YAML snapshot for GitOps/registry commits

## Trust + CI Metadata
- ci_run: triggered_by, policy, node_count, trust_enforced, minimum_coverage_required, runtime_flags, failed_nodes

## Example Output

ONEX/OmniBase supports both YAML and JSON formats for `execution_result` files, enabling interoperability and user flexibility.

- **YAML Format:**
  - Extension: `.yaml`
  - Example:
    ```yaml
    batch_id: validator_patch_v3
    status: partial
    results:
      - node_id: validator.check.format
        success: true
        execution_time_ms: 101
        status: success
      - node_id: validator.check.deprecated
        success: false
        execution_time_ms: 102
        status: failure
        errors:
          - Unexpected global import
    trust_delta: -0.02
    started_at: 2025-05-14T08:01:12Z
    completed_at: 2025-05-14T08:01:23Z
    ```

- **JSON Format:**
  - Extension: `.json`
  - Example:
    ```json
    {
      "batch_id": "validator_patch_v3",
      "status": "partial",
      "results": [
        {
          "node_id": "validator.check.format",
          "success": true,
          "execution_time_ms": 101,
          "status": "success"
        },
        {
          "node_id": "validator.check.deprecated",
          "success": false,
          "execution_time_ms": 102,
          "status": "failure",
          "errors": ["Unexpected global import"]
        }
      ],
      "trust_delta": -0.02,
      "started_at": "2025-05-14T08:01:12Z",
      "completed_at": "2025-05-14T08:01:23Z"
    }
    ```

- **Schema Validation:**
  - Both formats are validated against the canonical schemas:
    - YAML: `src/omnibase/schemas/execution_result.yaml`
    - JSON: `src/omnibase/schemas/execution_result.json`
  - Example files:
    - YAML: `tests/schema/testdata/valid_execution_result.yaml`
    - JSON: `tests/schema/testdata/valid_execution_result.json`

## CLI Integration
- `onex run --output batch_result.json`, `onex validate --export=ci_output.ndjson`, `onex report --summary --only-failed`, `onex badge generate --trust-level`

**Status:** Consolidated from legacy CI/test result model and refactored for structured, trust-aware reporting in ONEX batch and CI flows. 

# ONEX v0.1 Canonical Lifecycle and Batch Model

> **This section is canonical and supersedes any conflicting details below.**

## Node Lifecycle State
- `lifecycle_status`: active | frozen | legacy | pending | batch-complete
  - active: default, executable, mutable
  - frozen: metadata/schema locked
  - legacy: usable, not under active development
  - pending: under validation or trust elevation
  - batch-complete: finalized as part of orchestrated unit
- Enforced during validation, publishing, CI/CD export

## Node Enforcement via Lifecycle Enforcer
- Checks for missing/invalid `lifecycle_status`
- Prevents updates to `frozen` entries unless overridden
- Requires all batch entries to agree on lifecycle tag
- Warns on execution of `legacy`/`pending` nodes in critical paths

## Batch Coordination
- `BatchPlan`: batch_id, description, node_ids, dependency_graph (optional), required_status
- Used for release gating, CI planning, registry grouping, audit trails

## Versioning + Freeze Contracts
- Nodes in a `frozen` batch must declare a version, pass conformance, and have signature/trust metadata

## Enforcer Result Schema (Example)
```json
{
  "batch_id": "validator-core-v1",
  "status": "failure",
  "errors": [
    {
      "node_id": "tool.validator.autofix",
      "reason": "Expected status: frozen; found: active"
    }
  ],
  "passed": ["test.tree.sanity"]
}
```

## CLI Integration (Planned)
- `onex validate --enforce-lifecycle`
- `onex batch freeze batch-id.yaml`
- `onex publish --only-frozen`
- `onex report --include-lifecycle`

**Status:** Derived from legacy orchestrator lifecycle manager design. Recast as a core enforcement layer within the ONEX graph system. 

# ONEX v0.1 Canonical Directory Tree Validation

> **ONEX v0.1 Canonical Section**
> This section is canonical and supersedes any conflicting details below.

## ONEX Directory Tree Validation (v0.1)

### Overview

ONEX supports enforcement of canonical directory structures through a `.tree` + `.treerules` system. This allows for programmatic discovery, policy enforcement, and CI-level validation of file layout, naming patterns, and required content.

---

### 📁 `.tree` File: Canonical Structure

* Captures the directory/file hierarchy as a nested YAML tree
* Uses the `TreeNode` schema with fields:

  * `name`, `type` (file|directory), `children`
  * Optional: `metadata`, `mtime`, `size`

**Example:**

```yaml
name: root
children:
  - name: src
    type: directory
    children:
      - name: nodes
        type: directory
        children:
          - name: validator.check.namegen
            type: directory
            children:
              - name: metadata.yaml
                type: file
              - name: code.py
                type: file
              - name: test.py
                type: file
```

---

### 📜 `.treerules` File: Enforcement Policy

Defines validation constraints:

* Required files
* Allowed file/directory patterns
* Deny unlisted entries
* Optional: per-node configuration overrides

**Example:**

```yaml
rules:
  - path: src/nodes/**
    allowed_files:
      - "*.py"
      - "metadata.yaml"
    required_files:
      - "metadata.yaml"
      - "code.py"
    allowed_dirs:
      - "mocks"
      - "variants"
    deny_unlisted: true
    allow_flexible: false
```

---

### 🧪 Validation Behavior

* Files are matched against both `.tree` and `.treerules`
* Directories must include required files to pass
* Unlisted entries are rejected if `deny_unlisted: true`
* Known valid exceptions (`__pycache__`, `.git`, etc.) are globally whitelisted in `allow_flexible`

---

### 🔁 CI + Pre-commit Integration

* Pre-commit hook auto-runs tree validator on modified files
* CI validates full directory structure across all nodes

---

### 🔎 CLI Usage

```bash
onex validate-tree --root ./src/nodes --template .treerules
onex validate-tree --strict
onex validate-tree --format=json --output=report.json
```

---

### 🛠 Future Enhancements (Planned)

* `.treeignore` + override support
* Branch diff + tree merge tooling
* Remote API validation service
* Visualization via Graphviz or web interface
* Profile-based rulesets: `ci`, `dev`, `prod`

---

**Status:** This is the canonical system for directory shape enforcement in ONEX. All new nodes, scaffolds, and repositories must support `.tree` + `.treerules` as part of their CI pipeline.

---

## Dual-Format Support for .tree Files (YAML and JSON)

ONEX/OmniBase supports both YAML and JSON formats for `.tree` files, enabling maximum interoperability and user flexibility.

- **YAML Format:**
  - Extension: `.tree`
  - Example:
    ```yaml
    name: root
    type: directory
    children:
      - name: src
        type: directory
        children:
          - name: nodes
            type: directory
            children:
              - name: validator.check.namegen
                type: directory
                children:
                  - name: metadata.yaml
                    type: file
                  - name: code.py
                    type: file
                  - name: test.py
                    type: file
    ```

- **JSON Format:**
  - Extension: `.tree.json`
  - Example:
    ```json
    {
      "name": "root",
      "type": "directory",
      "children": [
        {
          "name": "src",
          "type": "directory",
          "children": [
            {
              "name": "nodes",
              "type": "directory",
              "children": [
                {
                  "name": "validator.check.namegen",
                  "type": "directory",
                  "children": [
                    { "name": "metadata.yaml", "type": "file" },
                    { "name": "code.py", "type": "file" },
                    { "name": "test.py", "type": "file" }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
    ```

- **Schema Validation:**
  - Both formats are validated against the same canonical schema, available as:
    - `src/omnibase/schemas/tree_format.yaml`
    - `src/omnibase/schemas/tree_format.json`
  - Example files:
    - YAML: `tests/validate/directory_tree/test_case/valid/valid_basic.tree`
    - JSON: `tests/validate/directory_tree/test_case/valid/valid_basic.tree.json`

- **Best Practices:**
  - Use `.tree` for YAML and `.tree.json` for JSON.
  - All tools, validators, and CI jobs must support both formats.
  - See `tests/tools/test_tree_discovery.py` for comprehensive test coverage of both formats.

---

> **Note:** All ONEX v0.1 sections below are canonical. Any previous or conflicting details are explicitly superseded.

# ONEX v0.1 Canonical Prompt Registry Specification

> **ONEX v0.1 Canonical Section**
> This section is canonical and supersedes any conflicting details below.

## ONEX Prompt Registry Specification (v0.1)

### Overview

This document defines the structure, versioning, and operational behavior of the ONEX Prompt Registry. The registry enables safe, testable, and rollback-capable prompt management for agents and tools in ONEX environments.

---

### 🎯 Purpose

* Manage prompt versions at the step level
* Enable rollback to trusted prior prompts
* Track prompt usage, hashes, and schema links
* Support auditing and automated safety checks

---

### 🧱 Prompt Registry Entry Format

```json
{
  "step": "coder",
  "version": "1.0.2",
  "hash": "sha256:abc123...",
  "prompt": "Write a Python function that...",
  "schema": "AgentCoderPromptSchema_v1",
  "created_at": "2025-05-01T10:00:00Z",
  "created_by": "prompt_autogen_tool",
  "trust_level": "verified",
  "tags": ["codegen", "backend", "fast"]
}
```

---

### 📦 Prompt Metadata Fields

| Field         | Description                            |
| ------------- | -------------------------------------- |
| `step`        | Agent step or role using the prompt    |
| `version`     | Manually or auto-incremented version   |
| `hash`        | SHA-256 of prompt string               |
| `schema`      | Linked input/output schema ID          |
| `created_by`  | Node/tool that generated this version  |
| `trust_level` | UNVERIFIED / SIGNED / VERIFIED         |
| `tags`        | Optional classifier tags for filtering |

---

### 🔁 Versioning and Rollback

* Prompts must be stored with immutable version hashes
* CLI supports rollback or restore:

```bash
onex prompt rollback --step coder --to 1.0.1
```

* Registry enforces no overwrites of prior versions
* Trust level required for promotion (e.g., to use in production)

---

### ⚠️ Prompt Injection Safety

* Only allow templated variables (e.g., `{{file_name}}`, `{{task}}`)
* Reject prompts with unscoped raw user content
* Validate prompt format against known schema

---

### 🔍 CLI Integration

* `onex prompt get --step coder`
* `onex prompt list --step coder`
* `onex prompt push --step coder --file new_prompt.txt`
* `onex prompt validate --step coder`

---

### 🧪 CI and Agent Integration

* Registry entries must match prompt hash used at runtime
* CI test must validate prompt schema compatibility
* Agents must log prompt hash and version on execution
* Enable replay of prior runs based on prompt + memory snapshot

---

**Status:** This is the canonical standard for all prompt definitions in ONEX. Prompts must be stored, versioned, validated, and optionally signed to be used in trusted execution environments.

---

> **Note:** All ONEX v0.1 sections below are canonical. Any previous or conflicting details are explicitly superseded.

# Schema Registry Versioning: Essentials

> **ONEX v0.1 Canonical Section**
> This section is canonical and supersedes any conflicting details below.

This section summarizes the critical requirements for versioning schemas in OmniNode's registry system. These principles ensure robust validation, compatibility, and agent interoperability.

---

## Core Requirements

### 📦 Schema Versioning & Storage

- Each schema (e.g., `UserMessage`) must support **multiple versions** (v1, v2, ...)
- Schemas are retrievable by `(name, version)`
- Each version includes:
  - Version number
  - Creation date
  - Change description (optional)

### ✅ Validation Behavior

- Incoming messages must specify a **`version` field**
- The registry selects and applies the appropriate schema version
- Support optional fallback or upgrade path

```python
schema = schema_registry.get("UserMessage", version="2")
schema.validate(incoming_message)
```

### 🔄 Evolution Rules

- Support **deprecation** of old versions
- Define rules for breaking vs backward-compatible changes
- Optional: diff tooling for schema evolution

### 🔍 Debugging & Observability

- Log schema version during validation
- Optional metrics:
  - Message volume by version
  - Validation failure rates per version

### 🧪 Testing Requirements

- Tests must validate:
  - Each schema version
  - Version mismatch handling
  - Cross-version compatibility

---

## Optional Enhancements (Planned)

- Developer codemods to auto-upgrade messages
- Schema changelog viewer
- Snapshot archive of registry states
- Version negotiation for agent-to-agent messaging

---

This versioning model underpins all schema-based validation in OmniNode and ensures long-term compatibility across nodes, agents, and tools.

## State Contract Schema: Dual-Format Support

ONEX/OmniBase supports both YAML and JSON formats for `state_contract` files, enabling interoperability and user flexibility.

- **YAML Format:**
  - Extension: `.yaml`
  - Example:
    ```yaml
    state:
      foo: bar
      count: 1
    ```

- **JSON Format:**
  - Extension: `.json`
  - Example:
    ```json
    {
      "state": {
        "foo": "bar",
        "count": 1
      }
    }
    ```

- **Schema Validation:**
  - Both formats are validated against the canonical schemas:
    - YAML: `src/omnibase/schemas/state_contract.yaml`
    - JSON: `src/omnibase/schemas/state_contract.json`
  - Example files:
    - YAML: `tests/schema/testdata/valid_state_contract.yaml`
    - JSON: `tests/schema/testdata/valid_state_contract.json`

## Schema Documentation Generation

ONEX/OmniBase provides an automated tool to generate Markdown documentation for all canonical schemas. This ensures that documentation is always up to date with the latest schema definitions and versioning.

- **Tool:** `src/omnibase/tools/docstring_generator.py`
- **Output:** Markdown files in `docs/generated/` (one per schema)
- **Template:** `docs/templates/schema_doc.md.j2`

### Usage

To generate documentation for all schemas:

```bash
poetry run python src/omnibase/tools/docstring_generator.py --output-dir docs/generated --verbose
```

This will scan all YAML/JSON schemas in `src/omnibase/schemas/`, extract field-level documentation, examples, and version/changelog info, and render Markdown docs to `docs/generated/`.

### Rationale
- Ensures documentation is always in sync with schemas
- Supports field-level, example-driven, and versioned docs
- Can be run in CI or as a pre-commit hook to prevent drift

See the generated docs in `docs/generated/` for up-to-date schema documentation.