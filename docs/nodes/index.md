# Node Architecture Series

> **Status:** Canonical
> **Precedence:** The following documents are part of the Node Architecture Series and take precedence over any conflicting or legacy documentation. They define the core execution, planning, and trust model for OmniNode/ONEX.

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

---

> For any architectural, execution, or node-related question, these documents are the source of truth. If a conflict arises with other documentation, the Node Architecture Series prevails.

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