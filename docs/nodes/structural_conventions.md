<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: 76e4bea5-7f74-45d5-9a08-ecef0dd96b4f -->
<!-- name: structural_conventions.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:20:05.952225 -->
<!-- last_modified_at: 2025-05-19T16:20:05.952226 -->
<!-- description: Stamped Markdown file: structural_conventions.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: 2bbf73591457e4709e9e39b227519070a796c19b9ebaabae8e6af453f856aa16 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'structural_conventions.md'} -->
<!-- namespace: onex.stamped.structural_conventions.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

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
