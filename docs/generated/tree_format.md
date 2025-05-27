<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: tree_format.md
version: 1.0.0
uuid: 79d0230f-7de1-4205-965c-26f831f17395
author: OmniNode Team
created_at: 2025-05-27T07:29:38.358916
last_modified_at: 2025-05-27T17:26:51.895243
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: de906737c0c64914765435c554370366396bd28eff23fb188f30becad65518c2
entrypoint: python@tree_format.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.tree_format
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Tree Format Schema

> **Status:** Canonical  
> **Last Updated:** 2025-05-27  
> **Purpose:** Define the schema for ONEX .onextree files and directory structure  
> **Audience:** Registry systems, project maintainers, CI/CD engineers  
> **Version:** 1.0.0

---

## Overview

This schema defines the expected structure of ONEX project directories and individual artifact packages, enabling programmatic validation and discovery by the ONEX registry. The `.onextree` file is a declarative manifest describing the desired or actual directory structure for ONEX projects and artifact packages. It is used by the registry for validation, discovery, and enforcement of standards.

> **See Also:** The [Registry Architecture](../registry_architecture.md) document is the canonical reference for registry, loader, and artifact discovery logic in ONEX. This document should be consulted for all questions about registry-centric layout, versioning, and compatibility enforcement.

---

## Schema Fields

| Name     | Type           | Required | Description                                                        | Enum                |
|----------|----------------|----------|--------------------------------------------------------------------|---------------------|
| name     | string         | Yes      | The name of the file or directory.                                 |                     |
| type     | string         | Yes      | The type of filesystem entry.                                      | directory, file     |
| children | array<object>  | No       | List of child entries (only for type: directory).                  |                     |
| metadata | string         | No       | (Rare) Path to an associated metadata file for this entry. In ONEX, the presence of a .yaml file (e.g., node.onex.yaml, cli_adapter.yaml) in a versioned directory is the canonical metadata for that artifact version. The 'metadata' field is typically omitted except for special cases, such as a file with its own metadata. |                     |
| path     | string         | No       | Relative path from the root of the .onextree file (optional).      |                     |

**Note:** In ONEX registry-centric layouts, the .yaml file (e.g., node.onex.yaml) in a versioned directory is the metadata for the entire artifact version (e.g., the node version), not for individual files like node.py. The 'metadata' field is only used if a file or directory has a distinct metadata file not following the standard convention. For most ONEX use cases, 'metadata' is omitted.

---

## Basic Tree Structure

### Simple Directory Tree

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

### Registry-Centric Layout

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

---

## Advanced Registry Layout

### Complete Ecosystem Structure

```yaml
name: omnibase
type: directory
children:
  - name: nodes
    type: directory
    children:
      - name: stamper_node
        type: directory
        children:
          - name: v2_0_0
            type: directory
            children:
              - name: node.onex.yaml
                type: file
              - name: node.py
                type: file
              - name: adapters
                type: directory
                children:
                  - name: cli_adapter
                    type: directory
                    children:
                      - name: v2_1_0
                        type: directory
                        children:
                          - name: cli_adapter.yaml
                            type: file
                          - name: cli_adapter.py
                            type: file
              - name: contracts
                type: directory
                children:
                  - name: stamper_contract
                    type: directory
                    children:
                      - name: v1_1_0
                        type: directory
                        children:
                          - name: contract.yaml
                            type: file
              - name: models
                type: directory
                children:
                  - name: v2_0_0
                    type: directory
                    children:
                      - name: state.py
                        type: file
              - name: tests
                type: directory
                children:
                  - name: v2_0_0
                    type: directory
                    children:
                      - name: test_node.py
                        type: file
                      - name: test_cli_adapter.py
                        type: file
  - name: runtimes
    type: directory
    children:
      - name: onex_runtime
        type: directory
        children:
          - name: v3_0_0
            type: directory
            children:
              - name: runtime.yaml
                type: file
              - name: runtime.py
                type: file
  - name: packages
    type: directory
    children:
      - name: serialization
        type: directory
        children:
          - name: v1_0_0
            type: directory
            children:
              - name: serialization.py
                type: file
              - name: serialization.yaml
                type: file
  - name: cli_tools
    type: directory
    children:
      - name: onex
        type: directory
        children:
          - name: v1_1_0
            type: directory
            children:
              - name: cli_main.py
                type: file
              - name: cli_tool.yaml
                type: file
  - name: registry
    type: directory
    children:
      - name: registry.yaml
        type: file
      - name: adapters.yaml
        type: file
      - name: contracts.yaml
        type: file
      - name: runtimes.yaml
        type: file
      - name: packages.yaml
        type: file
      - name: cli_tools.yaml
        type: file
```

