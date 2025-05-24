<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: registry_architecture.md
version: 1.1.0
uuid: 52124f63-ab43-42d4-9182-3fd1addc03e1
author: OmniNode Team
created_at: 2025-05-23T12:17:33.838696
last_modified_at: 2025-05-23T17:42:52.030028
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: b1393b3d2faac76c69b248cc1d86dfa71c09d809c218be547c2997e39c796364
entrypoint: python@registry_architecture.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.registry_architecture
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node & CLI Adapter Registry Architecture

<!--- TODO: Table of Contents (auto-generated or manual) --->

## Purpose
This document specifies the ONEX/OmniBase Node and CLI Adapter Registry Architecture. It incorporates recent enhancements such as versioned node support, registry namespacing, adapter protocol definitions, hot reloading use cases, structured error handling, and a comprehensive milestone roadmap. It serves as a living reference for core and plugin contributors.

**Note:** The ONEX registry now uses `.onextree` as the canonical, declarative manifest describing the expected structure of ONEX project directories and artifact packages. `.onextree` is used for programmatic validation, discovery, and enforcement of standards. See [onextree_format.md](../../docs/generated/tree_format.md) for schema, fields, and canonical examples.

---

## Registry Loader Implementation

### OnexRegistryLoader Overview

The `OnexRegistryLoader` class implements the `ProtocolRegistry` interface and provides the core registry functionality for ONEX. It follows these key principles:

1. **Registry-First Discovery**: All artifacts are discovered through `registry.yaml` files
2. **Metadata Validation**: Each artifact version must have valid metadata or a `.wip` marker
3. **`.onextree` Integration**: Registry contents are validated against the `.onextree` manifest
4. **Structured Error Handling**: All operations return structured results with clear status and error messages

### Registry.yaml Structure

The registry loader reads from `src/omnibase/registry/registry.yaml` which defines all available artifacts:

```yaml
nodes:
  - name: "stamper_node"
    versions:
      - version: "1.0.0"
        path: "src/omnibase/nodes/stamper_node/v1_0_0"
        metadata_file: "node.onex.yaml"
        status: "active"
  - name: "tree_generator_node"
    versions:
      - version: "1.0.0"
        path: "src/omnibase/nodes/tree_generator_node/v1_0_0"
        metadata_file: "node.onex.yaml"
        status: "active"

cli_tools:
  - name: "onex"
    versions:
      - version: "1.0.0"
        path: "src/omnibase/cli_tools/onex/v1_0_0"
        metadata_file: "cli_tool.yaml"
        status: "active"

runtimes:
  - name: "onex_runtime"
    versions:
      - version: "1.0.0"
        path: "src/omnibase/runtimes/onex_runtime/v1_0_0"
        metadata_file: "runtime.yaml"
        status: "active"

adapters:
  - name: "cli_adapter"
    versions:
      - version: "1.0.0"
        path: "src/omnibase/adapters/cli_adapter/v1_0_0"
        metadata_file: "cli_adapter.yaml"
        status: "active"

contracts:
  - name: "default_contract"
    versions:
      - version: "1.0.0"
        path: "src/omnibase/contracts/default_contract/v1_0_0"
        metadata_file: "contract.yaml"
        status: "active"

packages:
  - name: "core_package"
    versions:
      - version: "1.0.0"
        path: "src/omnibase/packages/core_package/v1_0_0"
        metadata_file: "package.yaml"
        status: "active"
```

### Artifact Validation Rules

The registry loader validates each artifact version according to these rules:

1. **WIP Marker Priority**: If a `.wip` file exists in the version directory, the artifact is marked as WIP and no further validation is performed
2. **Metadata File Requirement**: If no `.wip` marker exists, the specified metadata file (e.g., `node.onex.yaml`) must be present
3. **Metadata Structure Validation**: The metadata file must be valid YAML and contain required fields:
   - `name`: Artifact name
   - `version`: Version string
   - `schema_version`: Schema version for compatibility
4. **Path Validation**: The artifact path must exist and be accessible

### .wip Marker Convention

The `.wip` (Work In Progress) marker is a simple file that indicates an artifact version is under development:

- **File**: `.wip` (empty file in the version directory)
- **Purpose**: Allows incomplete artifacts to be tracked in the registry without requiring complete metadata
- **Behavior**: Registry loader marks these artifacts as WIP and skips metadata validation
- **Usage**: Useful during development when metadata is not yet finalized

Example:
```
src/omnibase/nodes/new_node/v1_0_0/
├── .wip                    # Marks this version as WIP
├── node.py                 # Implementation (may be incomplete)
└── (node.onex.yaml missing) # Metadata not required due to .wip marker
```

### .onextree Integration

The registry loader validates that all registered artifacts are properly represented in the `.onextree` manifest:

1. **Synchronization Check**: All artifact paths in `registry.yaml` must exist in `.onextree`
2. **Metadata File Tracking**: All metadata files must be tracked in `.onextree`
3. **Drift Detection**: The loader can detect when registry and `.onextree` are out of sync
4. **Validation API**: `validate_against_onextree()` method provides detailed validation results

### Registry Loading Process

The registry loading process follows these steps:

1. **Registry File Discovery**: Load `registry.yaml` from the configured path
2. **Artifact Enumeration**: Process all artifact types (nodes, cli_tools, runtimes, adapters, contracts, packages)
3. **Version Validation**: For each version, check for `.wip` marker or validate metadata file
4. **Metadata Loading**: Load and parse metadata files for valid artifacts
5. **Statistics Collection**: Track total, valid, invalid, and WIP artifact counts
6. **Result Generation**: Return structured `RegistryLoadResult` with status and details

### Error Handling and Diagnostics

The registry loader provides comprehensive error handling:

- **Structured Results**: All operations return `RegistryLoadResult` with clear status
- **Detailed Logging**: Warnings and errors are logged with specific artifact details
- **Validation Reasons**: Failed validations include specific reason messages
- **Statistics Tracking**: Counts of valid, invalid, and WIP artifacts for monitoring

### Registry API Methods

The `OnexRegistryLoader` implements these key methods:

```python
# Core loading methods
@classmethod
def load_from_disk(cls) -> "ProtocolRegistry"
@classmethod  
def load_mock(cls) -> "ProtocolRegistry"

# Artifact discovery methods
def get_node(self, node_id: str) -> Dict[str, Any]
def get_artifacts_by_type(self, artifact_type: str) -> List[ArtifactVersion]
def get_artifact_by_name_and_version(self, name: str, version: str, artifact_type: Optional[str] = None) -> Optional[ArtifactVersion]
def get_all_artifacts(self) -> Dict[str, List[ArtifactVersion]]
def get_wip_artifacts(self) -> List[ArtifactVersion]

# Validation and diagnostics
def validate_against_onextree(self, onextree_path: Optional[Path] = None) -> Dict[str, Any]
def get_registry_stats(self) -> Dict[str, Any]

# Plugin discovery (stub)
def discover_plugins(self) -> List[Any]
```

---

## Out of Scope
This document does **not** cover:
- Specific implementation details (e.g., choice of Python framework for adapters)
- Deployment strategies of ONEX itself
- Detailed security hardening of the underlying OS or network
- User authentication/authorization for CLI commands (though the registry might inform permissions)
- Runtime execution of nodes (the registry only provides discovery and metadata)

---

## Core Goals & Requirements
We aim for a robust, extensible, and maintainable registry system that addresses the following key requirements:

* **Third-party Plugin Support:** The system must allow external nodes and adapters while enforcing ONEX's registration and metadata standards.
* **Adapter Sharing:** Adapters can be node-specific or shared; the registry must support flexible references.
* **Performance:**
  * Initial startup discovery: under 30 seconds (acceptable due to comprehensive plugin scanning).
  * Runtime node/adapter lookup: typically under 100ms (critical for responsive CLI).
