<file name=0 path=/Volumes/PRO-G40/Code/omnibase/docs/nodes/caching_and_composite_nodes.md># ONEX Node Architecture: Caching and Composite Nodes

> **Status:** Canonical
> **Series:** Node Architecture
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting or legacy documentation.

## 03 – Caching and Composite Nodes

### Context & Origin

This document describes the ONEX caching layer and the role of composite nodes. This system is built upon the core idea of viewing ONEX nodes as functions and applying functional programming principles like **composition** and **memoization** to build efficient and predictable workflows. This approach was born from the insight:

> "We can create arbitrary parent nodes that cache their subgraphs—caching is just **memoization** applied to composed workflow functions."

---

### Composite Nodes

Composite nodes are a direct application of **function composition**. They allow you to encapsulate a subgraph – a sequence or graph of child nodes (functions) – and treat it as a single, larger node (a single composed function).

#### ✅ Purpose

* **Compose Child Functions:** Wrap multiple child nodes (functions) into a single composite unit (a higher-order function or workflow function).
* **Enable Reuse:** The composite node can be reused as a single dependency in other graphs.
* **Enable Substitution:** Different composite nodes (representing different subgraphs) can fulfill the same `state_contract`, allowing for interchangeable implementations of a workflow.
* **Enable Performance Optimization:** Provide a clear boundary for applying optimizations like caching (memoization) to the entire subgraph's execution.
* **Define Interface:** Provide a single entry/exit point (`state_contract`) for the potentially complex subgraph encapsulated within.

#### ✅ Structure

A composite node is declared in its `node.onex.yaml` metadata file using `meta_type: composite`. It explicitly lists its child nodes (functions) that form the subgraph under a `subgraph` key.

```yaml
# node.onex.yaml (example for a composite node)
schema_version: "0.1.0"
name: "my_composed_workflow"
version: "1.0.0"
uuid: "..." # unique identifier
author: "..."
description: "A composite node wrapping a data validation and processing subgraph."
meta_type: "composite" # Declares this is a composite node
state_contract: "state_contract://composed_workflow_contract.json" # Defines the input/output for the entire subgraph
dependencies:
  - tool://core.orchestrator@latest # Composite nodes implicitly depend on the orchestrator
  # ... other dependencies needed by the composite node itself (less common)
subgraph: # The list of child nodes/functions in the subgraph
  - tool://data.loader@1.0.0
  - validator://data.schema_checker@2.0.0
  - tool://data.processor@1.5.0
  # Child nodes listed here will be executed as part of this composite node's 'function call'
# Other standard .onex fields follow...
```

#### ✅ Execution Flow (Conceptual)

* The composite node, representing a composed workflow function, is resolved as part of the larger execution graph.
* When the composite node's "function" is called (its inputs are ready), the orchestrator plans and executes the child nodes within its `subgraph` as an isolated unit.
* The output of the composite node's "function call" is the final state produced by the subgraph's execution.
* The parent node (the composite node itself) may then apply strategies like memoization to this output or emit signals based on the subgraph's completion status.

---

### Caching Layer

The caching layer provides **memoization** for ONEX nodes and composite subgraphs. It stores the results of previous node "function calls" based on their inputs and configuration, allowing for fast retrieval instead of re-executing the node's logic.

#### ✅ Cache Between Nodes

The cache stores information about completed node executions, effectively recording the output for a given function call:

* **Inputs:** A hash or identifier representing the input `state_contract` passed to the node.
* **Node ID + Version:** Identifies the specific function (node) that was executed.
* **Configuration Hash:** A hash or identifier representing the node's static configuration (`.onex` metadata, potentially other config files).
* **Output + Performance Trace:** The resulting output `state_contract` and metadata about the execution (duration, resource usage, etc.).

The cache key uniquely identifies a specific execution instance.