---

## Metadata Integration

### Rare Metadata Field Usage

The `metadata` field is only used for special cases where a file has its own distinct metadata:

```yaml
- type: file
  name: custom_script.py
  metadata: custom_script_metadata.yaml
  path: scripts/custom_script.py
```

### Standard Metadata Conventions

In most cases, metadata follows standard conventions:
- `node.onex.yaml` for node versions
- `cli_adapter.yaml` for CLI adapters
- `contract.yaml` for contracts
- `runtime.yaml` for runtimes

---

## Registry Integration

### Artifact Metadata Examples

#### Node Metadata (nodes/stamper_node/v2_0_0/node.onex.yaml)

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

#### Adapter Metadata (adapters/cli_adapter/v2_1_0/cli_adapter.yaml)

```yaml
adapter_id: "cli_adapter"
version: "2.1.0"
compatible_node_versions: ">=2.0.0,<3.0.0"
compatible_runtime_versions: ">=3.0.0,<4.0.0"
```

#### CLI Tool Metadata (cli_tools/onex/v1_1_0/cli_tool.yaml)

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

### Registry Index Files

#### CLI Tools Registry (registry/cli_tools.yaml)

```yaml
cli_tools:
  - id: "onex"
    versions:
      - "1.1.0"
```

#### Adapters Registry (registry/adapters.yaml)

```yaml
adapters:
  - id: "cli_adapter"
    versions:
      - "2.1.0"
```

---

## Structural Conventions

### Artifact Organization

#### Node-Scoped vs Reusable Artifacts

- **Node-scoped**: Place under the node's directory if not reused elsewhere
- **Reusable**: Place in top-level namespace for discoverability across nodes

#### Version Management

- Each artifact version resides in its own subdirectory
- Must include corresponding `.yaml` metadata file
- Artifacts without metadata are ignored by the registry

#### Reference Resolution

- All metadata references must be explicit
- No implicit imports or filesystem-relative assumptions
- Compatibility metadata uses semantic version ranges
- Registry enforces compatibility and discoverability

### Best Practices

#### Directory Structure

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

#### Compatibility Management

- Use semantic version ranges in metadata
- Validate compatibility in CI/CD pipelines
- Auto-generate compatibility test matrix from registry metadata
- Integrate registry metadata validation into CI

---

## Schema Versioning

### Current Version: 1.0.0

### Changelog

#### 1.0.0 (2025-05-27)
- Initial release of tree format schema
- Support for registry-centric layouts
- Comprehensive artifact versioning
- Metadata integration patterns
- Compatibility management framework

### Deprecation Policy
- All schema deprecations must be documented in this changelog
- Deprecated fields or versions must be marked in the schema and referenced here
- Breaking changes require a major version bump and migration notes
- Backward-compatible changes require a minor version bump
- Patch version increments are for bugfixes or clarifications only

---

## Migration Notes

### Legacy Layout Migration

Legacy unversioned layouts are no longer supported. All documentation, CI, and tooling must reference the registry-centric, versioned structure and `.onextree` manifest.

### Migration Steps

1. **Create versioned directories** for all artifacts
2. **Add metadata files** for each artifact version
3. **Update references** to use explicit registry references
4. **Generate .onextree manifest** describing the new structure
5. **Update CI/CD** to validate registry metadata and compatibility

---

## Integration Examples

### CLI Usage

```bash
# Generate .onextree manifest
onex run tree_generator_node --args='["--root-directory", "src/omnibase", "--output-path", ".onextree"]'

# Validate tree structure
onex validate --schema tree_format .onextree

# Check registry compatibility
onex validate registry --check-compatibility
```

### Programmatic Usage

```python
from omnibase.schemas import TreeFormatSchema
from omnibase.core.validation import validate_schema

# Load and validate tree structure
with open('.onextree', 'r') as f:
    tree_data = yaml.safe_load(f)

validation_result = validate_schema(tree_data, TreeFormatSchema)
if validation_result.is_valid:
    print("Tree structure is valid")
else:
    print(f"Tree validation errors: {validation_result.errors}")
```

---

## References

- [Registry Architecture](../registry_architecture.md)
- [Repository Structure](../architecture/repository_structure.md)
- [ONEX Node Specification](../onex_node_spec.md)
- [Lifecycle Policy](../lifecycle_policy.md)

---

**Note:** The `.onextree` file is the canonical, registry-driven, versioned artifact manifest for ONEX projects. All nodes, adapters, contracts, runtimes, CLI tools, and packages are versioned in their own subdirectories, with explicit metadata and registry references.
