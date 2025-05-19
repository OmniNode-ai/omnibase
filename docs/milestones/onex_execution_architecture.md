<!-- === OmniNode:Metadata ===
<!-- metadata_version: 0.1.0 -->
<!-- schema_version: 1.1.0 -->
<!-- uuid: 13a73b1a-b975-468b-8feb-83fc63764720 -->
<!-- name: onex_execution_architecture.md -->
<!-- version: 1.0.0 -->
<!-- author: OmniNode Team -->
<!-- created_at: 2025-05-19T16:19:52.918924 -->
<!-- last_modified_at: 2025-05-19T16:19:52.918927 -->
<!-- description: Stamped Markdown file: onex_execution_architecture.md -->
<!-- state_contract: none -->
<!-- lifecycle: active -->
<!-- hash: 4d4e4d30180a30420f92117242f162287de8faa0fe11e283b2e8f250f39875b9 -->
<!-- entrypoint: {'type': 'markdown', 'target': 'onex_execution_architecture.md'} -->
<!-- namespace: onex.stamped.onex_execution_architecture.md -->
<!-- meta_type: tool -->
=== /OmniNode:Metadata === -->

## ONEX Execution Architecture Milestone Roadmap

This document outlines the phased plan for implementing the ONEX Execution Architecture — the core protocol and runtime model behind OmniNode's declarative, testable, and trust-scored node system. It defines four key milestones, starting with schema and protocol design and culminating in agent-triggered, trust-scored node execution.

---

### 🧭 Overview: MVP Goal

> **The MVP is a node that builds a node.**
>
> Specifically: a fully validated ONEX node that, when executed, generates a new ONEX node using the defined protocols, schema, and runtime environment.

This recursive capability demonstrates the maturity of the ONEX execution loop and confirms that the protocol and tooling are expressive, reliable, and self-extensible.

---

### 🌀 Implementation Flow

```
M1 → Schema + CI
   ↓
M2 → Runtime loads & executes M1-compliant node
   ↓
M2 → Scaffold node builds new ONEX node using M1 protocols
   ↘︎
M1 schema validates new node → CI
```

---

## 🔹 Milestone 1: Protocol + Metadata + Validation (MVP Schema)

### 🎯 Goal

Define and lock the base schema format and validation protocol for ONEX node metadata and lifecycle enforcement.

### 📦 Deliverables

* `onex_node.yaml`: canonical schema for ONEX metadata block
* `.tree`: directory discovery format referencing `.onex` metadata
* CI enforcement: validate schema/hash/lifecycle/state fields
* `validate_metadata.py` script with CI hook integration
* `generate_onex_node.py` for scaffolded metadata creation
* Docstring auto-formatter for schemas (CLI + docs)
* `state_contract.schema.json`: defines the structure and validation rules for state blocks

### 🧠 Design Considerations

* Lifecycle stages: `draft`, `review`, `active`, `deprecated`
* Metadata versioning: support stubs for future schema evolution
* Discovery metadata: tag, group, namespace, trust stub
* CI safety: all `.onex` files must validate + hash lock
* Docs: link to canonical field descriptions and lifecycle contracts
* State contract schema must be referenced or embedded in `.onex` metadata

### ✅ Completion Criteria

* All `.onex` metadata files pass schema validation in CI
* Scaffold generator produces valid metadata stubs
* Metadata includes version, lifecycle, trust stub, and `state_contract` stub
* `.tree` files reference `.onex` metadata correctly

### ⚠️ Risks & Mitigations

* **Risk**: Schema evolution incompatible with existing nodes
  **Mitigation**: Embed `version` field, support deprecation tags
* **Risk**: CI does not enforce all constraints
  **Mitigation**: Hash-based enforcement, lifecycle required

### 📊 Metrics

* 100% `.onex` files validate in CI
* 100% `.tree` files reference valid `.onex`
* CI runs enforce schema hash, lifecycle, and trust stub presence

### 🧑‍💻 Ownership

