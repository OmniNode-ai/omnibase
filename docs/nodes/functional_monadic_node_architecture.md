<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: functional_monadic_node_architecture.md
version: 1.0.0
uuid: c1b59d10-6406-4630-ac65-2d3864c2cd16
author: OmniNode Team
created_at: '2025-05-28T12:40:26.635827'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://functional_monadic_node_architecture
namespace: markdown://functional_monadic_node_architecture
meta_type: tool

<!-- === /OmniNode:Metadata === -->
# Functional Monadic Node Architecture for ONEX

> **Status:** Canonical Draft  
> **Part of:** [Node Architecture Series](./index.md)  
> **Audience:** Maintainers, contributors, node developers  
> **Related documents:** [Node Contracts](./node_contracts.md), [State Reducers](./state_reducers.md), [Node Typology](./node_typology.md)

## Overview

ONEX nodes will follow a monadic, functionally composable architecture with explicit state modeling, context propagation, and effect tracking. This pattern enables clean node composition, structured execution, introspection, agent simulation, and full replayability.

This document defines the canonical model for functional composition of nodes, extending the existing [Node as a Function](./index.md#-the-onex-node-as-a-function-conceptual-model) conceptual model with monadic principles.

## Core Design Principles

### Node as a Computation Unit

Each node is a computation from `input -> output` that returns a `NodeResult`, encapsulating:

* Output value
* Execution context (provenance, logs, trust, timestamp)
* Optional side effect metadata
* Optional state diffs

### Minimal Interface

```python
class NodeResult(Generic[T]):
    value: T
    context: ExecutionContext
    state_delta: Optional[Dict] = None
    events: Optional[List[Event]] = None

    async def bind(self, f: Callable[[T], Awaitable['NodeResult[U]']]) -> 'NodeResult[U]':
        return await f(self.value)

class Node(Generic[T, U]):
    async def run(self, input: T) -> NodeResult[U]:
        ...
```

### ExecutionContext Structure (Example)

```python
class ExecutionContext:
    provenance: List[str]             # trace of node invocations
    logs: List[LogEntry]             # structured logs per step
    trust_score: float               # numeric or enum-based trust level
    timestamp: datetime              # execution timestamp
    metadata: Dict[str, Any]         # additional ad hoc data
```

### Event Structure (Example)

```python
class Event:
    type: str                        # e.g., "log", "metric", "alert"
    payload: Dict[str, Any]          # structured content
    timestamp: datetime
```

### State Delta Format

State deltas should follow a simple, structured contract:

* JSON Patch-style object diffs (RFC 6902)
* OR key-value overwrite map (e.g., `{"users[123].status": "active"}`)
* Must be serializable and composable

### Types of Nodes

* **Pure Nodes:** Deterministic, no side effects. Equivalent to `Identity` monad.
* **Impure Nodes:** May access internal state, external services, or include cost/model calls.
* **Plugin Nodes:** Emit side effects only (e.g. logging, telemetry). Equivalent to `Writer` monad.
* **Ephemeral Nodes:** Model calls or non-deterministic functions. Return values are captured and replayed for simulation.

## Monadic Composition

Nodes are composed via `bind()`:

```python
result = await nodeA.run(input)
result = await result.bind(nodeB.run)
result = await result.bind(log_node.run)
```

Composability enables:

* Safe chaining
* Context propagation
* Intermediate result reuse
* Modular tool creation

## Redux-Style State Modeling

Each node produces:

* State delta
* Optional emitted events

A central reducer interprets state transitions:

```python
def reducer(state, action):
    # deterministic update
```

State history can be snapshotted, diffed, or replayed. Agents can simulate or inspect consequences before committing.
Reducers should be modular, composable, and structured hierarchically for scale.

## Asynchronous Support

All `.run()` and `.bind()` calls are `async`, supporting:

* Concurrent execution
* Event-driven nodes
* Streaming/long-running workflows
* Interruptible/resumable stateful computation

## Side Effect Modeling

Effects are made explicit:

* Logged in context
* Included in `NodeResult`
* Simulated or stubbed in replay mode

Ephemeral effects (e.g. model outputs) are captured and stored for deterministic replays.

## Agent-Native Benefits

* Nodes are fully introspectable
* Metadata includes input/output types, side effects, trust levels
* Tools are just composed node chains
* Agents can simulate, plan, and compose workflows declaratively

## Potential Challenges / Considerations

### Learning Curve

Monadic patterns, functional programming, and Redux-style state management can introduce complexity for developers unfamiliar with these paradigms. Training and well-structured documentation will be critical.

### Overhead / Boilerplate

While the overhead is minimal compared to ONEX's existing execution context, wrapping all nodes with `NodeResult`, `ExecutionContext`, and optional `state_delta`/`events` could lead to repetitive boilerplate for simple nodes. This can be mitigated with tooling, decorators, and node scaffolding utilities.

### Reducer Complexity

As the state model grows, a single global reducer can become a performance or maintainability bottleneck. Strategies such as modular, combinable reducers (similar to Redux's `combineReducers`) should be adopted early.

### Serialization Requirements

To support replay and audit, `NodeResult` and its subcomponents (especially context, state_delta, and events) must be serializable (e.g., to JSON or msgpack). This constraint should be enforced via test coverage and schema validation.

### Error Handling in Monads

NodeResult should support a discriminated union:

```python
Union[Success[T], Failure[E]]
```

Key considerations:

* **Structured error types:** Use enums or a custom class hierarchy for recoverable/transient/classification of errors
* **Retry logic:** Bind should support failure-aware chaining, or delegate to an orchestrator with retry/backoff logic
* **Error context:** Include stack trace, failing input, ExecutionContext snapshot in the Failure result

#### Error Structure and Recovery Hints

To improve agent recovery and retry planning, the `Failure[E]` type should support:
- A structured error payload with:
  - `error_type`: Enum (e.g. `Transient`, `Permanent`, `Validation`)
  - `message`: Human-readable string
  - `code`: Numeric or symbolic code
  - `trace`: Optional stack trace or traceback
  - `context`: Snapshot of input or partial ExecutionContext
- Optional retry metadata:
  - `retryable: bool`
  - `backoff_strategy: Optional[Literal['exponential', 'linear']]`
  - `max_attempts: Optional[int]`

### Trust Level Propagation

Trust metadata must be propagated and possibly modified across node chains. Define clear rules:

* Is trust inherited (`min(trustA, trustB)`)?
* Can downstream nodes elevate trust if validation passes?
* Should nodes annotate trust explicitly?

This should be formalized in the `ExecutionContext` structure.

### State Performance Considerations

Large state diffs may degrade reducer performance. Solutions:

* Use immutable data structures
* Structure sharing / diffable trees
* Batched reducer updates

### Orchestration & Workflow Management

* **Graph Definition:** Consider supporting both imperative chaining and declarative DSL (e.g., YAML, config-based graphs)
* **Fan-out / Fan-in:** Use helper combinators like `NodeResult.all()` or `gather()` for concurrent node runs
* **Persistence:** Long-running workflows may require persisting partial execution state
* **Conditional Logic:** Introduce branching nodes or conditional bind mechanisms for monadic `if/else`
* **Combinators:** Provide reusable functional combinators like:
  - `gather([NodeA, NodeB])`: Runs nodes concurrently, returns list of results
  - `branch(condition_fn, then_node, else_node)`: Executes one of two nodes based on condition
  - `sequence([Node1, Node2, ...])`: Chains nodes in order via `.bind()`

### Observability & Monitoring

* **Distributed Tracing:** Integrate ExecutionContext with OpenTelemetry or Zipkin
* **Metrics:** Capture per-node latency, input/output sizes, failure rates
* **Alerting:** Emit special events (e.g., `alert`) from Failure or threshold violations
* **Event Versioning:** As event types grow, consider including `version: str` field in the event schema and maintaining a schema registry for cross-system compatibility.

### Security Considerations

* **Access Control:** Nodes may need scoped permissions to access external services
* **Validation:** Input validation should be handled explicitly or via input schemas
* **Secrets Management:** Sensitive config should be injected securely and scoped per node/container

### Deployment and Operationalization

* **Node Discovery:** Central registry of node signatures (inputs, outputs, effects)
* **Versioning:** Track and resolve node schema versions via ExecutionContext
* **Resource Management:** Nodes can declare CPU/GPU/memory needs in metadata

### Human-in-the-Loop Support

Support interruptible or pauseable nodes:

* Nodes may emit `pause` events
* External agents (e.g., humans) may resume with decision input
* Useful for approval, disambiguation, escalation workflows

## Practical Example (Pseudocode)

```python
class ParseInput(Node[str, Dict]):
    async def run(self, input: str) -> NodeResult[Dict]:
        parsed = json.loads(input)
        return NodeResult(parsed, context=..., state_delta=None, events=[])

class ProcessData(Node[Dict, Dict]):
    async def run(self, input: Dict) -> NodeResult[Dict]:
        result = {...}  # some computation
        return NodeResult(result, context=..., state_delta={"results": result}, events=[])

class StoreResult(Node[Dict, bool]):
    async def run(self, input: Dict) -> NodeResult[bool]:
        db.write(input)
        return NodeResult(True, context=..., state_delta=None, events=[{"type": "db_write", "payload": input}])

# Pipeline
result = await ParseInput().run(raw_input)
result = await result.bind(ProcessData().run)
result = await result.bind(StoreResult().run)
```

## Relationship to Existing Node Architecture

This functional monadic architecture builds upon several existing architectural concepts in the Node Architecture Series:

- Extends the ["Node as a Function"](./index.md#-the-onex-node-as-a-function-conceptual-model) model with explicit monadic composition
- Formalizes [State Reducers](./state_reducers.md) approach with explicit state deltas
- Aligns with [Node Typology](./node_typology.md) but explicitly categorizes nodes based on their functional purity
- Enhances [Node Contracts](./node_contracts.md) with a more structured, monad-based result type
- Complements [Protocol Definitions](./protocol_definitions.md) with specific interfaces for monadic composition

## Implementation Timeline

This architecture will be implemented in phases:

1. **M2 (Q3 2025)**: Define NodeResult, ExecutionContext, and monadic bind interfaces
2. **M3 (Q4 2025)**: Implement core reducers and state delta tracking 
3. **M4 (Q1 2026)**: Add full event propagation and simulation support

## Summary

This architecture fuses:

* Functional purity
* Monadic composition
* Redux-like state semantics
* Agent-native tool design

It incurs minimal overhead beyond ONEX's existing execution context, but yields strong composability, reproducibility, testability, and planning guarantees.

---

[Back to Node Architecture Series](./index.md)
