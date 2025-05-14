## 02 – Graph Resolution and Execution Planning

### Context & Origin

This document defines how ONEX resolves dependency graphs of executable nodes based on contract satisfaction, trust metadata, and execution state. It expands the runtime's core loop: determining "what can run, in what order, and under what constraints."

This emerged from the insight:

> "The core skill of the entire ONEX system is graph resolution."

---

### Core Principles

#### ✅ The Execution Graph is a DAG

* Nodes are vertices
* Edges represent:

  * Contract dependencies (input → output)
  * Signals or state transitions
  * Contextual gating or trust constraints

#### ✅ Planning = Contract-Driven Topo Sort

* Resolve nodes in dependency order
* Validate contract satisfaction before dispatch
* Use metadata to enforce input/output expectations

---

### Graph Planner Responsibilities

#### 1. **Build the Execution Graph**

* Collect metadata for all relevant nodes
* Resolve dependencies based on `input_contract`
* Include composite and variant nodes

#### 2. **Topo Sort and Prune**

* Eliminate unsatisfied branches
* Short-circuit cycles or redundant paths
* Defer nodes gated by missing or failed outputs

#### 3. **Batch Dispatchable Nodes**

* Identify parallel execution opportunities
* Dispatch based on `run_mode`, cost, or trust priority
* Emit signals per node or batch

#### 4. **Track Execution State**

* Record:

  * Start/finish time
  * Success/failure result
  * Output contracts
  * Trust deltas or signal emissions

---

### Caching + Subgraph Encapsulation

#### ✅ Composite Nodes

* Allow encapsulating subgraphs in a parent node
* Parent node forms caching boundary
* Useful for:

  * Pipeline reuse
  * Latency or cost-aware skipping
  * Parallel graph partitioning

#### ✅ Cache Key = Signature

```yaml
cache_key:
  node: scaffold.pipeline
  input_hash: sha256:abc123
  config_hash: sha256:def456
  version: 0.1.2
```

---

### Recursive Flattening for GraphQL

* ONEX supports recursive graphs internally
* GraphQL interface flattens recursion:

  * Subgraphs returned as arrays or JSON blobs
  * External tools can traverse via `node_id` links

---

### Streaming Graph Execution

* Execution graph is streamed via:

  * JetStream (core)
  * gRPC or WebSocket bridges (optional)
* Messages emitted:

  * `signal.node.dispatch`
  * `signal.node.result`
  * `signal.graph.completed`

---

### Future Optimizations

* Subgraph caching + reuse
* Cost-aware graph shaping
* Parallel job queue per execution ring
* Agent-driven graph mutation + rerun
* Cold snapshot replay from context vault

---

**Status:** Canonical definition of the ONEX graph planner and execution resolver. Forms the basis for the run loop, stream dispatchers, and future agent-integrated planning layers.
