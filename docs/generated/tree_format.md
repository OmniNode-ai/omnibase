<!-- === OmniNode:Metadata ===
author: OmniNode Team
copyright: OmniNode Team
created_at: '2025-05-28T12:40:26.349692'
description: Stamped by ONEX
entrypoint: python://tree_format.md
hash: 612b20869e35b01d9cc65875d4c815a23732bc869fb53c74a154bf18bf492aea
last_modified_at: '2025-05-29T11:50:14.922090+00:00'
lifecycle: active
meta_type: tool
metadata_version: 0.1.0
name: tree_format.md
namespace: omnibase.tree_format
owner: OmniNode Team
protocol_version: 0.1.0
runtime_language_hint: python>=3.11
schema_version: 0.1.0
state_contract: state_contract://default
tools: null
uuid: 3357554d-85ad-49b0-9f63-bb3af324c0b9
version: 1.0.0

<!-- === /OmniNode:Metadata === -->


# onextree_format

**Purpose:**
This schema defines the expected structure of ONEX project directories and individual artifact packages, enabling programmatic validation and discovery by the ONEX registry. The `.onextree` file is a declarative manifest describing the desired or actual directory structure for ONEX projects and artifact packages. It is used by the registry for validation, discovery, and enforcement of standards.

**Version:** 1.0.0

Canonical schema for ONEX .tree files. Captures the directory/file hierarchy as a nested tree.

> **See Also:** The [Registry Architecture](../registry_architecture.md) document is the canonical reference for registry, loader, and artifact discovery logic in ONEX. This document should be consulted for all questions about registry-centric layout, versioning, and compatibility enforcement.

## Changelog

- Initial release of all canonical schemas:
  - `onex_node.yaml`
  - `tree_format.yaml`, `tree_format.json`
  - `execution_result.yaml`, `execution_result.json`
  - `state_contract.yaml`, `state_contract.json`
- All schemas include a `SCHEMA_VERSION` field at the top-level.
- Dual-format (YAML/JSON) support for all schemas.
- Registry-driven, protocol-injected tests and usage examples for all formats.

---

## Deprecation Policy

- All schema deprecations must be documented in this changelog.
- Deprecated fields or versions must be marked in the schema and referenced here.
- Breaking changes require a major version bump and migration notes.
- Backward-compatible changes require a minor version bump.
- Patch version increments are for bugfixes or clarifications only.



## Fields
| Name     | Type           | Required | Description                                                        | Enum                |
|----------|----------------|----------|--------------------------------------------------------------------|---------------------|
| name     | string         | Yes      | The name of the file or directory.                                 |                     |
| type     | string         | Yes      | The type of filesystem entry.                                      | directory, file     |
| children | array<object>  | No       | List of child entries (only for type: directory).                  |                     |
| metadata | string         | No       | (Rare) Path to an associated metadata file for this entry. In ONEX, the presence of a .yaml file (e.g., node.onex.yaml, cli_adapter.yaml) in a versioned directory is the canonical metadata for that artifact version. The 'metadata' field is typically omitted except for special cases, such as a file with its own metadata. |                     |
| path     | string         | No       | Relative path from the root of the .onextree file (optional).      |                     |

**Note:** In ONEX registry-centric layouts, the .yaml file (e.g., node.onex.yaml) in a versioned directory is the metadata for the entire artifact version (e.g., the node version), not for individual files like node.py. The 'metadata' field is only used if a file or directory has a distinct metadata file not following the standard convention. For most ONEX use cases, 'metadata' is omitted.

**Example of metadata field usage (rare):**
```yaml
- type: file
  name: custom_script.py
  metadata: custom_script_metadata.yaml
```



## Example

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

## Canonical Example (2025-06 Update)

```yaml
type: directory
name: nodes
children:
  - type: directory
    name: stamper_node
    children:
      - type: directory
        name: v1_0_0
        children:
          - type: file
            name: node.py
          - type: file
            name: node.onex.yaml
          - type: file
            name: contract.yaml
          - type: directory
            name: models
            children: []
          - type: directory
            name: helpers
            children: []
          - type: directory
            name: adapters
            children:
              - type: file
                name: cli_adapter.py
              - type: file
                name: web_adapter.py
          - type: directory
            name: tests
            children: []
          - type: directory
            name: fixtures
            children: []
      - type: directory
        name: v2_0_0
        children:
          - type: file
            name: .wip
  - type: directory
    name: another_node
    children:
      - type: directory
        name: v1_0_0
        children:
          - type: file
            name: node.py
          - type: file
            name: node.onex.yaml
          - type: file
            name: contract.yaml
          - type: directory
            name: adapters
            children:
              - type: file
                name: cli_adapter.py
```

**Note:**
- `node.onex.yaml` is the metadata for the node version directory, not for node.py or any individual code file.
- Loader only recognizes a version if `node.onex.yaml` is present or a `.wip` marker file is set in the version directory.
- Adapters and contracts must be referenced in `node.onex.yaml` with explicit module/class and filename.
- See [structural_conventions.md](../nodes/structural_conventions.md) for rationale and full details.

## Registry-Centric, Versioned Artifact Example (2025-06 Update)

This example shows a full extended nested registry-centric layout including CLI tools, runtimes, packages, and detailed artifact versioning. All references are explicit and resolved via the registry—no direct imports or symlinks.