```yaml
# Conceptual cache key structure
cache_key:
  node_uri: tool://scaffold.tree_builder@1.0.0 # Identifies the function (node ID + version)
  input_hash: sha256:abcdef123... # Hash of the input state
  config_hash: sha256:1234567... # Hash of the node's static configuration
  # For Impure nodes, the key might include other factors influencing output,
  # or caching might be restricted.
```

#### ✅ Cache Policy Block

Cache behavior is controlled via a `cache` policy block within the node's `.onex` metadata. This defines the memoization strategy for that specific node's function.

```yaml
# Example cache policy in node.onex.yaml
cache:
  enabled: true        # Whether memoization is active for this node/function
  strategy: memoize    # Caching strategy (e.g., memoize, passthrough, immutable)
  scope: node          # Scope of the cache key (node-specific, composite-specific, global)
  ttl_seconds: 3600    # How long the cache entry is valid
  # Future additions could include:
  # consistency: strict | eventual # Consistency model for distributed caches
  # invalidation_signals: [...] # Signals that invalidate the cache
  # state_fields_ignored_in_cache_key: [...] # For Impure/stateful nodes, ignore certain volatile input fields in key
```

A new optional field `memoization_tier` may be specified to control how deep memoization is applied, especially for composite nodes:

```yaml
cache:
  enabled: true
  strategy: memoize
  scope: composite
  memoization_tier: deep  # 'shallow' caches only composite input/output; 'deep' caches the entire subgraph
```

* `shallow`: caches only the outer composite node’s input/output.
* `deep`: recursively caches each subgraph node's execution, using `trace_hash`-based keys and structural equivalence.

When set to `deep`, the planner uses recursive fingerprinting to store and match prior executions of identical subgraphs, even across different composite nodes.

#### ✅ Cold Context as Long-Term Cache

All cached outputs are stored persistently and constitute the "cold context." This long-term storage of past function calls and their results:

* Acts as a historical record of executions.
* Can be queried and inspected independently.
* Supports replaying past workflows using cached results.
* Entries are versioned (tied to the node version) and governed by TTL policies.

When `memoization_tier: deep` is active, the cold context includes not only composite node results but also internal subgraph traces. These are identified via deterministic `trace_hash` keys that account for node inputs, config, and outputs, enabling subgraph-level reuse and equivalence detection. This supports advanced optimization techniques, including reuse of previously cached function paths across different workflows or composite boundaries.

---

### Benefits of Caching (Memoization)

Applying memoization to node functions and composite workflows yields significant benefits:

* **Prevents Redundant Computation:** Avoids re-executing expensive node functions with identical inputs.
* **Enables Deterministic Workflow Testing:** Caching allows for reliable replay of subgraph execution during testing.
* **Accelerates Graph Replay:** Quickly reconstructs execution outcomes using cached results.
* **Reduces Resource Costs:** Lowers computation, model API calls, and other resource expenditures.
* **Supports Offline/Disconnected Operation:** Workflows can potentially execute using cached results when dependencies are unavailable.

---

### Advanced Use Cases

#### 🔁 Tournament Caching (for Functional Variants)

* Different node *implementations* (variants with the same `state_contract` and often `base_class`) can compete.
* Execution performance and metadata for each variant's function call are cached.
* A winning variant can be promoted or selected based on criteria like hash + performance score, enabling A/B testing of node function implementations.

#### ♻️ Smart Cache Invalidation

* Invalidate memoized results automatically when the node's function definition changes (new node version, config change).
* Invalidate or revalidate cache entries based on schema upgrades, external signals, or declared dependencies' changes.

#### 🧠 Self-Aware Nodes (Functions Querying Past Results)

* Nodes (functions) can query their own cache history (past calls and results) via the registry or execution context.
* Agents or stateful nodes (using reducers) can review past performance or results to inform their current execution path or state transitions. This is like a function having memory of its previous invocations.

---

### Status

This document is the canonical reference for the ONEX caching system, framing it as memoization applied to the node-as-a-function model. Composite nodes define the default boundary for applying caching strategies, enabling reuse, test scaffolding, and latency optimization across composed workflows. </file>