* Milestone Owner: Jonah Gray
* Reviewer: Gemini / Cursor agent

### 🔗 References

* [docs/standards/metadata\_block.md](../docs/standards/metadata_block.md)
* [docs/standards/lifecycle.md](../docs/standards/lifecycle.md)
* [docs/validation/README.md](../docs/validation/README.md)
* [docs/standards/state_contract.md](../docs/standards/state_contract.md)

---

## 🔹 Milestone 2: Runtime Loader + Execution Contract + Scaffold Node

### 🎯 Goal

Implement a simple but structured ONEXRuntime class capable of loading and executing `.onex` nodes, and create the first node that builds a new node.

> ⚙️ **Primary Functional Output**: This milestone proves the system can build itself. The scaffold node must generate a valid `.onex` node using M1 protocols.

### 📦 Deliverables

* `ONEXRuntime`: executes Python and CLI-based `.onex` nodes
* Runtime result schema: defines success, error, trace log, and state
* State contract validation logic
* Execution contract loader (reads `.onex`, dispatches by type)
* Node scaffold generator: builds valid `.onex` + placeholder files using defined scaffold templates
* Template definitions: format and location for templates used by scaffold node
* Sample "scaffold node" that outputs new ONEX node metadata
* CI test harness: executes all active nodes + compares expected output

### 🧠 Design Considerations

* Future extensibility: design runtime as service/shim for M3
* Node execution types: `python`, `cli`, `noop`, future `docker`
* Output: must emit `execution_result` block with trace + trust stub fields
* State propagation: input/output schema defined + validated
* Runtime safety: sandbox or temp dir use for I/O

### ✅ Completion Criteria

* ONEXRuntime loads and executes `.onex` nodes (Python/CLI)
* Output is stored in structured result block
* Scaffold node generates new `.onex` metadata and associated files
* State contract is validated before and after node execution
* CI runs include full execution test suite

### ⚠️ Risks & Mitigations

* **Risk**: Runtime too tightly coupled to Python
  **Mitigation**: Abstract execution shim layer, plan for microservice handoff
* **Risk**: State serialization fails across boundaries
  **Mitigation**: Enforce Pydantic/JSONSchema format, define fallback/defaults

### 📊 Metrics

* 100% of `active` nodes execute without error in CI
* Scaffold node produces at least 1 valid `.onex` node per run
* All result objects pass trace and error contract validation

### 🧑‍💻 Ownership

* Milestone Owner: Jonah Gray
* Reviewer: Gemini / Cursor agent

### 🔗 References

* [docs/runtime/ONEXRuntime.md](../docs/runtime/ONEXRuntime.md)
* [docs/standards/state\_contract.md](../docs/standards/state_contract.md)
* [docs/validation/runtime\_tests.md](../docs/validation/runtime_tests.md)

---

## 🔹 Milestone 3: Event Bus Integration + Trigger Graphs

### 🎯 Goal

Enable ONEX nodes to be executed based on message triggers or input queues, and propagate results via an event bus.

### 📦 Deliverables

* `BusTrigger`: schema for messages that can invoke ONEX nodes
* MessageBusConnector: interface layer for Redis/JetStream
* Node type: `trigger` — listens and dispatches via ONEXRuntime
* CI: Test suite for event-driven execution
* Logs: Stream `execution_result` to result channels
* Discovery: Registry lists `triggerable` and `active` node sets

### 🧠 Design Considerations

* Topic format: `node.exec.request.<group>`
* Input/output message schema versioning
* Trigger chaining: use `on_success`, `on_failure`, etc.
* Filtering: node can self-select based on tags or trust
* Agent compatibility: LLM agents send `BusTrigger` messages

### ✅ Completion Criteria

* Trigger node executes valid `.onex` on message receipt
* Result posted to `node.exec.result.<group>` with trace and status
* CI test: publish → execute → validate output

### ⚠️ Risks & Mitigations

* **Risk**: Bus integration complexity delays execution loop
  **Mitigation**: Stub Redis first, add JetStream adapter later
