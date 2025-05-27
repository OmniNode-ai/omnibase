# ONEX Node Architecture: State Reducers and Streams

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define the model for node typing (pure/impure) and structured internal state management via reducers  
> **Audience:** Node authors, runtime developers  
> **Series:** Node Architecture  

---

## Overview

This document defines the foundational thinking behind how ONEX handles internal state changes, inspired by Redux, functional architecture patterns, and distributed event-driven systems. It clarifies the distinction between pure and impure node behavior and establishes the reducer-based internal state management model.

---

## The ONEX Node as a Function: Pure vs Impure

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

## Reducer-Based Internal State

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

### Example Reducer Configuration

```yaml
# Addition to node.onex.yaml schema for advanced nodes
reducer: "src/omnibase/reducers/retry_step_reducer.py" # Path to the reducer implementation file
```

---

## Internal vs External State

- **External State**: Defined via the `state_contract` field in `.onex`, validated against its schema, passed *between* nodes (like function arguments/return values). This is the node's public, shareable data interface.
- **Internal State**: Managed via the node's embedded `reducer`, scoped *to a single node's runtime instance*, not typically validated against a public schema unless explicitly declared (e.g., via a `reducer_contract`). This is the node's private, mutable state.

This distinction supports **encapsulation** and **composability**—external consumers interact only with the node's declared external state interface, abstracting away internal state complexities.

---

## Trust and Reducer Cohesion

Because reducers define dynamic, potentially stateful behavior within a node, they are integrated into the trust and validation model:

- The `reducer` field in `.onex` references the implementation file path
- Reducer implementation files are subject to validation (e.g., linting, protocol compliance checks)
- Reducers may optionally declare a versioned schema for their *internal* state (`reducer_contract`) to aid testing, introspection, and ensure state shape consistency across dispatches
- Nodes may declare a `reducer_snapshot` policy in `.onex` to specify if and how their reducer state should be periodically saved. This enables resumability without requiring full replay of previous actions and improves planner efficiency

---

## State Reducers and Streams Architecture

### Core Concepts

#### Reducers as Local State Transformers

* Each subsystem (e.g. metadata, config, prompt, cache) has its own **local reducer**
* Reducers receive actions and update their local state
* Reducers can emit signals (like Redux middleware) to trigger tooling, validation, or external actions

#### Global Reducer Subscription Pattern

* Global reducers can subscribe to the output of local reducers
* This supports derived state calculations, aggregated status, or cross-subsystem effects

#### Asynchronous Gate Control

* Because many operations are async, reducers may wait for conditions before propagating state
* Example: a node dispatch action may require `global_state.ready == true` before continuing

#### Event-Driven Flow

* Actions are not always direct calls; they are state changes
* Middleware or tooling reacts to these transitions (e.g. auto-lint on `file.updated`, or run validator on `metadata.changed`)

---

## Streaming and Signals

### Signals as Core Event Primitive

```yaml
type: signal.state.transition
from: idle
to: active
source: node.orchestrator
```

Signals can be emitted by:
* Reducers
* Incoming message bus packets (e.g. from JetStream)
* External tools or agents

Signals can be observed by:
* Other reducers
* Nodes
* Agents
* Composite workflows
* Triggered dispatches (e.g. schedule a validator after metadata updates)

Signals carry session, trust, and context metadata.

---

## Architecture Design Patterns

### Composable Sub-Reducers

* Systems like `metadata` or `tree` may use reducers-per-subpath
* Each reducer only cares about its own scope and emits state snapshots

### Modular Black Box Nodes

Each node is treated as a black box with:
* Inputs
* Outputs
* Metadata
* Internal reducer state (optional)

### Deterministic Execution

* Given the same reducer + input action, the output must be deterministic
* This enables caching, reproducibility, and testing
* Nodes using reducers may optionally persist reducer snapshots to cold storage. This allows the system to restore state without replaying the entire action history, improving performance for long-running or restartable sessions

---

## Reducer Implementation Examples

### Simple State Reducer

```python
from typing import Dict, Any
from omnibase.protocol.protocol_reducer import ReducerProtocol

class CounterReducer(ReducerProtocol):
    """Simple counter reducer for demonstration."""
    
    def initial_state(self) -> Dict[str, Any]:
        return {"count": 0, "last_action": None}
    
    def dispatch(self, state: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
        action_type = action.get("type")
        
        if action_type == "INCREMENT":
            return {
                "count": state["count"] + 1,
                "last_action": action_type
            }
        elif action_type == "DECREMENT":
            return {
                "count": state["count"] - 1,
                "last_action": action_type
            }
        elif action_type == "RESET":
            return self.initial_state()
        
        return state
```

### Retry Logic Reducer

