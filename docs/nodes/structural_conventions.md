<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: structural_conventions.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 7573848c-85e2-45e2-b3a8-0e0eb2745c33 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:41:40.160917 -->
<!-- last_modified_at: 2025-05-21T16:42:46.054628 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: 7c002d076df21a6b215565a1bc78088eb9fdbe2267a849d97eaf470bf6a4e5ca -->
<!-- entrypoint: {'type': 'python', 'target': 'structural_conventions.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.structural_conventions -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: structural_conventions.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 0a4e5708-4101-47e9-b653-12903411148c -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T12:33:43.436401 -->
<!-- last_modified_at: 2025-05-21T16:39:56.482623 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: dc7731abc0c946ae357c9c6068d0c31c1ad17ba9bd2f17aec68b277e3250ead2 -->
<!-- entrypoint: {'type': 'python', 'target': 'structural_conventions.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.structural_conventions -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- protocol_version: 0.1.0 -->
<!-- owner: OmniNode Team -->
<!-- copyright: OmniNode Team -->
<!-- schema_version: 0.1.0 -->
<!-- name: structural_conventions.md -->
<!-- version: 1.0.0 -->
<!-- uuid: 3f257d5d-b971-4662-8aa8-da2f51cfd682 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-21T09:28:42.663893 -->
<!-- last_modified_at: 2025-05-21T16:24:00.348207 -->
<!-- description: Stamped by ONEX -->
<!-- state_contract: state_contract://default -->
<!-- lifecycle: active -->
<!-- hash: a3109f8592bad73f280722f21ed2f955a12a8cd9bb6bc82f6e5b5f7152170c3d -->
<!-- entrypoint: {'type': 'python', 'target': 'structural_conventions.md'} -->
<!-- runtime_language_hint: python>=3.11 -->
<!-- namespace: onex.stamped.structural_conventions -->
<!-- meta_type: tool -->
<!-- === /OmniNode:Metadata === -->

# ONEX Node Architecture: Structural Conventions

> **Status:** Canonical
> **Series:** Node Architecture
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting documentation.

## 09 – Structural Conventions

### Context & Origin

This document defines the canonical directory structure, file layout, discovery mechanisms, and module typing conventions for ONEX nodes. It builds on the [nodes as functions](./index.md) model to define a consistent, discoverable, and maintainable structure for node implementations. It emerged from the need to standardize how node functions are packaged, discovered, and referenced.

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
| `tool`        | General-purpose transformation or utility function | `validator`, `parser`, `formatter` |
| `agent`       | Stateful node with complex decision-making         | `assistant`, `planner`, `reviewer` |
| `model`       | AI model wrapper                                   | `text_generator`, `embedder`       |
| `composite`   | Workflow composed of other nodes                   | `pipeline`, `orchestrator`         |
| `utility`     | Infrastructure or support function                 | `logger`, `metrics_collector`      |

Additional types may be defined as needed, but they should always be explicitly declared in the `meta_type` field of the node metadata.

---

### Canonical Rule: When to Use `runtime/` vs. Node-Local Protocols

**Use a `runtime/` directory (not node-internal) when:**

1. **The protocol is reused by multiple internal nodes**
   - If two or more nodes depend on it, duplication violates DRY.
   - *Example:* A base protocol for node-side caching or event emission, used across all internal nodes.

2. **The protocol supports the execution environment, not the domain logic**
   - Runtime-layer concerns: lifecycle hooks, internal observability, event emitters.
   - These aren't logically part of any specific node's purpose.

3. **You want to decouple runtime evolution from node logic**
   - Keeping execution or coordination logic in `runtime/` allows nodes to evolve without being tightly coupled to execution wiring.
   - Avoids circular dependencies when nodes import core features.

4. **It may eventually support node scaffolding or simulation**
   - Anything touching orchestration, CLI entrypoints, or runner context should not live in a specific node folder.

---

**Prefer node-local protocols when:**
- Protocols are domain-specific (e.g., only meaningful for `stamper_node`)
- It's a scaffold-specific abstraction that will never be reused
- It defines interaction within a node rather than across runtime or system boundaries

**Summary:**
Use `runtime/` when the protocol governs how nodes behave, not what a node does. Keep node-internal protocols for domain-specific logic.

---

**Automated Enforcement Proposal:**
To prevent protocol duplication and ensure correct placement, implement a CI check that flags any protocol used by more than one node but not located in `runtime/`. This will help maintain DRY and architectural clarity as the codebase grows.

---

### Discovery Rules

Rules governing how nodes are discovered, referenced, and composed.

#### ✅ URI-Based References

Nodes reference each other using URI-style identifiers in the format:
```
<type>://<namespace>@<version>
```

For example:
```yaml
dependencies:
  - tool://validator.schema@1.0.0
  - model://text.generator@latest
```

These URIs are resolved at execution time to locate the appropriate node implementation.

#### ✅ Version Resolution

Version specifications follow semantic versioning patterns:
* Exact version: `@1.2.3`
* Latest: `@latest`
* Range: `@^1.0.0` (compatible with 1.x.x)
* Minimum: `@>=1.2.0` (1.2.0 or newer)

The ONEX runtime resolves these version specifications against available nodes to select the appropriate implementation.

---

**Status:** This document defines the canonical directory structure, file layout, and naming conventions for ONEX nodes. All new nodes should adhere to these conventions, and existing nodes should be migrated to this structure as feasible. The conventions ensure discoverability, maintainability, and proper isolation between node implementations.

---

## Utility vs Tool: Canonical Distinction in ONEX

### Utility
- **Purpose:** Internal, reusable logic or helpers not intended for direct user invocation.
- **Location:** `src/omnibase/utils/`
- **Naming:** `utils_*.py`, `*_extractor.py`, or similar.
- **Usage:** Imported by core modules, protocols, or tools; not exposed as CLI commands.
- **Testing:** Unit tested in isolation.
- **Examples:**
  - `utils_node_metadata_extractor.py` (loads and validates metadata blocks)
  - `utils_uri_parser.py` (parses ONEX URIs; see parse_onex_uri, OnexUriModel, and UriTypeEnum)

### Tool
- **Purpose:** User-facing CLI entrypoints or scripts that perform actions, validation, or transformations.
- **Location:** `src/omnibase/tools/`
- **Naming:** `cli_*.py`, `*_generator.py`, or similar.
- **Usage:** Invoked via CLI (e.g., `onex validate ...`), may call utilities internally.
- **Testing:** Requires both unit and CLI/integration tests.
- **Examples:**
  - `cli_validate.py` (CLI for validating `.onex` files)
  - `cli_stamp.py` (CLI for stamping metadata)

### Key Rules
- All reusable logic must live in `utils/` and be imported by tools as needed.
- Tools should be thin wrappers over utilities and protocol implementations.
- Utilities do not implement CLI or user-facing logic.
- Document and enforce this distinction in code review and CI.

> **Note:** The URI parser utility is protocol-ready for M1+ and uses canonical Enum and Pydantic model types. See src/omnibase/utils/utils_uri_parser.py, model/model_uri.py, and model/model_enum_metadata.py for details.

> **Note:**
> The `runtime/` directory is the canonical location for shared execution-layer logic, utilities, and internal modules reused by multiple nodes. See the milestone checklist for required moves and refactors. If two or more nodes import the same logic, extract it to `runtime/` and update all documentation and imports accordingly. See the directory layout and naming conventions above for details.

> **Node Testing Standard:**
> All node-local tests, fixtures, and test scaffolds must follow the canonical guidelines in [docs/testing/node_testing_guidelines.md](../testing/node_testing_guidelines.md). This document defines directory structure, import conventions, CLI validation, and CI integration for all ONEX nodes.
