<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: node_typology.md
version: 1.0.0
uuid: 0cbccc21-45ae-431f-8a1c-dab8befecc0b
author: OmniNode Team
created_at: 2025-05-27T08:06:48.856652
last_modified_at: 2025-05-27T17:26:51.911448
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 88d82f2e957a2f1912d2c10ad1cc22062e8f9e46f1949f88f77154a8ab3bf426
entrypoint: python@node_typology.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.node_typology
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# ONEX Node Architecture: Node Typology and Execution Model

> **Status:** Canonical  
> **Last Updated:** 2025-01-27  
> **Purpose:** Define a tiered model for ONEX nodes to clarify execution semantics, state handling, side effect classification, and planning implications  
> **Audience:** Node authors, system architects, runtime developers  
> **Series:** Node Architecture  

---

## Overview

ONEX nodes are the core building blocks of the system. Each node is defined via metadata (`.onex`), a declared interface (`state_contract`), and an optional internal state handler (`reducer`). To support composability, testability, and execution planning, ONEX nodes are categorized into three functional tiers that clarify execution semantics, state handling, and side effect classification.

---

## Tier 1: Pure Functional Nodes (Stateless)

**Definition:** Deterministic transformations that accept external state and return modified state. No side effects, no internal state.

### Characteristics

* **Meta Type:** `tool` or `utility`
* **Reducer:** None
* **State:** Uses only `state_contract`
* **Execution:** One-shot, stateless, side-effect free
* **Deterministic:** Same input always produces same output
* **Composable:** Can be safely chained and parallelized

### Examples

* Math functions (e.g., `add`, `scale`, `clamp`)
* Format converters (e.g., `dict_to_yaml`)
* Content transformers (e.g., `normalize_text`, `strip_html_tags`)
* Embedding or summarization wrappers
* Schema validators
* Data parsers and formatters

### Output State Pattern

```json
{
  "status": "success",
  "result": "...",
  "metadata": {
    "execution_time_ms": 42,
    "input_hash": "abc123"
  }
}
```

### Implementation Example

```python
def run_text_normalizer(input_state: TextNormalizerInput) -> TextNormalizerOutput:
    """Pure functional node for text normalization."""
    normalized_text = input_state.text.strip().lower()
    
    return TextNormalizerOutput(
        status="success",
        result=normalized_text,
        metadata={
            "original_length": len(input_state.text),
            "normalized_length": len(normalized_text)
        }
    )
```

> **Enhanced Classification:** The [Monadic Node Core](./architecture-node-monadic-core.md) provides an enhanced categorization based on functional purity with specific monadic types (Pure Nodes, Impure Nodes, Plugin Nodes, and Ephemeral Nodes). This approach further refines the classification with stronger guarantees for composition via the `bind()` method and a structured `NodeResult` return type.

---

## Tier 2: Reducer Nodes (Encapsulated State Logic)

**Definition:** Deterministic nodes that include an internal state machine. They support progressive state transitions across invocations while maintaining deterministic behavior.

### Characteristics

* **Meta Type:** Often `tool` or `agent`
* **Reducer:** Implements `ReducerProtocol`
* **State:** Internal (via reducer) + External (via `state_contract`)
* **Execution:** Deterministic but state-aware
* **Resumable:** Can snapshot and restore internal state
* **Testable:** Reducer logic can be tested in isolation

### Use Cases

* Retry with exponential backoff
* Branching logic within a tool
* Memory for session-local data
* Stateful validators or classifiers
* Multi-step workflows
* Conversation state management
* Progress tracking for long-running operations

### Metadata Example

```yaml
# node.onex.yaml
reducer: src/omnibase/reducers/retry_tracker.py
cache:
  enabled: true
  strategy: memoize
  scope: reducer_state
```

### ReducerProtocol Implementation