```python
from typing import Dict, Any
from datetime import datetime
from omnibase.protocol.protocol_reducer import ReducerProtocol

class RetryReducer(ReducerProtocol):
    """Reducer for managing retry logic and backoff."""
    
    def initial_state(self) -> Dict[str, Any]:
        return {
            "attempts": 0,
            "max_attempts": 3,
            "last_attempt": None,
            "backoff_seconds": 1,
            "status": "ready"
        }
    
    def dispatch(self, state: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
        action_type = action.get("type")
        
        if action_type == "ATTEMPT":
            return {
                **state,
                "attempts": state["attempts"] + 1,
                "last_attempt": datetime.now().isoformat(),
                "status": "attempting"
            }
        elif action_type == "SUCCESS":
            return {
                **state,
                "status": "success"
            }
        elif action_type == "FAILURE":
            if state["attempts"] >= state["max_attempts"]:
                return {
                    **state,
                    "status": "failed",
                    "backoff_seconds": min(state["backoff_seconds"] * 2, 60)
                }
            else:
                return {
                    **state,
                    "status": "retrying",
                    "backoff_seconds": min(state["backoff_seconds"] * 2, 60)
                }
        
        return state
```

---

## Signal Emission and Handling

### Signal Structure

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class Signal:
    """Structured signal for state transitions."""
    type: str
    source: str
    payload: Dict[str, Any]
    timestamp: datetime
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    trust_score: Optional[float] = None
```

### Signal Emission Example

```python
def emit_state_transition_signal(
    reducer_name: str,
    old_state: Dict[str, Any],
    new_state: Dict[str, Any],
    action: Dict[str, Any]
) -> Signal:
    """Emit a signal when reducer state changes."""
    return Signal(
        type="state.transition",
        source=f"reducer.{reducer_name}",
        payload={
            "old_state": old_state,
            "new_state": new_state,
            "action": action,
            "state_delta": compute_state_delta(old_state, new_state)
        },
        timestamp=datetime.now()
    )
```

---

## Testing Reducers

### Reducer Testing Patterns

```python
import pytest
from typing import Dict, Any

def test_reducer_deterministic(reducer_class):
    """Test that reducer produces deterministic results."""
    reducer = reducer_class()
    initial_state = reducer.initial_state()
    
    action = {"type": "TEST_ACTION", "payload": {"value": 42}}
    
    # Multiple calls should produce identical results
    result1 = reducer.dispatch(initial_state, action)
    result2 = reducer.dispatch(initial_state, action)
    
    assert result1 == result2

def test_reducer_state_immutability(reducer_class):
    """Test that reducer doesn't mutate input state."""
    reducer = reducer_class()
    initial_state = reducer.initial_state()
    original_state = initial_state.copy()
    
    action = {"type": "TEST_ACTION"}
    reducer.dispatch(initial_state, action)
    
    # Original state should be unchanged
    assert initial_state == original_state

def test_reducer_protocol_compliance(reducer_class):
    """Test that reducer implements required protocol methods."""
    reducer = reducer_class()
    
    # Test initial_state method
    initial = reducer.initial_state()
    assert isinstance(initial, dict)
    
    # Test dispatch method
    action = {"type": "NOOP"}
    result = reducer.dispatch(initial, action)
    assert isinstance(result, dict)
```

---

## Benefits

* Clean separation of state vs effect
* Tools can plug into reducer output instead of monkeypatching logic
* Easier to test reducers in isolation
* Foundation for trust-aware state propagation and replay
* Deterministic execution enables caching and reproducibility
* Event-driven architecture supports reactive programming patterns
* Modular design allows for composable state management

---

## Best Practices

### Reducer Design

1. **Keep reducers pure**: No side effects in reducer functions
2. **Immutable state updates**: Always return new state objects
3. **Action-driven**: All state changes should be triggered by actions
4. **Deterministic**: Same input should always produce same output
5. **Testable**: Design reducers to be easily unit tested

### State Management

1. **Minimize state**: Only store what's necessary for the node's operation
2. **Clear contracts**: Define clear interfaces for state shape
3. **Validation**: Validate state transitions where appropriate
4. **Snapshotting**: Consider snapshot strategies for long-running processes
5. **Recovery**: Design for state recovery and error handling

### Signal Handling

1. **Structured signals**: Use consistent signal formats
2. **Correlation**: Include correlation IDs for tracing
3. **Metadata**: Attach relevant context and trust information
4. **Async handling**: Design for asynchronous signal processing
5. **Error propagation**: Handle signal processing errors gracefully

---

## References

- [Node Architecture Index](./index.md) - Overview of node architecture series
- [Node Contracts](./node_contracts.md) - Contract-first node design
- [Protocol Definitions](./protocol_definitions.md) - Core protocol interfaces
- [Functional Monadic Node Architecture](./functional_monadic_node_architecture.md) - Monadic composition patterns
- [Node Typology](./node_typology.md) - Node categorization and execution model
- [Sessions and Streaming](./sessions_and_streaming.md) - Session lifecycle and streaming architecture

---

**Note:** This document defines the canonical foundational architecture for state and reducer management in ONEX. It forms the basis for the node execution planner and session layer, providing a robust foundation for stateful node operations and event-driven execution patterns. 