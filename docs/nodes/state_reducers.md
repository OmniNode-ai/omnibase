<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: state_reducers.md
version: 1.0.0
uuid: db247ef1-cf71-45cb-9391-c4811d3e3a39
author: OmniNode Team
created_at: '2025-05-28T12:40:26.769259'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://state_reducers
namespace: markdown://state_reducers
meta_type: tool

<!-- === /OmniNode:Metadata === -->
<file name=0 path=/Volumes/PRO-G40/Code/omnibase/docs/nodes/state_reducers.md># ONEX Node Model: State and Reducers

> **Status:** Canonical Draft
> **Last Updated:** 2025-05-18
> **Purpose:** Define the model for node typing (pure/impure) and structured internal state management via reducers.
> **Audience:** Node authors, runtime developers
> **Series:** Node Architecture  
> **Precedence:** This document is part of the Node Architecture Series and takes precedence over any conflicting documentation.

---

## 🧠 The ONEX Node as a Function: Pure vs Impure

> This section clarifies the distinction between pure and impure node behavior within the conceptual model.

By default, nodes are intended to operate similarly to **pure functions** – deterministic transformations of input state into output state, without side effects that are not explicitly captured in the output state or handled by declared dependencies (like logging utilities). However, the model also supports **impure nodes** through explicit metadata hints and optional embedded reducers, allowing for controlled side effects (e.g., I/O, memory management, retries).

### Node Typing: Pure vs Impure

| Type        | Characteristics                                           | Metadata Hint                  |
|-------------|-----------------------------------------------------------|--------------------------------|
| Pure        | Stateless, deterministic transformation, schema-driven      | Typically `meta_type: tool`    |
| Impure      | May have I/O, external dependencies, manage internal state  | `meta_type: agent`, explicit `reducer:` or side-effect declaration |
| Middleware  | Primarily performs side effects (e.g., logging, caching)    | `meta_type: utility` or specific side-effect declaration |

> **Note:** For a more detailed categorization of node types, see the [Node Typology and Execution Model](./node_typology.md) document, which defines a three-tier model based on state handling, side effects, and execution semantics.

> **Advanced Implementation:** The [Functional Monadic Node Architecture](./functional_monadic_node_architecture.md) provides a more formalized implementation of the reducer pattern through `NodeResult` and state deltas, with explicit monadic composition via the `bind()` method. This approach offers stronger guarantees for context propagation, state delta tracking, and effect management when composing nodes.

---

## 🌀 Reducer-Based Internal State

Some nodes require **local state transitions** or structured side effects beyond a single input/output pass. ONEX supports an embedded reducer model to define internal state machines scoped to a node's runtime instance.

### Reducer Protocol

All reducers must implement:

```python
class ReducerProtocol:
    def initial_state(self) -> dict:
        """Returns the initial state for the reducer."""
        ...

    def dispatch(self, state: dict, action: dict) -> dict:
        """Processes an action and returns the next state."""
        ...
```

### Use Cases

- Retry tracking for idempotent operations
- Local orchestration or branching within a node's logic
- Stepwise generation (e.g., in scaffold nodes that build output over time)
- Buffered/cached state across multiple internal operations or subcalls
- Managing conversational state or interaction history within an agent node
- Handling complex state transitions for long-running tasks

### Example (`reducer` field in .onex - Future)

```yaml
# Proposed addition to node.onex.yaml schema (Future M2+)
reducer: "src/omnibase/reducers/retry_step_reducer.py" # Path to the reducer implementation file
```

---

## 📜 Internal vs External State (Explanation)

- **External State**: Defined via the `state_contract` field in `.onex`, validated against its schema, passed *between* nodes (like function arguments/return values). This is the node's public, shareable data interface.
- **Internal State**: Managed via the node's embedded `reducer` (Future M2+), scoped *to a single node's runtime instance*, not typically validated against a public schema unless explicitly declared (e.g., via a future `reducer_contract`). This is the node's private, mutable state.

This distinction supports **encapsulation** and **composability**—external consumers interact only with the node's declared external state interface, abstracting away internal state complexities.