* **Risk**: Message loss or duplication
  **Mitigation**: Use `idempotent_key` in trigger messages

### 📊 Metrics

* Trigger node responds within 1s to test message in CI
* 100% of triggered executions produce valid result logs

### 🧑‍💻 Ownership

* Milestone Owner: Jonah Gray
* Reviewer: Gemini / Messaging Agent

### 🔗 References

* [docs/messaging/bus\_protocol.md](../docs/messaging/bus_protocol.md)

---

## 🔹 Milestone 4: Autonomous Planning + Trust-Based Execution

### 🎯 Goal

Introduce autonomous node planning, scheduling, and trust-scored execution results for reproducibility and coordination.

### 📦 Deliverables

* Trust score contract in `.onex` metadata and result logs
* Node memory: log of previous executions and trace reports
* Agent planner: basic planner that selects + schedules nodes
* Scorecard validator: evaluates trust score consistency
* Trust thresholds: filter or reject low-confidence nodes

### 🧠 Design Considerations

* Success/failure definitions by node type
* Contextual scoring: include I/O size, latency, rate limits
* LLM agent simulation (stubbed): provide prompt interface
* Memory per node (stored in `.onex`, updated on success)

### ✅ Completion Criteria

* Nodes store trust score history on each execution
* Planner generates and dispatches node sequences
* CI includes trust and replay consistency checks

### ⚠️ Risks & Mitigations

* **Risk**: Overfitting trust to single execution result
  **Mitigation**: Use rolling average + decay + min sample count
* **Risk**: Planner over-generates sequences
  **Mitigation**: Add cycle detection and max depth guard

### 📊 Metrics

* 100% of nodes with history generate trust scores
* All planned sequences are valid and terminate in CI test

### 🧑‍💻 Ownership

* Milestone Owner: Jonah Gray
* Reviewer: Agent Framework Team

### 🔗 References

* [docs/agents/planner\_protocol.md](../docs/agents/planner_protocol.md)

---

## 🚦 Status

* ✅ M1: Protocol, schema, validator, and metadata format finalized
* 🛠️ M2: Runtime execution, state validation, and scaffold node in progress
* ⏳ M3: Event bus trigger design stubbed
* 🌱 M4: Trust score model and planning architecture outlined

---

## 🧭 Strategic Notes

* Schema and runtime design must allow recursion (scaffolded node is real)
* Execution state must be serializable, typed, and validatable across runs
* CI is a first-class enforcement tool — no node or result is valid unless tested
* Runtime must be extendable: today's CLI/Python → tomorrow's WASM/microservices
* Trust and scoring are future core, but instrumentation starts at M1/M2

---

## 📚 Guiding Principles

* **Schema-First**: Metadata contracts define all behavior.
* **CI is Law**: No node passes without schema and lifecycle validation.
* **Fail Fast**: Every milestone must surface errors early and visibly.
* **Recursive by Design**: Nodes generate other nodes using ONEX protocol.
* **No Manual Discovery**: All nodes must be discoverable via `.tree`.
* **Extensibility Without Breakage**: Schemas and protocols must support forward-compatible evolution.
* **Testable at Every Stage**: Each milestone has testable outputs and CI coverage.

---

## 📌 Appendix: Canonical File Definitions

### `.onex` — ONEX Metadata Block

* Required for every node
* Contains: metadata version, lifecycle, execution contract, state contract, trust stub

### `.tree` — Directory Discovery Index

* Required at repo root and per container/module
* Maps folder structure to `.onex` metadata files for discovery
* Contains no metadata itself — serves as index to `.onex` files

### `execution_result.json` — Output Contract

* Captured per execution by runtime or bus listener
* Contains: input state, output state, trace, error, trust fields

---

This roadmap defines a minimal but expressive architecture for self-describing, testable, and autonomous ONEX nodes. Each milestone is self-reinforcing and accelerates the next.

**The MVP is achieved when ONEX can build ONEX.**
