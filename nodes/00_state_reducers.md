## 00 – State Reducers and Streams Architecture

### Context & Origin

This document captures the foundational thinking behind how OmniNode handles internal state changes, inspired by Redux, functional architecture patterns, and distributed event-driven systems.

The original insight began with:

> "Should we build a reducer-style state system with tools reacting to state changes, instead of just making function calls?"

This rapidly expanded into a full framework for state-driven, reducer-controlled execution inside ONEX.

---

### Core Concepts

#### ✅ Reducers as Local State Transformers

* Each subsystem (e.g. metadata, config, prompt, cache) has its own **local reducer**
* Reducers receive actions and update their local state
* Reducers can emit signals (like Redux middleware) to trigger tooling, validation, or external actions

#### ✅ Global Reducer Subscription Pattern

* Global reducers can subscribe to the output of local reducers
* This supports derived state calculations, aggregated status, or cross-subsystem effects

#### ✅ Asynchronous Gate Control

* Because many operations are async, reducers may wait for conditions before propagating state
* Example: a node dispatch action may require `global_state.ready == true` before continuing

#### ✅ Event-Driven Flow

* Actions are not always direct calls; they are state changes
* Middleware or tooling reacts to these transitions (e.g. auto-lint on `file.updated`, or run validator on `metadata.changed`)

---

### Streaming and Signals

#### ✅ Signals are the core event primitive

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

#### ✅ Signals can be observed by:

* Other reducers
* Nodes
* Agents
* Composite workflows
* Triggered dispatches (e.g. schedule a validator after metadata updates)

#### ✅ Signals carry session, trust, and context metadata

---

### Architecture Design Patterns

#### 🔁 Composable Sub-Reducers

* Systems like `metadata` or `tree` may use reducers-per-subpath
* Each reducer only cares about its own scope and emits state snapshots

#### 🧩 Modular Black Box Nodes

* Each node is treated as a black box with:

  * Inputs
  * Outputs
  * Metadata
  * Internal reducer state (optional)

#### 🔄 Deterministic Execution

* Given the same reducer + input action, the output must be deterministic
* This enables caching, reproducibility, and testing

---

### Benefits

* Clean separation of state vs effect
* Tools can plug into reducer output instead of monkeypatching logic
* Easier to test reducers in isolation
* Foundation for trust-aware state propagation and replay

---

### Open Questions

* How to snapshot global state for rollback?
* How to unify reducer state with streaming JetStream message data?
* Should reducers be persisted in cold storage (e.g. last known state)?

---

**Status:** Canonical foundational doc for state and reducer architecture. Forms the basis for the node execution planner and session layer.
