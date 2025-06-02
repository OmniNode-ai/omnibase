<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: registry.md
version: 1.0.0
uuid: 41563e67-748b-4ecf-8b4c-e1506faa725e
author: OmniNode Team
created_at: 2025-05-27T05:41:08.173900
last_modified_at: 2025-05-27T17:26:51.951115
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 35623de8396faf87668e100239f13fe56ae1f2acfeb32e9e1eab06b2f09a8842
entrypoint: python@registry.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.registry
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# OmniBase Registry Specification

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Registry system for tracking all registered components including validators, tools, test cases, artifacts, and pipelines

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

## Protocol-Driven Engine and Test Case Registration

- All protocol-driven engines (e.g., the ONEX Metadata Stamper) must be registered in the protocol registry, enabling dynamic discovery and selection at runtime or via CLI.
- Test cases for protocol-driven tools must also be registered in the test case registry, supporting context-agnostic and fixture-injectable execution.
- Registries must support introspection, filtering, and enumeration of protocol-driven engines and their test cases.
- Example registration pattern:

```python
from omnibase.protocols import ProtocolStamperEngine
from omnibase.registry import ProtocolRegistry

registry = ProtocolRegistry()
registry.register_engine("stamper", RealStamperEngine())
registry.register_engine("stamper_in_memory", InMemoryStamperEngine())
```

- See [Core Protocols](./reference-protocols-core.md), [Registry Protocols](./reference-protocols-registry.md), and [docs/testing.md](./testing.md) for canonical registry and fixture-injection patterns.

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

```yaml
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
```

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

```bash
onex list-nodes --tag canary
onex run stamper_node --args='["file", "example.py"]'
onex node-info 123e4567-e89b-12d3-a456-426614174000
onex validate metadata my_validator.yaml
onex run tree_generator_node --args='["--visualize-dependencies", "stamper_node"]'
onex list-nodes --type tool --tags canary
onex run registry_loader_node --args='["--search", "name=stamper,type=tool"]'
onex run parity_validator_node --args='["--nodes-directory", "validator:abc123"]'
onex node-info uuid-of-component
```

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

## ONEX Registry and Federation Model

### Registry Mission
The ONEX registry is the canonical, signed, and federated source of truth for all nodes, agents, tools, transformers, and plans. It supports multi-org federation, trust negotiation, and policy enforcement.

### Registry Entry Model
- All entries are signed, hash-addressed, and time-stamped.
- Required fields: object_type, payload, fingerprint (SHA-256), trust_level (UNVERIFIED/SIGNED/VERIFIED), attestation, registered_at, doc_url, schema_url.
- Namespace format: org.project.domain.transformer

### Federation and Trust
- Federation via manifest sync and trust anchor rotation.
- Trust anchors are signed by org or federation root.
- Conflict resolution via trust_policy: local_prefer | remote_prefer | quarantine.
- Fallback to local transformer on latency failure, signature mismatch, or quorum disagreement.

### Attestation and Execution Trust Chain
- Registry entries must support attestation and execution trust chain: agent keypair, node identity, signed registry entry, session grant, execution attestation.

### CI and Result Reporting
- Registry must support CI integration, result reporting, and conformance suite:
  - Schema validation, retry/fallback conformance, budget exhaustion tracing, policy injection enforcement, federation failover simulation, chaos test validation.
- Emit logs for execution_start, execution_end, retry, fallback, error, budget_exceeded, deprecation_warning, policy_violation, resource_usage.

### Deprecation and Sunset Policy
- Deprecated entries must emit warnings and provide replacement references.

---

## Registry Migration and Bootstrap Policy

### Migration Workflow
- Apply normalization rules: auto-inject required fields, infer missing schema URLs
- Validate runtime import: decorator presence, bootstrap() for plugins, entrypoint load

### Bootstrap Convention
- All plugin, tool, or injectable modules MUST expose:
```python
def bootstrap(registry):
    registry.register("scaffold", MyTool())
```
- Enables runtime DI population and introspection via CLI

### Required Decorators (Enforced)
| Object Type | Required Decorator        |
| ----------- | ------------------------- |
| tool        | `@tool`                   |
| validator   | `@validator`              |
| fixture     | `@fixture`                |
| plugin      | `@plugin` + `bootstrap()` |

### CI Validation Steps
- Lint for `bootstrap()` if plugin
- Enforce decorator presence on import
- Hash metadata and compare to registry entry
- Fail if entrypoint missing/malformed, decorator not present, YAML/NDJSON missing required fields

### CLI Integration
- `onex lint --registry plugin.*`
- `onex validate --entrypoint fixtures/*.py`
- `onex sync --verify-hashes`

---

## Plugin Registry and Dependency Injection

### Plugin Object Format
- Each plugin is a registry entry with `object_type: plugin`.
- Required fields: module, class_name, provides, entrypoint, compatible_with, default_scope.

### Plugin DI Registration
- All plugins must implement a `bootstrap()` or `register()` function to expose methods, register hooks, and validate compatibility.
- Example:
```python
def bootstrap(registry):
    registry.register("scaffold", AutogenScaffolder())
```

### Runtime Hooks
- Plugins may define hooks (e.g., on_create, on_validate) to trigger at key lifecycle events.

### Plugin Metadata Fields
- provides, default_scope, supports_roles, requires_gpu, compatible_types, etc.

### CLI Integration
- `onex scaffold --plugin ...`, `onex validate --wrap ... --with plugin...`

### Discovery
- Plugins are registered like any other node, discoverable by namespace/type/metadata scan.
- Example: `onex list-nodes --type plugin --provides scaffold`

---

## Registry Architecture

### Registry Object Types
- transformer, schema, agent, test, tool, fixture, plugin, plan, policy
- All share a common wrapper format, differentiated by schema/metadata fields

### Core Fields (Shared)
- id, version, namespace, object_type, registered_at, fingerprint, trust_level, schema_url, entrypoint, source_url, status

### Registry Categories
- Tools, Validators, Fixtures, Plugins, Agents (each with specific metadata fields)

### Trust and Status Fields
- trust: level, signed_by, signature, federation_scope

### Storage and Discovery
- Canonical format: .yaml or .ndjson
- Indexable via GraphQL or JetStream event feeds
- Supports batch export by type, namespace, lifecycle, trust status

### CLI Integration
- `onex list-nodes --type validator`, `onex node-info ...`, `onex sync --to remote`, `onex publish ... --status frozen`

---

## Result Reporting and CI Integration

### Result Model Schema
- NodeExecutionResult: node_id, input_hash, output_hash, success, execution_time_ms, metadata, errors, warnings, status
- BatchExecutionResult: batch_id, status, results, started_at, completed_at, coverage_percent, trust_delta, trust_notes

### Output Format
- Recommended: .json or .ndjson
- Supports filters: --only-failed, --only-regression, --include-coverage
- Optional YAML snapshot for GitOps/registry commits

### Trust + CI Metadata
- ci_run: triggered_by, policy, node_count, trust_enforced, minimum_coverage_required, runtime_flags, failed_nodes

### Example Output

ONEX/OmniBase supports both YAML and JSON formats for `execution_result` files, enabling interoperability and user flexibility.

#### YAML Format:
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

#### JSON Format:
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

### Schema Validation
Both formats are validated against the canonical schemas:
    - YAML: `src/omnibase/schemas/execution_result.yaml`
    - JSON: `src/omnibase/schemas/execution_result.json`

---

> Registry state is the source of truth for all validation, execution, and orchestration decisions.
