# ONEX Node Architecture Series

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Comprehensive guide to ONEX node architecture, execution patterns, and design principles  
> **Audience:** Node developers, system architects, contributors  

---

## Introduction

The Node Architecture Series captures the canonical, foundational design and execution patterns for ONEX. These documents define the reducer/event-driven state model, contract-first node philosophy, graph resolution, caching, streaming, prompt/model integration, performance memory, and the architectural distinction from GraphQL. They are the authoritative reference for all node and execution-related behavior in the system.

---

## Table of Contents

1. **[State Reducers and Streams Architecture](./state_reducers.md)**  
   _Reducer/event-driven state, signals, and streaming as the foundation for node execution and session management._

2. **[Node Contracts and Metadata Structure](./node_contracts.md)**  
   _Contract-first, metadata-driven node design; input/output contracts, performance memory, and trust._

3. **[Sessions and Streaming Architecture](./sessions_and_streaming.md)**  
   _Session lifecycle, JetStream/gRPC/WebSocket streaming, trust-aware multiplexed execution._

4. **[Node Typology and Execution Model](./node_typology.md)**  
   _Tiered model for node categorization based on state handling, side effects, and execution semantics._

5. **[Monadic Node Core](./architecture-node-monadic-core.md)** - Core monadic principles and interfaces
6. **[Node Composition](../architecture-node-composition.md)** - Composition patterns and execution models  
   _Monadic approach to node composition with explicit state modeling, context propagation, and effect tracking._

6. **[Structural Conventions](./structural_conventions.md)**  
   _Standard directory structure, file layout, discovery mechanisms, and module typing conventions._

7. **[Protocol Definitions](./protocol_definitions.md)**  
   _Foundational protocol interfaces that core components and nodes must adhere to._

8. **[Templates and Scaffolding](./templates_scaffolding.md)**  
   _Role and structure of canonical templates used for scaffolding new nodes and components._

9. **[Developer Guide](./developer_guide.md)**  
   _Development conventions, testing philosophy, process guidelines, and contribution best practices._

---

> For any architectural, execution, or node-related question, these documents are the source of truth. If a conflict arises with other documentation, the Node Architecture Series prevails.

---

## ONEX Node Model: Overview

### What is an ONEX Node?

An ONEX node is a self-contained, declarative, executable unit defined by a `.onex` metadata file. It can be conceptually viewed as a **function** with a formal, metadata-defined interface. Nodes are:

- Discoverable via `.tree` or registry
- Executable via a defined `entrypoint`
- Validated against schemas and CI rules
- Composable via `dependencies`, `protocols_supported`, and `base_class`
- Optionally stateful, managing internal state via a declared reducer
- Rated via a trust score stub
- Interoperable with ONEX runtimes and agents

### The ONEX Node as a Function: Conceptual Model

An ONEX node is fundamentally a **function** with a well-defined interface described by its `.onex` metadata and associated schemas. By default, nodes are intended to operate similarly to **pure functions** – deterministic transformations of input state into output state, without side effects. However, the model also supports **impure nodes** through explicit metadata hints and optional embedded reducers, allowing for controlled side effects (e.g., I/O, logging, memory management, retries).

#### Core Principles

- **Input/Output is explicit**: Defined via `state_contract`
- **Execution is declarative**: Entrypoints point to callable scripts or modules
- **Purity is preferred**: Nodes are functional by default where feasible
- **State is scoped**: Persistent/impure state is isolated and declared
- **Metadata drives everything**: All behavior is declared in `.onex`

#### Node = Function (Redux-Like)

At a conceptual level, an ONEX node is:

```
(input_state: dict) -> (output_state: dict)
```

This transformation is performed by the code at the `entrypoint`. The function's behavior is optionally enhanced with:

- Internal state managed by a `reducer`
- Composability links (`dependencies`, `base_class`, `consumes`/`produces`)
- Trust/validation metadata (`trust_score_stub`, `hash`, etc.)
- CI and validation rules (`.tree`, `schema_version`, validation enforcement)
- Defined Execution Environment (`entrypoint`, `runtime_language_hint`)

---

## ONEX v0.1 Canonical Node Naming and Structure Standard

### Node Definition
- Every node is a composable execution unit: smallest independently testable, addressable, and registrable unit of functionality

### Directory Naming
- Pattern: `{object_type}.{domain}.{name}` (e.g., `validator.check.namegen`)
- Directory name is the canonical registry and execution name

### Required Files per Node

| File            | Required | Description                              |
| --------------- | -------- | ---------------------------------------- |
| `metadata.yaml` | ✅        | Contains ONEX metadata and contract info |
| `code.py`       | ✅        | Main implementation logic                |
| `test.py`       | ✅        | Validator or output check                |
| `schema.py`     | ⬜        | Pydantic contracts (optional)            |
| `README.md`     | ⬜        | Local usage docs (optional)              |

- All filenames must be lowercase. No camelCase or underscores.

### Directory Layout
- Nodes live under `src/nodes/` (e.g., `src/nodes/validator.check.namegen/`)
- Node directory name is the primary key, not the folder path

### Node Discovery
- `.tree` file lists all known nodes for CI, CLI, and agent discovery

### Shared Logic
- Local-only helpers allowed within node dir
- Shared library modules go in `shared/`, not versioned with node
- Promote to node if testable/trust-rated
- Forbidden: symlinks, cross-node imports, shared logic in `nodes/` unless a node

### Optional Extensions
- `mocks/`, `variants/`, `hooks/` allowed, declared in `metadata.yaml` under `auxiliary:`

### Trust and Enforcement
- All nodes must pass `onex lint`
- Metadata must define lifecycle
- Node names must resolve to valid registry entries
- CI enforces contract correctness and code coverage

### Forbidden Patterns
- No camelCase or uppercase in filenames
- No nesting of node directories
- No dynamic entrypoint or wildcard imports
- No direct `getLogger()` — use DI

### Summary Table

| ✅ Feature             | 📌 Reason                                       |
| --------------------- | ----------------------------------------------- |
| Node = execution unit | Enforces contract, version, registry discipline |
| Canonical ID format   | Enables deterministic execution + discovery     |
| Fixed file names      | Keeps tooling and CLI predictable               |
| Extensible subdirs    | Supports real-world complexity cleanly          |
| Metadata-first design | Fully agent-compatible and audit-friendly       |
| Shared logic external | Promotes reuse and avoids duplication           |

> **Note:** The term "tuple" is deprecated in favor of "node." All references to "tuples" in prior documentation, filenames, or `.tree` structures should be interpreted as referring to ONEX nodes. Future naming, scaffolding, and enforcement should use the term "node" exclusively.

---

## References

- [Developer Guide](./developer_guide.md) - Development conventions and best practices
- [Structural Conventions](./structural_conventions.md) - Directory structure and file layout standards
- [Protocol Definitions](./protocol_definitions.md) - Core protocol interfaces
- [Node Contracts](./node_contracts.md) - Contract-first node design principles

---

**Note:** This series provides the foundational architecture for ONEX nodes. All node development should follow these principles and patterns to ensure consistency and interoperability within the ONEX ecosystem. 