```yaml
omnibase:
  nodes:
    stamper_node:
      v2_0_0:
        node.onex.yaml
        node.py
        adapters:
          cli_adapter:
            v2_1_0:
              cli_adapter.yaml
              cli_adapter.py
        contracts:
          stamper_contract:
            v1_1_0:
              contract.yaml
        models:
          v2_0_0:
            state.py
        tests:
          v2_0_0:
            test_node.py
            test_cli_adapter.py
  runtimes:
    onex_runtime:
      v3_0_0:
        runtime.yaml
        runtime.py
  packages:
    serialization:
      v1_0_0:
        serialization.py
        serialization.yaml
  cli_tools:
    onex:
      v1_1_0:
        cli_main.py
        cli_tool.yaml
  registry:
    registry.yaml
    adapters.yaml
    contracts.yaml
    runtimes.yaml
    packages.yaml
    cli_tools.yaml
```

**Note:**
- `node.onex.yaml` is the metadata for the node version directory, not for node.py or any individual code file.
- All artifacts are versioned in their own subdirectories.
- All references are explicit in metadata and resolved via the registry.
- No symlinks or direct imports—everything is loaded dynamically by the registry.
- Compatibility is managed via semantic version ranges in metadata.
- CLI tools, nodes, adapters, contracts, runtimes, and packages can all evolve independently, with the registry enforcing compatibility and discoverability.

### Structural Clarifications and Best Practices

- Artifact categories (`adapters`, `contracts`, `runtimes`, `packages`, `cli_tools`) may be top-level or nested under the node depending on reuse strategy.
  - If the artifact is node-scoped and not reused elsewhere, place it under the node's directory.
  - If the artifact is reused across multiple nodes or systems, it should be placed in the top-level namespace for discoverability.
- Each artifact version resides in its own subdirectory and must include a corresponding `.yaml` metadata file.
- All metadata references must be explicit: no implicit imports or filesystem-relative assumptions.
- Artifacts without `*.yaml` metadata will be ignored by the registry.
- Compatibility metadata (e.g. `compatible_node_versions`) must use valid semantic version ranges and is enforced by the registry loader.

### Example Metadata Snippets

**nodes/stamper_node/v2_0_0/node.onex.yaml**
```yaml
node_id: "stamper_node"
version: "2.0.0"
adapter_ref:
  id: "cli_adapter"
  version: "2.1.0"
contract_ref:
  id: "stamper_contract"
  version: "1.1.0"
runtime_ref:
  id: "onex_runtime"
  version: "3.0.0"
```

**nodes/stamper_node/v2_0_0/adapters/cli_adapter/v2_1_0/cli_adapter.yaml**
```yaml
adapter_id: "cli_adapter"
version: "2.1.0"
compatible_node_versions: ">=2.0.0,<3.0.0"
compatible_runtime_versions: ">=3.0.0,<4.0.0"
```

**nodes/stamper_node/v2_0_0/contracts/stamper_contract/v1_1_0/contract.yaml**
```yaml
contract_id: "stamper_contract"
version: "1.1.0"
```

**runtimes/onex_runtime/v3_0_0/runtime.yaml**
```yaml
runtime_id: "onex_runtime"
version: "3.0.0"
```

**cli_tools/onex/v1_1_0/cli_tool.yaml**
```yaml
cli_tool_id: "onex"
version: "1.1.0"
compatible_node_versions: ">=2.0.0,<3.0.0"
compatible_adapter_versions: ">=2.1.0,<3.0.0"
compatible_runtime_versions: ">=3.0.0,<4.0.0"
compatible_contract_versions: ">=1.1.0,<2.0.0"
description: "ONEX CLI tool for node orchestration and management."
entrypoint: "cli_main.py"
```

### Registry Index Example

**registry/cli_tools.yaml**
```yaml
cli_tools:
  - id: "onex"
    versions:
      - "1.1.0"
```

**registry/adapters.yaml**
```yaml
adapters:
  - id: "cli_adapter"
    versions:
      - "2.1.0"
```

### Notes
- All artifacts are versioned in their own subdirectories.
- All references are explicit in metadata and resolved via the registry.
- No symlinks or direct imports—everything is loaded dynamically by the registry.
- Compatibility is managed via semantic version ranges in metadata.
- CLI tools, nodes, adapters, contracts, runtimes, and packages can all evolve independently, with the registry enforcing compatibility and discoverability.

### Test Matrix and Registry Hygiene

- Recommended: auto-generate a compatibility test matrix from registry metadata, validating all declared artifact combinations.
- Recommended: integrate registry metadata validation and schema checks into CI.
- Future: support signed metadata and provenance tracking for trusted artifact execution.

# 2025-06 Update: Canonical .onextree Manifest and Registry-Centric Layout

The `.onextree` file is now the canonical, registry-driven, versioned artifact manifest for ONEX projects. All nodes, adapters, contracts, runtimes, CLI tools, and packages are versioned in their own subdirectories, with explicit metadata and registry references. The loader and CI enforce this structure using the `.onextree` manifest and registry metadata files.

- See [registry_architecture.md](../registry_architecture.md) and [structural_conventions.md](../nodes/structural_conventions.md) for full rationale and canonical examples.

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

## Migration Note

- Legacy unversioned layouts are no longer supported. All documentation, CI, and tooling must reference the registry-centric, versioned structure and `.onextree` manifest.
