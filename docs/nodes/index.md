<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: index.md
version: 1.0.0
uuid: 70f3c1cf-c5a5-4421-a12d-e9094410cf68
author: OmniNode Team
created_at: 2025-05-28T12:40:26.680715
last_modified_at: 2025-05-28T17:20:04.552320
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 9624ec2fa438045c6c55ee1831ee386397a15f3ce6a42a99be8cadf9fef68726
entrypoint: python@index.md
runtime_language_hint: python>=3.11
namespace: omnibase.stamped.index
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Node Architecture Series

> **Status:** Canonical
> **Precedence:** The following documents are part of the Node Architecture Series and take precedence over any conflicting documentation. They define the core execution, planning, and trust model for OmniNode/ONEX.

---

## Introduction

The Node Architecture Series captures the canonical, foundational design and execution patterns for OmniNode (ONEX). These documents define the reducer/event-driven state model, contract-first node philosophy, graph resolution, caching, streaming, prompt/model integration, performance memory, and the architectural distinction from GraphQL. They are the authoritative reference for all node and execution-related behavior in the system.

---

## Table of Contents

1. **[State Reducers and Streams Architecture](./state_reducers.md)**  
   _Reducer/event-driven state, signals, and streaming as the foundation for node execution and session management._
2. **[Node Contracts and Metadata Structure](./node_contracts.md)**  
   _Contract-first, metadata-driven node design; input/output contracts, performance memory, and trust._
3. **[Graph Resolution and Execution Planning](./graph_resolution.md)**  
   _DAG-based execution planning, contract-driven topo sort, trust constraints, and streaming execution._
4. **[Caching and Composite Nodes](./caching_and_composite_nodes.md)**  
   _Composite nodes, subgraph encapsulation, cache keys, and advanced caching strategies._
5. **[Sessions and Streaming Architecture](./sessions_and_streaming.md)**  
   _Session lifecycle, JetStream/gRPC/WebSocket streaming, trust-aware multiplexed execution._
6. **[Prompt Blocks and Model Nodes](./prompt_blocks_and_model_nodes.md)**  
   _Prompts as first-class input blocks, model nodes as transformers, prompt contracts, and agent planning._
7. **[Performance Memory and Cost-Aware Execution](./performance_memory_and_cost.md)**  
   _Performance tracking, trace hashes, node evolution, trust/reputation, and cost-optimized planning._
8. **[GraphQL vs ONEX: Declarative Execution vs Declarative Query](./graphql_vs_onex.md)**  
   _Comparison of ONEX's contract-driven execution model with GraphQL's query paradigm._
9. **[Node Typology and Execution Model](./node_typology.md)**  
   _Tiered model for node categorization based on state handling, side effects, and execution semantics._
10. **[Functional Monadic Node Architecture](./functional_monadic_node_architecture.md)**  
    _Monadic approach to node composition with explicit state modeling, context propagation, and effect tracking._
11. **[Structural Conventions](./structural_conventions.md)**  
    _Standard directory structure, file layout, discovery mechanisms, and module typing conventions._
12. **[Protocol Definitions](./protocol_definitions.md)**  
    _Foundational protocol interfaces that core components and nodes must adhere to._
13. **[Templates and Scaffolding](./templates_scaffolding.md)**  
    _Role and structure of canonical templates used for scaffolding new nodes and components._
14. **[Developer Guide](./developer_guide.md)**  
    _Development conventions, testing philosophy, process guidelines, and contribution best practices._
15. **[Future Work and Roadmap](./future_roadmap.md)**  
    _Proposed future features, enhancements, and roadmap items for the ONEX node model beyond M0 and M1._

---

> For any architectural, execution, or node-related question, these documents are the source of truth. If a conflict arises with other documentation, the Node Architecture Series prevails.

# ONEX Node Model: Overview

> **Status:** Canonical Draft
> **Last Updated:** 2025-05-18
> **Purpose:** Provide a high-level conceptual overview of ONEX nodes, defining their fundamental nature and core principles within the system.
> **Audience:** All ONEX contributors and users

---

## 🧱 What is an ONEX Node?

An ONEX node is a self-contained, declarative, executable unit defined by a `.onex` metadata file. It can be conceptually viewed as a **function** with a formal, metadata-defined interface. Nodes are:
- Discoverable via `.tree` or registry
- Executable via a defined `entrypoint`
- Validated against schemas and CI rules
- Composable via `dependencies`, `protocols_supported`, and `base_class`
- Optionally stateful, managing internal state via a declared reducer
- Rated via a trust score stub
- Interoperable with ONEX runtimes and agents