```python
from typing import Dict, Any
from omnibase.protocol.protocol_reducer import ReducerProtocol

class RetryTrackerReducer(ReducerProtocol):
    """Reducer for tracking retry attempts with backoff."""
    
    def initial_state(self) -> Dict[str, Any]:
        return {
            "attempts": 0,
            "max_attempts": 3,
            "backoff_seconds": 1,
            "status": "ready",
            "last_error": None
        }
    
    def dispatch(self, state: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
        action_type = action.get("type")
        
        if action_type == "ATTEMPT":
            return {
                **state,
                "attempts": state["attempts"] + 1,
                "status": "attempting"
            }
        elif action_type == "SUCCESS":
            return {
                **state,
                "status": "success"
            }
        elif action_type == "FAILURE":
            new_backoff = min(state["backoff_seconds"] * 2, 60)
            if state["attempts"] >= state["max_attempts"]:
                return {
                    **state,
                    "status": "failed",
                    "last_error": action.get("error"),
                    "backoff_seconds": new_backoff
                }
            else:
                return {
                    **state,
                    "status": "retrying",
                    "last_error": action.get("error"),
                    "backoff_seconds": new_backoff
                }
        
        return state
```

---

## Tier 3: Impure or Middleware Nodes

**Definition:** Nodes that perform side effects—network calls, file writes, logging, database mutations. May include reducers for state management.

### Characteristics

* **Meta Type:** `agent`, `plugin`, `utility`
* **Reducer:** Optional
* **State:** Optional internal state + external context
* **Execution:** Impure (side effects allowed and expected)
* **Auditable:** Must track provenance and impact
* **Constrained:** May require special execution policies

### Examples

* Remote API callers
* File system operations
* Database interactions
* Loggers and monitoring tools
* External service wrappers
* Streaming output handlers
* Email or notification senders
* Cache management operations

### Identification and Metadata

```yaml
# node.onex.yaml
meta_type: agent
impure: true
side_effects:
  - "network_io"
  - "file_system"
  - "logging"
environment:
  - name: "API_KEY"
    required: true
  - name: "TIMEOUT_SECONDS"
    default: "30"
```

### Implementation Example

```python
import requests
from typing import Optional
from omnibase.protocol.protocol_event_bus import ProtocolEventBus

def run_api_caller(
    input_state: ApiCallerInput,
    event_bus: Optional[ProtocolEventBus] = None
) -> ApiCallerOutput:
    """Impure node that makes external API calls."""
    
    # Emit start event
    if event_bus:
        event_bus.emit("api_call.start", {
            "url": input_state.url,
            "method": input_state.method
        })
    
    try:
        response = requests.request(
            method=input_state.method,
            url=input_state.url,
            json=input_state.payload,
            timeout=input_state.timeout_seconds
        )
        
        result = ApiCallerOutput(
            status="success",
            response_data=response.json(),
            status_code=response.status_code,
            metadata={
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "content_length": len(response.content)
            }
        )
        
        # Emit success event
        if event_bus:
            event_bus.emit("api_call.success", {
                "status_code": response.status_code,
                "response_time_ms": result.metadata["response_time_ms"]
            })
        
        return result
        
    except Exception as e:
        # Emit error event
        if event_bus:
            event_bus.emit("api_call.error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
        
        return ApiCallerOutput(
            status="error",
            error_message=str(e),
            metadata={"error_type": type(e).__name__}
        )
```

---

## Composition & Orchestration

ONEX allows recursive and declarative orchestration across all node tiers:

### Dependency Declaration

Dependencies are declared in metadata using standardized URI format:

```yaml
dependencies:
  - tool://text.normalizer@>=1.0.0
  - agent://api.caller@^2.1.0
base_class:
  - validator://core.base@1.0.0
protocols_supported:
  - protocol://retry.backoff@1.0.0
```

### Execution Model

All nodes, regardless of tier, present a consistent interface:

```python
(input_state: dict) -> (output_state: dict)
```

### Orchestration Considerations

* **Tier 1 nodes**: Can be safely parallelized and cached
* **Tier 2 nodes**: Require state management and may need serialization
* **Tier 3 nodes**: May require planning constraints (ordering, mutex, resource limits)

---

## Implications for Validation and Execution

### Validation Requirements

| Tier | Validation Requirements |
|------|------------------------|
| **Tier 1** | Strict schema validation, deterministic testing |
| **Tier 2** | Schema + reducer test coverage, state transition validation |
| **Tier 3** | Additional sandboxing, policy checks, side effect auditing |

### Trust and Audit

* All nodes may define `trust_score_stub` for execution history tracking
* Impure nodes must track provenance and impact metadata
* Reducer nodes should implement snapshot strategies for resumability
* Side effects must be declared and auditable

### Execution Planning

The execution planner uses tier information to optimize execution:

* **Pure nodes**: Can be cached, parallelized, and reordered freely
* **Reducer nodes**: Require state management and may benefit from snapshotting
* **Impure nodes**: May be deferred, require resource constraints, or need special ordering

#### Advanced Planning Features

* Nodes with declared `execution_profile` and `model_profiles` enable cost-aware dispatch
* Composite nodes using `memoization_tier: deep` benefit from subgraph-level caching
* `trace_hash` structures enable reusable execution paths
* Reducer nodes may declare snapshot strategies to reduce replay overhead

---

## Node Classification Examples

### Classification Decision Tree

```
Is the node deterministic?
├─ Yes: Does it maintain internal state?
│  ├─ Yes: **Tier 2** (Reducer Node)
│  └─ No: Does it have side effects?
│     ├─ Yes: **Tier 3** (Impure Node)
│     └─ No: **Tier 1** (Pure Functional Node)
└─ No: **Tier 3** (Impure Node)
```

### Real-World Examples

```yaml
# Tier 1: Pure Functional
text_normalizer:
  meta_type: tool
  deterministic: true
  side_effects: []

# Tier 2: Reducer Node  
retry_handler:
  meta_type: tool
  reducer: src/reducers/retry_logic.py
  deterministic: true
  side_effects: []

# Tier 3: Impure Node
api_client:
  meta_type: agent
  impure: true
  side_effects: ["network_io", "logging"]
  deterministic: false
```

---

## Testing Strategies by Tier

### Tier 1: Pure Functional Testing

```python
def test_pure_node_deterministic():
    """Test that pure nodes are deterministic."""
    input_state = {"text": "Hello World"}
    
    result1 = run_text_normalizer(input_state)
    result2 = run_text_normalizer(input_state)
    
    assert result1 == result2

def test_pure_node_no_side_effects():
    """Test that pure nodes have no side effects."""
    original_state = {"text": "Hello World"}
    input_state = original_state.copy()
    
    run_text_normalizer(input_state)
    
    # Input should be unchanged
    assert input_state == original_state
```

### Tier 2: Reducer Node Testing

```python
def test_reducer_state_transitions():
    """Test reducer state transitions."""
    reducer = RetryTrackerReducer()
    state = reducer.initial_state()
    
    # Test attempt action
    state = reducer.dispatch(state, {"type": "ATTEMPT"})
    assert state["attempts"] == 1
    assert state["status"] == "attempting"
    
    # Test failure action
    state = reducer.dispatch(state, {"type": "FAILURE", "error": "timeout"})
    assert state["status"] == "retrying"
    assert state["last_error"] == "timeout"
```

### Tier 3: Impure Node Testing

```python
def test_impure_node_with_mocks():
    """Test impure nodes using mocks."""
    with patch('requests.request') as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        input_state = ApiCallerInput(
            url="https://api.example.com/test",
            method="GET"
        )
        
        result = run_api_caller(input_state)
        assert result.status == "success"
        assert result.response_data == {"result": "success"}
```

---

## Summary Table

| Tier | Type                | State    | Side Effects | Reducer  | Meta Type(s)           | Execution Characteristics |
| ---- | ------------------- | -------- | ------------ | -------- | ---------------------- | ------------------------ |
| 1    | Pure function       | None     | No           | No       | tool, utility          | Cacheable, parallelizable |
| 2    | Stateful (reducer)  | Local    | No           | Yes      | tool, agent            | State-aware, resumable   |
| 3    | Middleware / Impure | Optional | Yes          | Optional | utility, agent, plugin | Constrained, auditable   |

---

## References

- [Node Architecture Index](./index.md) - Overview of node architecture series
- [State Reducers](./state_reducers.md) - State management and reducer patterns
- [Node Contracts](./node_contracts.md) - Contract-first node design
- [Protocol Definitions](./protocol_definitions.md) - Core protocol interfaces
- [Monadic Node Core](../architecture-node-monadic-core.md) - Core monadic principles and interfaces
- [Node Composition](../architecture-node-composition.md) - Composition patterns and execution models
- [Structural Conventions](./structural_conventions.md) - Directory structure and file layout

---

**Note:** This document supports clear node authoring, classification, and execution strategy alignment. It should be referenced when designing node metadata and runtime behavior to ensure proper categorization and optimal execution planning.
