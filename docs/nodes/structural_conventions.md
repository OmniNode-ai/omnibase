<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: structural_conventions.md
version: 1.0.0
uuid: 9a32f869-3a7d-4b18-828f-fbb0682a158a
author: OmniNode Team
created_at: 2025-05-22T14:03:21.847030
last_modified_at: 2025-05-22T21:19:13.497703
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: ef395f65a6de99e52bc564f301f9a1c6b4b3c65fec7880e21cd5e738e5bbe22e
entrypoint: python@structural_conventions.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.structural_conventions
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Architecture: Structural Conventions

> **Status:** Canonical
> **Series:** Node Architecture
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting documentation.

> **See Also:** The [Registry Architecture](../registry_architecture.md) document is the canonical reference for registry, loader, and artifact discovery logic in ONEX. This document should be consulted for all questions about registry-centric layout, versioning, and compatibility enforcement.

## 09 – Structural Conventions

### Context & Origin

This document defines the canonical directory structure, file layout, discovery mechanisms, and module typing conventions for ONEX nodes. It builds on the [nodes as functions](./index.md) model to define a consistent, discoverable, and maintainable structure for node implementations. It emerged from the need to standardize how node functions are packaged, discovered, and referenced.

## Protocol Placement Guidance

ONEX protocols (Python Protocols/ABCs) must be placed according to their intended scope and usage. This ensures clarity, maintainability, and discoverability across the codebase.

### Protocol Types
- **Runtime Protocol:** Used only by the ONEX runtime system (execution, eventing, I/O, orchestration). Not needed by models, CLI, or node-local logic outside runtime execution.
- **Core/Cross-Cutting Protocol:** Used by multiple layers (models, CLI, nodes, runtime, plugins). Defines contracts fundamental to ONEX, not just runtime.
- **Node-Local Protocol:** Used only within a single node's implementation. Not imported outside that node's directory.

### Decision Criteria Table
| Protocol Type         | Used Only by Runtime? | Used by CLI/Tools? | Used by Nodes Directly? | Used by Models? | Location                        |
|-----------------------|----------------------|--------------------|------------------------|-----------------|----------------------------------|
| File I/O (IOClient)   | Yes                  | Maybe              | No                     | No              | runtime/protocol/                |
| EventBusProtocol      | Yes                  | Maybe              | No                     | No              | runtime/protocol/                |
| NodeRunnerProtocol    | Yes                  | No                 | No                     | No              | runtime/protocol/                |
| StateModelProtocol    | No                   | Yes                | Yes                    | Yes             | protocol/ (core/global)          |
| ErrorCodeProtocol     | No                   | Yes                | Yes                    | Yes             | protocol/ (core/global)          |
| RegistryProtocol      | Maybe                | Yes                | Maybe                  | Maybe           | protocol/ (core/global) if shared|
| NodeLocalHandler      | No                   | No                 | Yes (one node only)    | No              | node directory                   |

### Canonical Questions to Ask
1. Is this protocol only used by the runtime system (execution, eventing, I/O, orchestration)?
   - If yes, put it in `runtime/protocol/`.
2. Is this protocol used by models, CLI, or node-local code outside of runtime?
   - If yes, put it in `protocol/` (core/global).
3. Is this protocol only used by a single node?
   - If yes, keep it node-local.
4. Is this protocol likely to be extended or swapped by plugins or external tools?
   - If yes, and it's not runtime-specific, keep it global.

### Summary Table
| Protocol Type         | Location                        |
|----------------------|---------------------------------|
| Runtime-only         | runtime/protocol/               |
| Cross-cutting/core   | protocol/                       |
| Node-local           | node directory                  |

**All contributors must follow this guidance when adding or refactoring protocols.**

---

### Directory and Module Structure

ONEX nodes follow a standardized directory structure that makes them easily discoverable and ensures proper isolation and dependency management.

#### ✅ Standard Node Structure

```
node_name/                      # Root directory for the node
├── node.onex.yaml              # Node metadata and contract definition
├── src/                        # Source code for the node implementation
│   ├── __init__.py             # Package initialization
│   ├── main.py                 # Main implementation (often the entrypoint)
│   └── helpers/                # Internal helpers specific to this node
├── tests/                      # Tests for this specific node
│   ├── __init__.py
│   ├── test_main.py            # Tests for the main implementation
│   └── fixtures/               # Test fixtures and helpers
└── README.md                   # Node-specific documentation
```

#### ✅ Node Discovery via `.tree`

ONEX nodes are discovered through a centralized `.tree` file at the root of a repository or project, which catalogs all available nodes.

```yaml
# Example .tree file
nodes:
  - name: validator.schema
    path: nodes/validator.schema/node.onex.yaml
  - name: transform.summarize
    path: nodes/transform.summarize/node.onex.yaml
  # Additional nodes...
```

This centralized discovery mechanism enables tools, runtimes, and CI systems to find and validate all nodes without traversing the entire directory structure.

---

### File Layouts and Naming

ONEX follows specific conventions for file naming and structure to ensure consistency and predictability.