* **Correctness:** Ensuring consistent and predictable discovery, loading, and resolution of nodes and adapters, with clear conflict resolution rules and robust error handling.
* **Auditability/Traceability:** The system must provide clear logs and mechanisms to trace which registry provided a node, its version, and any resolution decisions.
* **Hot Reloading/Dynamic Registration:** We require an API for hot reloading, though its full implementation can be deferred initially.
* **Registry Namespacing:** The registry must support namespacing (e.g., per environment, tenant, or feature) to isolate environments and prevent conflicts.
* **Versioned Node Support:** Multiple node versions must coexist, with canonical lookup and resolution mechanisms.
* **Metadata Enforcement:** All nodes and adapters must provide canonical metadata (YAML/JSON) and conform to protocol standards.
* **Structured Error Handling:** Registry operations must raise typed exceptions or return structured error results for reliable debugging and consistent behavior.

---

## Architectural Overview
The registry architecture is built around a set of core principles and components designed for flexibility, standardization, and extensibility.

### 1. Protocol-Driven Registries
All registries, whether core, plugin, or per-node, must adhere to a canonical protocol. This ensures consistency and interoperability across the system. **ProtocolNodeCliAdapter** is a Python Protocol (from `typing`), supporting structural subtyping and flexible plugin integration.

```python
# NodeMetadataBlock (Conceptual Pydantic model)
class NodeMetadataBlock:
    node_id: str
    name: str
    version: str
    category: str
    description: str
    cli_adapter_ref: dict  # {'module': str, 'class': str}
    tags: list[str]
    deprecated: bool
    git_commit: Optional[str]

# ProtocolNodeCliAdapter (Python Protocol/Interface)
class ProtocolNodeCliAdapter(Protocol):
    def run(self, args: list[str]) -> None:
        """Main entry point for CLI invocation."""
    def get_parser(self) -> Any:
        """Returns the CLI argument parser."""
```

Registry methods following this protocol include:
* `get_node(node_id: str, version: Optional[str] = None, namespace: Optional[str] = None) -> NodeMetadataBlock`
* `list_nodes(namespace: Optional[str] = None) -> list[NodeMetadataBlock]`
* `get_adapter(node_id: str, version: Optional[str] = None, namespace: Optional[str] = None) -> ProtocolNodeCliAdapter`
* `reload() -> None`

#### Registry Namespacing
We support **namespacing** to isolate different environments (e.g., `dev/my_node_id`, `prod/my_node_id`), multi-tenant setups, or feature-flagged deployments. Nodes are registered under a specific namespace, and lookups include this namespace context. This prevents accidental cross-environment interference and name collisions.

### 2. Chainable Registry Manager
The `ChainedNodeRegistry` is a central component that composes multiple registries (core, plugin, local, etc.). When a lookup occurs, it queries each registry in a defined order until a match is found. This design allows for seamless coexistence and composition of various registry types.

For **conflict resolution** (when the same `node_id` exists in multiple registries), we prioritize based on a defined order and may use a "registry precedence score" (e.g., integer value in plugin metadata):
1.    **Explicitly pinned version**
2.    **Internal core registry**
3.    **Plugin registries** (by load order, declared weight, or precedence score)
4.    **Local/per-node registries**
We will consider emitting a warning or audit log entry when precedence is applied.

### 3. Plugin & Entry Point Discovery
At startup, the system will discover all installed packages that expose a `node_registry` entry point (e.g., via setuptools or Poetry plugins). Each discovered plugin must provide a registry instance conforming to the defined protocol. We will also support fallback discovery from a user-defined configuration file for non-standard plugin setups or restricted environments. The CLI runner will be responsible for loading all discovered registries and chaining them together.

### 4. Metadata-Driven Registration & Validation
Each node and adapter must provide a canonical metadata file (e.g., `node.onex.yaml`). The registry will enforce conformance to specified standards (e.g., naming conventions, required fields). This enforcement will be backed by a formal JSON Schema (or similar schema definition language) to provide programmatic validation. In development mode, we may consider auto-generating metadata stubs for missing fields with warnings, rather than hard failures. In production or strict mode, non-conforming plugins will be ignored by default, with an option to treat violations as errors.

**Note:** In ONEX, the presence of a `.yaml` file (e.g., `node.onex.yaml`, `cli_adapter.yaml`) in a versioned directory is the canonical metadata for that artifact version. The `metadata` field in `.onextree` is rarely used except for special cases (see [onextree_format.md](../../docs/generated/tree_format.md)).

