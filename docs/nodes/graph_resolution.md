# ONEX Node Architecture: Graph Resolution and Execution Planning

> **Status:** Canonical
> **Series:** Node Architecture
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting or legacy documentation.

## 02 – Graph Resolution and Execution Planning

### Context & Origin

This document defines how the ONEX runtime (specifically the Graph Planner and Execution Resolver) resolves dependency graphs of executable nodes. Building on the concept of [Nodes as Functions](docs/nodes/index.md), this process determines "which node functions can be called, in what order, and under what constraints, based on their declared interfaces and dependencies."

It expands the runtime's core loop: determining "what set of function calls can run, in what valid sequence or parallel batches, and under what conditions."

This emerged from the insight:

> "The core skill of the entire ONEX system is **orchestrating function calls** by resolving the dependency graph."

---

### Core Principles

The principles governing graph resolution and execution planning are rooted in the functional nature of ONEX nodes:

#### ✅ The Execution Graph is a Directed Acyclic Graph (DAG)

* **Nodes are Vertices:** Each vertex in the graph represents a specific **ONEX node function** (identified by its URI: `<type>://<namespace>@<version>`).
* **Edges Represent Dependencies:** Edges represent the flow of data (output `state_contract` of one node providing input `state_contract` to another) or control flow constraints (signals, explicit ordering, trust thresholds) between node function calls.

#### ✅ Planning = Contract-Driven Topological Sort

* The process of generating an execution plan involves ordering the node function calls.
* **Resolve Node Function Dependencies:** Nodes are resolved based on their declared `dependencies` and `base_class` links, and their `state_contract` input requirements.
* **Validate Contract Satisfaction:** The planner ensures that the required input `state_contract` for a node function call is satisfied by the output `state_contract` of preceding node function calls in the graph.
* **Use Metadata for Constraints:** Node metadata (`meta_type`, `lifecycle`, `trust_score_stub`, caching policies, future reducer semantics) is used to enforce constraints on *when* and *how* a node function call can be dispatched.

---

### Graph Planner Responsibilities

The Graph Planner acts as the **workflow orchestrator** or **function graph scheduler**. Its primary responsibilities are to analyze the declared relationships between node functions and generate a valid sequence (or set of parallel batches) of function calls.

#### 1. **Build the Execution Graph (Set of Function Calls)**

* Collect metadata (the function definitions and their interfaces) for all relevant nodes referenced in the workflow (`.tree`, direct dependencies, etc.).
* Resolve dependencies by matching declared `dependencies` and required `state_contract` inputs with available node function outputs.
* Include composite nodes and variant nodes as potential functions to call or structures containing child functions.

#### 2. **Topological Sort and Prune**

* Order the node function calls based on data dependencies, creating a valid topological sort of the graph.
* Eliminate or defer branches of function calls whose input requirements cannot be satisfied.
* Identify and short-circuit cycles or redundant paths in the function call graph.
* Defer node function calls gated by missing or failed outputs from prerequisite calls.

#### 3. **Batch Dispatchable Nodes (Schedule Function Calls)**

* Identify node function calls that have all their inputs satisfied and constraints met.
* Group independent function calls for potential parallel execution based on configuration (`run_mode`), estimated cost, or priority (`trust_score_stub`).
* Dispatch these batched function calls to the Execution Resolver.
* Emit signals per node function call or batch completion (`signal.node.dispatch`, `signal.node.result`).

#### 4. **Track Execution State**

* Record the state of each node function call within the current graph execution context.
* Track:
    * Start/finish time of the function call
    * Success/failure result and any emitted errors
    * Actual output `state_contract` produced
    * Updates to trust deltas or emitted signals

---

### Caching + Subgraph Encapsulation (Memoization for Composed Functions)

The caching layer provides **memoization** for node functions, particularly leveraged by composite nodes.

#### ✅ Composite Nodes

* Composite nodes represent **composed workflow functions**.
* They encapsulate a subgraph of child node functions and provide a single interface for executing that subgraph.
* The composite node acts as a boundary for applying **memoization** to the entire subgraph's execution.

#### ✅ Cache Key = Function Call Signature

The cache key uniquely identifies a specific *call* to a node function or composite function based on its inputs and definition.

```yaml
# Conceptual cache key structure
cache_key:
  node_uri: tool://scaffold.pipeline@0.2.4 # Identifies the function being called
  input_hash: sha256:abc123 # Hash of the input state_contract (function arguments)
  config_hash: sha256:def456 # Hash of the node's static config (.onex, etc. - function definition)
  # For Impure/stateful nodes, cache key might need enhancement or caching may be limited per policy.
```

---

### Recursive Flattening for GraphQL

ONEX supports recursive graphs of node functions internally. For interfaces like GraphQL, which typically operate on simpler structures, the graph resolver provides flattened representations:

* Recursive subgraph structures are returned as arrays or JSON blobs containing links (`node_uri`) to child function calls.
* External tools can then traverse these links to explore the full, underlying recursive function graph.

---

### Streaming Graph Execution (Streaming Function Call Events)

The execution graph's progress and outcomes are streamed via messaging systems. This stream consists of events related to node function calls:

* Streamed via: JetStream (core), gRPC or WebSocket bridges (optional).
* Messages emitted:
    * `signal.node.dispatch`: Indicates a node function call is starting.
    * `signal.node.result`: Contains the output `state_contract` and status of a completed node function call.
    * `signal.graph.completed`: Indicates the entire composed workflow function (graph) has finished executing.

---

### Future Optimizations (for Function Graph Orchestration)

* **Subgraph Memoization & Reuse:** Advanced caching techniques applied to frequently executed composite functions (subgraphs).
* **Cost-Aware Graph Shaping:** Planner considers the cost of node function calls when determining execution paths or variant selection.
* **Parallel Job Queue per Execution Ring:** Optimized dispatching of batched function calls to execution resources.
* **Agent-Driven Graph Mutation + Rerun:** Agents or stateful nodes (via reducers) can dynamically modify the planned function call graph based on intermediate results and request re-planning/re-execution of parts of the graph.
* **Cold Snapshot Replay:** Ability to reconstruct and replay past workflow executions directly from the cached history of function calls and their results.

---

**Status:** Canonical definition of the ONEX graph planner and execution resolver. It frames the process as orchestrating a graph of node functions based on their interfaces and metadata, forming the basis for the run loop, stream dispatchers, and future agent-integrated planning layers.

--- 