---

## 🧠 The ONEX Node as a Function: Conceptual Model

> This section describes the conceptual model of an ONEX node as a declarative function, providing context for its design and behavior.

An ONEX node is fundamentally a **function** with a well-defined interface described by its `.onex` metadata and associated schemas. By default, nodes are intended to operate similarly to **pure functions** – deterministic transformations of input state into output state, without side effects. However, the model also supports **impure nodes** through explicit metadata hints and optional embedded reducers, allowing for controlled side effects (e.g., I/O, logging, memory management, retries).

### Core Principles

- **Input/Output is explicit**: Defined via `state_contract`
- **Execution is declarative**: Entrypoints point to callable scripts or modules
- **Purity is preferred**: Nodes are functional by default where feasible
- **State is scoped**: Persistent/impure state is isolated and declared
- **Metadata drives everything**: All behavior is declared in `.onex`

### Node = Function (Redux-Like)

At a conceptual level, an ONEX node is:

```
(input_state: dict) -> (output_state: dict)
```

This transformation is performed by the code at the `entrypoint`. The function's behavior is optionally enhanced with:

- Internal state managed by a `reducer` (Future M2+)
- Composability links (`dependencies`, `base_class`, future `consumes`/`produces`)
- Trust/validation metadata (`trust_score_stub`, `hash`, etc.)
- CI and validation rules (`.tree`, `schema_version`, validation enforcement)
- Defined Execution Environment (`entrypoint`, `runtime_language_hint`)

---

## Notes

* Validators (`meta_type: validator`) are intended to become fully executable ONEX nodes in Milestone 2, aligning with the "Node as a Function" model.

---

# ONEX v0.1 Canonical Node Naming and Structure Standard

> **This section is canonical and supersedes any conflicting details below.**

## Node Definition
- Every node is a composable execution unit: smallest independently testable, addressable, and registrable unit of functionality.

## Directory Naming
- Pattern: `{object_type}.{domain}.{name}` (e.g., `validator.check.namegen`)
- Directory name is the canonical registry and execution name.

## Required Files per Node
| File            | Required | Description                              |
| --------------- | -------- | ---------------------------------------- |
| `metadata.yaml` | ✅        | Contains ONEX metadata and contract info |
| `code.py`       | ✅        | Main implementation logic                |
| `test.py`       | ✅        | Validator or output check                |
| `schema.py`     | ⬜        | Pydantic contracts (optional)            |
| `README.md`     | ⬜        | Local usage docs (optional)              |
- All filenames must be lowercase. No camelCase or underscores.

## Directory Layout
- Nodes live under `src/nodes/` (e.g., `src/nodes/validator.check.namegen/`)
- Node directory name is the primary key, not the folder path.

## Node Discovery
- `.tree` file lists all known nodes for CI, CLI, and agent discovery.

## Shared Logic
- Local-only helpers allowed within node dir
- Shared library modules go in `shared/`, not versioned with node
- Promote to node if testable/trust-rated
- Forbidden: symlinks, cross-node imports, shared logic in `nodes/` unless a node

## Optional Extensions
- `mocks/`, `variants/`, `hooks/` allowed, declared in `metadata.yaml` under `auxiliary:`

## Trust and Enforcement
- All nodes must pass `onex lint`
- Metadata must define lifecycle
- Node names must resolve to valid registry entries
- CI enforces contract correctness and code coverage

## Forbidden Patterns
- No camelCase or uppercase in filenames
- No nesting of node directories
- No dynamic entrypoint or wildcard imports
- No direct `getLogger()` — use DI

## Summary Table
| ✅ Feature             | 📌 Reason                                       |
| --------------------- | ----------------------------------------------- |
| Node = execution unit | Enforces contract, version, registry discipline |
| Canonical ID format   | Enables deterministic execution + discovery     |
| Fixed file names      | Keeps tooling and CLI predictable               |
| Extensible subdirs    | Supports real-world complexity cleanly          |
| Metadata-first design | Fully agent-compatible and audit-friendly       |
| Shared logic external | Promotes reuse and avoids duplication           |

> **Addendum:** The term "tuple" is deprecated in favor of "node." All references to "tuples" in prior documentation, filenames, or `.tree` structures should be interpreted as referring to ONEX nodes. Future naming, scaffolding, and enforcement should use the term "node" exclusively.