#### ✅ File Naming Conventions

| File Type        | Naming Pattern              | Example                       |
|------------------|-----------------------------|------------------------------ |
| Node Metadata    | `node.onex.yaml`            | `node.onex.yaml`              |
| Entrypoint       | Referenced in metadata      | `src/main.py`                 |
| Tests            | `test_*.py`                 | `tests/test_main.py`          |
| Internal Helpers | `*_helper.py`, `*_util.py`  | `src/helpers/parsing_util.py` |

#### ✅ Core Files

* **node.onex.yaml**: The canonical metadata file that defines the node's interface, dependencies, and execution properties. Contains fields like `state_contract`, `dependencies`, `entrypoint`, etc. as defined in [Node Contracts and Metadata](./node_contracts.md).
* **Entrypoint File**: The main implementation file specified by the `entrypoint.target` field in the metadata. This file contains the core function that implements the node's primary behavior and adheres to the specified `state_contract`.
* **README.md**: Documents the node's purpose, usage, examples, and any special considerations. Should be kept in sync with metadata properties.

---

### Type Hinting and State Contracts

ONEX nodes use explicit type definitions to represent their input and output contracts.

#### ✅ State Contracts as Types

```python
# Example state contract implementation in Python
from pydantic import BaseModel
from typing import List, Optional

class SummaryInputState(BaseModel):
    """Input state contract for the summarizer node."""
    text: str
    max_length: Optional[int] = 100
    preserve_keywords: List[str] = []

class SummaryOutputState(BaseModel):
    """Output state contract for the summarizer node."""
    summary: str
    original_length: int
    summary_length: int
    preserved_keywords_count: int
```

These types enforce the structure of input and output states, providing both runtime validation and development-time type checking.

Nodes that support reducer-based internal state or `memoization_tier: deep` caching should also ensure their state types and execution outputs are schema-bound. Reducers may implement snapshot-compatible state models using `BaseModel`, while composite nodes should document the types of all subgraph input and output contracts to support trace hashing and planner compatibility.

---

### Module Typing and Categorization

ONEX modules are categorized based on their primary role and behavior to aid in discovery and composition.

#### ✅ Node Type Categories

| Type          | Purpose                                            | Examples                           |
|---------------|----------------------------------------------------|------------------------------------|
| `tool`        | General-purpose transformation or utility function | `validator`, `parser`, `formatter`

### Canonical Versioned Node Structure (2025-06 Update)

ONEX nodes now use a versioned directory structure to support multiple versions, robust adapter management, and future extensibility. Each node version is isolated, and all adapters, contracts, and helpers are versioned per node.

```
nodes/
  stamper_node/
    v1_0_0/
      node.py                # Main implementation (entrypoint)
      node.onex.yaml         # Canonical metadata (references entrypoint, adapter, contract)
      contract.yaml          # State contract (normalized name for CI/tooling)
      models/                # State/input/output models
      helpers/               # Node-local helpers
      adapters/              # All adapters (e.g., cli_adapter.py, web_adapter.py)
      tests/                 # Node-local tests
      fixtures/              # Node-local test fixtures
    v2_0_0/                  # (Optional, empty or WIP for roadmap)
      WIP                    # Loader ignores unless node.onex.yaml or WIP flag present
  another_node/
    v1_0_0/
      ...
```

#### Rationale
- **Adapters**: Always versioned and node-local to prevent global conflicts. Place all adapters in `adapters/`.
- **Contracts**: Use `contract.yaml` for consistency and glob-friendly tooling.
- **Metadata**: `node.onex.yaml` is the only canonical metadata file; it references the entrypoint, adapter, and contract.
- **Empty Version Stubs**: Loader ignores empty versions unless a `node.onex.yaml` or `WIP` marker is present.

#### Canonical `.onextree` Example

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
            metadata: node.onex.yaml
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
            name: WIP
  - type: directory
    name: another_node
    children:
      - type: directory
        name: v1_0_0
        children:
          - type: file
            name: node.py
            metadata: node.onex.yaml
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

#### Loader Behavior
- Loader only recognizes a version if `node.onex.yaml` is present or a `WIP` marker is set.
- Adapters and contracts must be referenced in `node.onex.yaml` with explicit module/class and filename.
- All metadata, contract, and adapter references are validated at load time.

#### See Also
- [Registry Architecture](../nodes/registry_architecture.md) for advanced loader, registry, and plugin discovery features.
- [Canonical File Types](../standards/canonical_file_types.md) for naming conventions.

# 2025-06 Update: Registry-Centric, Versioned Artifact Layout

ONEX now enforces a fully registry-driven, versioned artifact structure. All nodes, adapters, contracts, runtimes, CLI tools, and packages are versioned in their own subdirectories, with explicit metadata and registry references. The loader and CI enforce this structure using a `.onextree` manifest and registry metadata files.

## Canonical Example Directory Layout

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

See [registry_architecture.md](../registry_architecture.md) and [canonical_file_types.md](../standards/canonical_file_types.md) for full rationale and canonical examples.