```yaml
# Example node.onex.yaml structure
node_id: "example.data.processor"
name: "Example Data Processor Node"
version: "1.0.0"
category: "data-processing"
description: "A node to process raw data into a canonical format."
cli_adapter:
  module: "onex_plugins.data_processor.cli_adapter"
  class: "DataProcessorCliAdapter"
tags: ["beta", "utility"]
deprecated: false
git_commit: "a1b2c3d4e5f67890abcdef1234567890"
```

#### Versioned Node Support
We support **versioned nodes** to allow multiple versions of a node to coexist. Each node version must reside in its own directory, following a canonical path structure such as `nodes/<category>/<subdomain>/<name>/vX_Y_Z/`. The registry will resolve nodes using symbolic IDs and version tuples. Node metadata defines a `version` and optionally a `full_id` (e.g., `stampers.meta.default@1.0.0`).

**WIP Marker:** To indicate a work-in-progress version directory, place a `.wip` file in the version directory. The registry will ignore such directories unless explicitly configured otherwise.

The registry will support various policies for resolving versions, including: `latest`, `highest_trust`, `exact`, and `pinned`. Old versions will not be automatically deleted; deprecation will be marked in metadata (e.g., `deprecated: true`) and optionally moved to an `archive/` directory. The registry must support symbolic-to-version aliasing and emit a resolution trace when ambiguity exists.

### 5. Adapter Lookup & Protocol
Each node's metadata includes a reference to its CLI adapter (specifying the module and class). The registry is responsible for resolving and lazy-loading the adapter as needed for performance. Shared adapters are pure code entities referenced by node metadata and do not require their own metadata blocks. The interface details for `ProtocolNodeCliAdapter` are defined in section 1.

### 6. Hot Reloading & Dynamic Registration
We will provide an API method for reloading registries at runtime (e.g., `reload()`). While the full implementation can be a stub initially, the API will be in place for future development.

**Use Cases** for hot reloading include:
* Rapid development cycles (allowing local changes without service restarts)
* A/B testing node versions in live environments
* Dynamic updates for long-running services without downtime
* Quick security patches for specific nodes

### 7. Structured Error Handling
Registry operations must implement robust and structured error handling. This includes raising typed exceptions or returning structured error results. All errors encountered during registry operations will be logged via the ONEX logging framework, ensuring traceability for debugging and consistent behavior across registry consumers.

Standard exceptions to be defined and used include:
* `NodeNotFound`: When a requested node cannot be located.
* `InvalidMetadata`: When a node or adapter's metadata fails validation.
* `PluginLoadError`: When there's an issue loading a plugin or its registry instance.
* `RegistryConflictError`: When a conflict resolution mechanism is triggered for `node_id`s.

### 8. Security Considerations (Early Mention)
The architecture will lay groundwork for future security controls (e.g., signed metadata, sandboxing) to ensure the integrity and safety of third-party plugins. Details are deferred to Milestone 4.

---

## Operational Features
- CLI commands for registry introspection: `list`, `show`, `validate`, `reload`.
- Registry health/status API (CLI or Python method).
- Registry event hooks (emit events for node/adapter registration, conflict, error).
- ONEX logging/metrics/tracing integration for registry operations.
- Registry provenance tracking (source, load timestamp, metadata hash).
- Audit log for registry precedence decisions and fallback paths.
- TODO: Add CLI/UX diagrams or command examples.

---

## Security & Policy
- Pluggable registry policies (conflict resolution, version selection, validation strictness).
- Security controls (allowlist/denylist, sandboxing, signed metadata for production).
- Attestation and trust anchors (signed metadata, provenance verification).

---

## Recommended Practices
* Node metadata SHOULD include a Git commit hash for versioned traceability.
* Registry implementations SHOULD log all precedence decisions, errors, and resolution traces.
* All registry methods MUST raise typed exceptions or return structured errors for reliable debugging.

---

## Open Questions & Considerations
While the core architecture is defined, some aspects warrant further consideration:

* **Conflict Resolution:** If two registries provide the same node ID, how strict should the warning or audit log entry be when precedence is applied?
* **Validation Strictness:** How strict should metadata validation be? Should non-conforming plugins be ignored, flagged, or cause errors in all modes?
* **Performance Optimization:** For very large plugin ecosystems, should we implement caching or lazy-loading mechanisms for registries? Should we track registry performance metrics (e.g., lookup time, cache hit rate) for future optimization?
* **Adapter Sharing Strategy:** Should there be a central registry specifically for shared adapters, or should adapters always be referenced via node metadata?
* **Versioning Ambiguity:** How should the registry prioritize between versions with identical IDs but differing trust scores or timestamps?
* **Namespace Isolation Scope:** Should all registries inherently support namespacing, or should it be an opt-in feature for specific registry implementations?
* **Registry Persistency:** What mechanisms are needed to persist dynamically registered nodes/adapters, or cached registry states, across application restarts?
* **Cross-Language Support:** How would the registry and adapter protocol evolve to support nodes or adapters implemented in other programming languages (e.g., via gRPC, FFI)?
* **Runtime Registry Management API:** Should there be a high-level Python API for dynamically adding, updating, or removing nodes/adapters from registries at runtime, complementing the CLI?

---

## 2025-06 Loader and Registry Enhancements

# 2025-06 Update: Registry-Centric, Versioned Artifact Layout

ONEX now enforces a fully registry-driven, versioned artifact structure. All nodes, adapters, contracts, runtimes, CLI tools, and packages are versioned in their own subdirectories, with explicit metadata and registry references. The loader and CI enforce this structure using a `.onextree` manifest and registry metadata files.

- See [structural_conventions.md](../nodes/structural_conventions.md) and [canonical_file_types.md](../standards/canonical_file_types.md) for full rationale and canonical examples.

## Example Directory Layout

```
src/omnibase/
  nodes/
    stamper_node/
      v1_0_0/
        node.py
        node.onex.yaml
        contract.yaml
        adapters/
          cli_adapter.py
        tests/
          test_node.py
          fixtures/
            sample_input.yaml
  runtimes/
    onex_runtime/
      v1_0_0/
        runtime.py
        runtime.yaml
  cli_tools/
    onex/
      v1_0_0/
        cli_main.py
        cli_tool.yaml
  registry/
    registry.yaml
    adapters.yaml
    contracts.yaml
    runtimes.yaml
    packages.yaml
    cli_tools.yaml
```

- All artifacts are versioned in their own subdirectories.
- All references are explicit in metadata and resolved via the registry.
- No symlinks or direct imports—everything is loaded dynamically by the registry.
- Compatibility is managed via semantic version ranges in metadata.
- CLI tools, nodes, adapters, contracts, runtimes, and packages can all evolve independently, with the registry enforcing compatibility and discoverability.

## Loader and .onextree Manifest

- The `.onextree` file is a declarative manifest describing the expected structure of ONEX project directories and artifact packages.
- Loader only recognizes a version if `node.onex.yaml` is present or a `.wip` marker file is set in the version directory.
- Adapters and contracts must be referenced in `node.onex.yaml` with explicit module/class and filename.

### Milestone 2: Registry Foundation & Extensibility
* Implement protocol-driven, chainable registries (core, plugin, per-node).
* Enforce canonical metadata (YAML/JSON, schema validation).
* Integrate registry namespacing and versioned node support.
* Develop basic CLI commands for registry introspection (`list`, `show`, `validate`).
* Establish conflict resolution rules and precedence order (core > plugin > per-node).
* Provide a stub for the hot reloading/dynamic registration API.
* Implement standard structured error handling and logging for registry operations.
* Ensure node metadata includes Git commit hash for traceability.
* **Registry self-validation and linting:** Add a `registry lint` CLI command to validate all loaded registries and node metadata, check for duplicates, missing fields, and adapter reference validity. Optionally, auto-fix or scaffold missing metadata in dev mode.
* **Initial Testing Strategy:** Define and implement initial unit/integration testing strategy for core registry components.