---

## 🔐 Trust and Reducer Cohesion (Explanation)

Because reducers define dynamic, potentially stateful behavior within a node, they will be integrated into the trust and validation model in future milestones (M2+):
- The `reducer` field in `.onex` will reference the implementation file path.
- Reducer implementation files will be subject to validation (e.g., linting, protocol compliance checks).
- In future releases, reducers may optionally declare a versioned schema for their *internal* state (`reducer_contract`) to aid testing, introspection, and ensure state shape consistency across dispatches.
- Nodes may declare a `reducer_snapshot` policy in `.onex` to specify if and how their reducer state should be periodically saved. This enables resumability without requiring full replay of previous actions and improves planner efficiency.

---

## Notes

* The `reducer` field is planned for formal introduction in a future milestone (M2+). Its semantics (e.g., stateful, interactive, idempotent) will be annotated via metadata to assist orchestration and system reasoning.
* Middleware nodes (`meta_type: utility`) are primarily designed for performing side effects and often leverage internal state managed by a reducer.

---

# State Reducers and Streams Architecture

## Context & Origin

This document captures the foundational thinking behind how OmniNode handles internal state changes, inspired by Redux, functional architecture patterns, and distributed event-driven systems.

The original insight began with:

> "Should we build a reducer-style state system with tools reacting to state changes, instead of just making function calls?"

This rapidly expanded into a full framework for state-driven, reducer-controlled execution inside ONEX.

---

## Core Concepts

### ✅ Reducers as Local State Transformers

* Each subsystem (e.g. metadata, config, prompt, cache) has its own **local reducer**
* Reducers receive actions and update their local state
* Reducers can emit signals (like Redux middleware) to trigger tooling, validation, or external actions

### ✅ Global Reducer Subscription Pattern

* Global reducers can subscribe to the output of local reducers
* This supports derived state calculations, aggregated status, or cross-subsystem effects

### ✅ Asynchronous Gate Control

* Because many operations are async, reducers may wait for conditions before propagating state
* Example: a node dispatch action may require `global_state.ready == true` before continuing

### ✅ Event-Driven Flow

* Actions are not always direct calls; they are state changes
* Middleware or tooling reacts to these transitions (e.g. auto-lint on `file.updated`, or run validator on `metadata.changed`)

---

## Streaming and Signals

### ✅ Signals are the core event primitive

```yaml
type: signal.state.transition
from: idle
to: active
source: node.orchestrator
```

* Signals can be emitted:

  * By reducers
  * By incoming message bus packets (e.g. from JetStream)
  * By external tools or agents

### ✅ Signals can be observed by:

* Other reducers
* Nodes
* Agents
* Composite workflows
* Triggered dispatches (e.g. schedule a validator after metadata updates)

### ✅ Signals carry session, trust, and context metadata

---

## Architecture Design Patterns

### 🔁 Composable Sub-Reducers

* Systems like `metadata` or `tree` may use reducers-per-subpath
* Each reducer only cares about its own scope and emits state snapshots

### 🧩 Modular Black Box Nodes

* Each node is treated as a black box with:

  * Inputs
  * Outputs
  * Metadata
  * Internal reducer state (optional)

### 🔄 Deterministic Execution

* Given the same reducer + input action, the output must be deterministic
* This enables caching, reproducibility, and testing
* Nodes using reducers may optionally persist reducer snapshots to cold storage. This allows the system to restore state without replaying the entire action history, improving performance for long-running or restartable sessions.

---

## Benefits

* Clean separation of state vs effect
* Tools can plug into reducer output instead of monkeypatching logic
* Easier to test reducers in isolation
* Foundation for trust-aware state propagation and replay

---

## Open Questions

* How to snapshot global state for rollback?
* How to unify reducer state with streaming JetStream message data?
* Should reducers be persisted in cold storage (e.g. last known state)?

---

**Status:** Canonical foundational doc for state and reducer architecture. Forms the basis for the node execution planner and session layer. </file>