### Milestone 3: Plugin Ecosystem & Observability
* Implement plugin/entry point discovery (setuptools/Poetry plugins, user config fallback).
* Develop a registry health/status API (accessible via CLI or Python method).
* Add registry event hooks (to emit events for node/adapter registration, conflict, error).
* Integrate ONEX logging, metrics, and tracing for comprehensive registry operations observability.
* Enable registry provenance tracking (source, load timestamp, metadata hash).
* Implement an audit log for registry precedence decisions and fallback paths.
* Extend CLI with `onex registry reload` and `onex registry validate --strict` commands.
* **Registry "Explain" and Traceability:** Add a `registry explain <node_id>` command/API to show which registry provided a node, the resolution path, and any conflicts or overrides.
* **Registry "Dry Run" and Impact Analysis:** Allow a "dry run" mode for registry changes to simulate effects and report what would change or break.
* **Registry "Snapshot" and Rollback:** Support exporting/importing registry "snapshots" for debugging, rollback, or reproducibility.
* **Registry "Diff" and Change Auditing:** Add a `registry diff <snapshot1> <snapshot2>` command to compare two registry states and highlight changes.
* **Registry "Live Watch" and Hot Reload:** Implement a "watch" mode to monitor registry sources for changes and auto-reload/validate on change.
* **Performance Monitoring Definition:** Specify what metrics will be tracked (e.g., number of registered nodes, time to resolve, cache hit/miss rates) and how they will be exposed.

### Milestone 4: Policy, Performance, and Security
* Implement pluggable registry policies (for conflict resolution, version selection, validation strictness).
* Introduce registry caching and lazy loading mechanisms for large plugin ecosystems.
* Gather and report performance metrics (lookup time, cache hit rate, registry load time).
* Develop security controls (allowlist/denylist, sandboxing, signed metadata for production).
* Support registry schema evolution (versioned schemas, migration tools, multi-version support).
* Build a comprehensive registry test harness (for fuzzing, simulated failures, error handling verification).
* **Registry "Policy Packs":** Allow loading policy packs (YAML/JSON or Python plugins) for custom rules and validation strictness, swappable per environment.
* **Registry "Health Dashboard":** Build a web or CLI dashboard to show registry health, loaded nodes/adapters, errors, and performance metrics in real time.
* **Registry "Plugin Marketplace" Integration:** Integrate with a plugin marketplace or index for discovery, install, and update of node/adapters/plugins directly from the CLI.
* **Policy Granularity:** Define and support policy granularity (global, per-registry, per-category, per-node).

### Future Ideas (Post-M4 or as-needed)
* Fully implement hot reloading/dynamic registration.
* Develop self-describing registries (`describe()` method, metadata output).
* Integrate attestation and trust anchors (signed metadata, provenance verification).
* Provide robust namespace-aware registry isolation for multi-tenant or feature-flagged environments.
* Create automated metadata scaffolding and repair tools.
* Implement advanced symbolic aliasing and resolution trace emission.
* Explore registry performance auto-tuning and adaptive caching.
* Develop a user-facing registry dashboard (web or CLI TUI) for live introspection.
* **Registry "Schema Evolution Assistant":** Provide tooling to help migrate node/adapter metadata as schemas evolve, with detection and auto-migration support.
* **Automated Node Testing Integration:** Provide hooks or utilities for automated testing frameworks to discover and execute tests for registered nodes and adapters.

---

## Document Maintenance
* **Versioning:** This document should include a semantic version in its metadata block at the top. Major changes should increment the major version, minor changes for new features, and patch for clarifications or editorial updates.
* **Review Cadence:** The architecture document should be reviewed quarterly and before major releases to ensure it remains current and authoritative.
* **Change Communication:** All changes to this document should be made via pull requests and summarized in a changelog section or commit history for traceability.

---

## Editorial Notes for Maintainers
* The `ProtocolNodeCliAdapter` definition is centralized in section 1 for clarity and maintainability; all references elsewhere should point to this canonical definition.
* Registry namespacing is an optional, opt-in feature; not all registries are required to implement it.
* When implementing performance tracking, ensure that metrics such as lookup time and cache hit rates are explicitly measured and logged as part of ONEX observability.
* All error handling must use typed exceptions and integrate with the ONEX logging framework.
* Maintain this document as the single source of truth for registry architecture.
